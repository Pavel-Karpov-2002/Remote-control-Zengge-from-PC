import tkinter as tk
import unittest
from color_picker import ColorPicker, parse_hex

class ColorPickerTests(unittest.TestCase):
    def test_hex(self):
        self.assertEqual(parse_hex('#ff8040'),(255,128,64))
        for invalid in ('#FFF','FFFFFFF','gg0000'):
            with self.assertRaises(ValueError): parse_hex(invalid)

    def test_picker_inputs_and_cancel(self):
        root=tk.Tk();root.withdraw()
        picker=ColorPicker(root,(255,128,64));root.update()
        picker.hex.set('#20A0FF');self.assertTrue(picker.read_input(True))
        self.assertEqual(picker.rgb(),(32,160,255))
        picker.channels[0].set('256');self.assertFalse(picker.read_input(False))
        self.assertEqual(picker.rgb(),(32,160,255))
        picker.destroy();root.destroy()

    def test_black_white_and_confirmation(self):
        root=tk.Tk();root.withdraw()
        picker=ColorPicker(root,(0,0,0));root.update()
        self.assertEqual(picker.rgb(),(0,0,0))
        picker.hex.set('#FFFFFF');picker.read_input(True)
        self.assertEqual(picker.rgb(),(255,255,255))
        picker.confirm();self.assertEqual(picker.result,(255,255,255))
        root.destroy()
