"""Small, dependency-free average-color capture for the Windows virtual desktop."""
import ctypes
from ctypes import wintypes


class _BitmapInfoHeader(ctypes.Structure):
    _fields_ = [
        ('size', wintypes.DWORD), ('width', wintypes.LONG), ('height', wintypes.LONG),
        ('planes', wintypes.WORD), ('bit_count', wintypes.WORD), ('compression', wintypes.DWORD),
        ('image_size', wintypes.DWORD), ('x_pixels', wintypes.LONG), ('y_pixels', wintypes.LONG),
        ('colors_used', wintypes.DWORD), ('colors_important', wintypes.DWORD),
    ]


class _BitmapInfo(ctypes.Structure):
    _fields_ = [('header', _BitmapInfoHeader), ('colors', wintypes.DWORD * 3)]


def capture_average_rgb():
    """Capture a downscaled sample of every monitor in the virtual desktop."""
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)
    user32.GetSystemMetrics.argtypes = [ctypes.c_int]
    user32.GetSystemMetrics.restype = ctypes.c_int
    user32.GetDC.argtypes = [wintypes.HWND]
    user32.GetDC.restype = wintypes.HDC
    user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
    user32.ReleaseDC.restype = ctypes.c_int
    gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
    gdi32.CreateCompatibleDC.restype = wintypes.HDC
    gdi32.CreateDIBSection.argtypes = [wintypes.HDC, ctypes.POINTER(_BitmapInfo), wintypes.UINT,
                                       ctypes.POINTER(ctypes.c_void_p), wintypes.HANDLE, wintypes.DWORD]
    gdi32.CreateDIBSection.restype = wintypes.HBITMAP
    gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
    gdi32.SelectObject.restype = wintypes.HGDIOBJ
    gdi32.StretchBlt.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                 wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                 wintypes.DWORD]
    gdi32.StretchBlt.restype = wintypes.BOOL
    gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
    gdi32.DeleteObject.restype = wintypes.BOOL
    gdi32.DeleteDC.argtypes = [wintypes.HDC]
    gdi32.DeleteDC.restype = wintypes.BOOL

    left, top = user32.GetSystemMetrics(76), user32.GetSystemMetrics(77)
    screen_width, screen_height = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
    if screen_width <= 0 or screen_height <= 0:
        raise OSError('Не удалось определить подключённые экраны Windows.')
    scale = min(1.0, 480 / screen_width, 270 / screen_height)
    width, height = max(1, round(screen_width * scale)), max(1, round(screen_height * scale))
    screen_dc = user32.GetDC(None)
    if not screen_dc:
        raise ctypes.WinError(ctypes.get_last_error())
    memory_dc = None
    bitmap = None
    previous = None
    try:
        memory_dc = gdi32.CreateCompatibleDC(screen_dc)
        info = _BitmapInfo()
        info.header.size = ctypes.sizeof(_BitmapInfoHeader)
        info.header.width = width
        info.header.height = -height
        info.header.planes = 1
        info.header.bit_count = 32
        info.header.compression = 0  # BI_RGB
        pixels = ctypes.c_void_p()
        bitmap = gdi32.CreateDIBSection(screen_dc, ctypes.byref(info), 0, ctypes.byref(pixels), None, 0)
        if not memory_dc or not bitmap or not pixels.value:
            raise ctypes.WinError(ctypes.get_last_error())
        previous = gdi32.SelectObject(memory_dc, bitmap)
        if not gdi32.StretchBlt(memory_dc, 0, 0, width, height, screen_dc, left, top,
                                screen_width, screen_height, 0x00CC0020):  # SRCCOPY
            raise ctypes.WinError(ctypes.get_last_error())
        raw = ctypes.string_at(pixels, width * height * 4)
        x_step, y_step = max(1, width // 48), max(1, height // 27)
        red = green = blue = count = 0
        for y in range(y_step // 2, height, y_step):
            for x in range(x_step // 2, width, x_step):
                offset = (y * width + x) * 4
                blue += raw[offset]
                green += raw[offset + 1]
                red += raw[offset + 2]
                count += 1
        return tuple(round(value / count) for value in (red, green, blue))
    finally:
        if memory_dc and previous:
            gdi32.SelectObject(memory_dc, previous)
        if bitmap:
            gdi32.DeleteObject(bitmap)
        if memory_dc:
            gdi32.DeleteDC(memory_dc)
        user32.ReleaseDC(None, screen_dc)
