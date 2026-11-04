import asyncio
import unittest
from protocol import Protocol

class ProtocolTests(unittest.TestCase):
    def test_primary_colors(self):
        p = Protocol()
        for rgb, hsv in [((255,0,0), (0,100,100)), ((0,255,0), (60,100,100)), ((0,0,255), (120,100,100)), ((0,0,0), (0,0,0)), ((255,255,255), (0,0,100))]:
            packet = p.rgb(*rgb)
            self.assertEqual(tuple(packet[10:13]), hsv)
            self.assertEqual(packet[-1], sum(packet[8:-1]) & 255)
            self.assertEqual(len(packet), 21)
    def test_power_and_counter_wrap(self):
        p = Protocol()
        self.assertEqual(p.power(True)[9], 0x23)
        self.assertEqual(p.power(False)[9], 0x24)
        for _ in range(600):
            packet = p.initialize()
            self.assertEqual(packet[0], 0)
            self.assertTrue(1 <= packet[1] <= 255)
    def test_invalid_color(self):
        for value in (-1, 256, 1.5, '2'):
            with self.assertRaises(ValueError):
                Protocol().rgb(value, 0, 0)

class GuiTests(unittest.TestCase):
    def test_window_and_validation(self):
        import tkinter as tk
        from app import App
        root = tk.Tk()
        app = App(root)
        root.update()
        self.assertEqual(str(app.apply_button['state']), 'disabled')
        app.rgb[0].set('invalid')
        app.apply()
        self.assertIn('0 до 255', app.status.get())
        app.rgb[0].set('0')
        self.assertEqual(app.values(), (0,128,64))
        app.close()
        root.after(1500, root.quit)
        root.mainloop()

if __name__ == '__main__':
    unittest.main()
