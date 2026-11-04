"""Persistent asyncio BLE worker; independent connections, counters and write locks."""
import asyncio
from dataclasses import dataclass, field
import queue
import threading
from bleak import BleakClient, BleakScanner
from protocol import Protocol, SERVICE, WRITE, NOTIFY

@dataclass
class Connection:
    client: object
    characteristic: object
    name: str
    protocol: Protocol = field(default_factory=Protocol)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

class Bluetooth:
    def __init__(self):
        self.events = queue.Queue()
        self.connections = {}
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def submit(self, action, *args):
        async def work():
            try:
                result = await getattr(self, action)(*args)
                self.events.put(('done', action, result))
            except Exception as exc:
                self.events.put(('error', action, str(exc) or type(exc).__name__))
        return asyncio.run_coroutine_threadsafe(work(), self.loop)

    def snapshot(self):
        return [{'address': address, 'name': connection.name}
                for address, connection in self.connections.items()]

    def publish_connections(self):
        self.events.put(('connections', '', self.snapshot()))

    async def scan(self):
        results = await BleakScanner.discover(timeout=7, return_adv=True)
        return sorted([(d, a) for d, a in results.values()
                       if (a.local_name or d.name or '').lower().startswith(('lednet', 'zengge'))
                       or SERVICE in a.service_uuids], key=lambda pair: pair[1].rssi, reverse=True)

    async def connect(self, device):
        address = device.address
        if address in self.connections:
            return self.snapshot()
        client = BleakClient(device, disconnected_callback=lambda client: self._disconnected(address, client),
                             winrt={'use_cached_services': False})
        try:
            await asyncio.wait_for(client.connect(), 25)
            service = client.services.get_service(SERVICE)
            if service is None or service.get_characteristic(WRITE) is None:
                raise RuntimeError('Устройство не поддерживает протокол LEDnetWF (FFFF/FF01).')
            connection = Connection(client, service.get_characteristic(WRITE), device.name or address)
            notify = service.get_characteristic(NOTIFY)
            if notify is not None:
                await client.start_notify(notify, lambda _sender, _data: None)
            await self._send(connection, 'initialize')
            if not client.is_connected:
                raise RuntimeError('Устройство отключилось во время подключения.')
            self.connections[address] = connection
            self.publish_connections()
            return self.snapshot()
        except BaseException:
            await client.disconnect()
            raise

    def _disconnected(self, address, client):
        connection = self.connections.get(address)
        if connection is not None and connection.client is client:
            self.connections.pop(address)
            self.events.put(('device_error', '', f'{connection.name}: соединение потеряно.'))
            self.publish_connections()

    async def disconnect(self, addresses=None):
        selected = list(self.connections) if addresses is None else list(addresses)
        errors = []
        for address in selected:
            connection = self.connections.pop(address, None)
            if connection is not None:
                try:
                    async with connection.lock:
                        await asyncio.wait_for(connection.client.disconnect(), 8)
                except Exception as exc:
                    errors.append(f'{connection.name}: {exc}')
        self.publish_connections()
        if errors:
            raise RuntimeError('; '.join(errors))
        return self.snapshot()

    async def _send(self, connection, command, *args):
        async with connection.lock:
            if not connection.client.is_connected:
                raise RuntimeError('Соединение потеряно.')
            packet = getattr(connection.protocol, command)(*args)
            response = 'write' in connection.characteristic.properties
            await asyncio.wait_for(connection.client.write_gatt_char(connection.characteristic, packet, response=response), 4)

    async def _broadcast(self, command, *args):
        connections = list(self.connections.items())
        if not connections:
            raise RuntimeError('Нет подключённых ламп.')
        results = await asyncio.gather(*(self._send(c, command, *args) for _, c in connections), return_exceptions=True)
        successes = 0
        for (address, connection), result in zip(connections, results):
            if isinstance(result, BaseException):
                self.events.put(('device_error', '', f'{connection.name}: {result}'))
                # Drop failed writes, so a broken lamp cannot delay every later frame.
                if self.connections.get(address) is connection:
                    self.connections.pop(address)
                    try:
                        await asyncio.wait_for(connection.client.disconnect(), 2)
                    except Exception:
                        pass
            else:
                successes += 1
        if successes != len(connections):
            self.publish_connections()
        if not successes:
            raise RuntimeError('Не удалось отправить команду ни одной лампе. Подключитесь снова.')

    async def color(self, rgb):
        await self._broadcast('rgb', *rgb)

    async def power(self, enabled):
        await self._broadcast('power', enabled)

    async def music_color(self, rgb):
        await self.color(rgb)
