"""Color Remote HSV picker, rendered with Tk only (no platform color dialog)."""
import colorsys
import tkinter as tk
from tkinter import ttk

BG, PANEL, FG, MUTED = '#1D2029', '#333541', '#F4F6FA', '#BFC3D3'

def parse_hex(value):
    value = value.strip().lstrip('#')
    if len(value) != 6:
        raise ValueError('Введите HEX из 6 символов, например FF8040.')
    try:
        return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        raise ValueError('Введите HEX из 6 символов, например FF8040.') from None

class ColorPicker(tk.Toplevel):
    def __init__(self, parent, initial):
        super().__init__(parent)
        self.withdraw()
        self.title('Выбрать цвет')
        self.configure(bg=BG)
        self.resizable(False, False)
        self.transient(parent)
        self.result = None
        self.h, self.s, self.v = colorsys.rgb_to_hsv(*(c/255 for c in initial))
        self.original = '#%02X%02X%02X' % initial
        self.last_hue = None
        self.hex = tk.StringVar()
        self.channels = [tk.StringVar() for _ in range(3)]
        self.error = tk.StringVar()
        frame = ttk.Frame(self, padding=24)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='Выбрать цвет', font=('Segoe UI', 18, 'bold')).pack(anchor='w', pady=(0, 16))
        self.field = tk.Canvas(frame, width=360, height=210, highlightthickness=0, cursor='crosshair', takefocus=True)
        self.field.pack()
        self.field.bind('<Button-1>', self.select_sv)
        self.field.bind('<B1-Motion>', self.select_sv)
        self.field.bind('<Left>', lambda e: self.nudge_sv(-.01, 0))
        self.field.bind('<Right>', lambda e: self.nudge_sv(.01, 0))
        self.field.bind('<Up>', lambda e: self.nudge_sv(0, .01))
        self.field.bind('<Down>', lambda e: self.nudge_sv(0, -.01))
        self.hue = tk.Canvas(frame, width=360, height=24, highlightthickness=0, cursor='hand2', takefocus=True)
        self.hue.pack(pady=(16, 18))
        self.hue.bind('<Button-1>', self.select_hue)
        self.hue.bind('<B1-Motion>', self.select_hue)
        self.hue.bind('<Left>', lambda e: self.nudge_hue(-1/360))
        self.hue.bind('<Right>', lambda e: self.nudge_hue(1/360))
        pixels = bytes(c for _ in range(24) for x in range(360) for c in self.hue_rgb(x/359))
        self.hue_image = tk.PhotoImage(data=b'P6\n360 24\n255\n'+pixels, format='PPM')
        self.hue.create_image(0, 0, image=self.hue_image, anchor='nw')
        swatches = ttk.Frame(frame)
        swatches.pack(fill='x')
        for label, color in (('Текущий', self.original), ('Новый', self.original)):
            col=ttk.Frame(swatches); col.pack(side='left', fill='x', expand=True)
            ttk.Label(col, text=label, foreground=MUTED).pack(anchor='w', pady=(0, 5))
            swatch=tk.Canvas(col, width=172, height=34, bg=color, highlightthickness=0)
            swatch.pack(anchor='w')
            self.new_swatch=swatch
        inputs=ttk.Frame(frame); inputs.pack(fill='x', pady=(16, 0))
        for i, (label, var, width) in enumerate([('HEX',self.hex,10)]+[(label,var,5) for label,var in zip(('R','G','B'),self.channels)]):
            col=ttk.Frame(inputs);col.pack(side='left', fill='x', expand=True, padx=(0, 8) if i<3 else 0)
            ttk.Label(col,text=label,foreground=MUTED).pack(anchor='w',pady=(0,5))
            entry=ttk.Entry(col,textvariable=var,width=width)
            entry.pack(fill='x')
            entry.bind('<FocusOut>', lambda e, hex_input=i==0: self.read_input(hex_input))
            entry.bind('<Return>', lambda e, hex_input=i==0: self.read_input(hex_input))
        ttk.Label(frame,textvariable=self.error,foreground='#FFB4AB',wraplength=360).pack(fill='x',pady=(8,8))
        actions=ttk.Frame(frame);actions.pack(fill='x')
        ttk.Button(actions,text='Отмена',command=self.destroy).pack(side='left')
        ttk.Button(actions,text='Выбрать цвет',style='Primary.TButton',command=self.confirm).pack(side='right')
        self.bind('<Escape>',lambda e:self.destroy())
        self.protocol('WM_DELETE_WINDOW',self.destroy)
        self.refresh()
        self.update_idletasks()
        x=parent.winfo_rootx()+(parent.winfo_width()-self.winfo_reqwidth())//2
        y=parent.winfo_rooty()+(parent.winfo_height()-self.winfo_reqheight())//2
        self.geometry(f'+{max(0,x)}+{max(0,y)}')
        self.deiconify();self.grab_set();self.field.focus_set()

    @staticmethod
    def hue_rgb(h):
        return tuple(round(c*255) for c in colorsys.hsv_to_rgb(h,1,1))

    def rgb(self):
        return tuple(round(c*255) for c in colorsys.hsv_to_rgb(self.h,self.s,self.v))

    def refresh(self):
        if self.last_hue != self.h:
            pixels=bytes(c for y in range(210) for x in range(360)
                         for c in (round(v*255) for v in colorsys.hsv_to_rgb(self.h,x/359,1-y/209)))
            self.sv_image=tk.PhotoImage(data=b'P6\n360 210\n255\n'+pixels,format='PPM')
            self.field.delete('all')
            self.field.create_image(0,0,image=self.sv_image,anchor='nw')
            self.last_hue=self.h
        self.field.delete('marker')
        x,y=self.s*359,(1-self.v)*209
        self.field.create_oval(x-6,y-6,x+6,y+6,outline='black',width=3,tags='marker')
        self.field.create_oval(x-5,y-5,x+5,y+5,outline='white',width=2,tags='marker')
        self.hue.delete('marker');x=self.h*359
        self.hue.create_rectangle(x-3,1,x+3,23,outline='black',width=3,tags='marker')
        self.hue.create_rectangle(x-2,1,x+2,23,outline='white',width=1,tags='marker')
        rgb=self.rgb();color='#%02X%02X%02X'%rgb
        self.new_swatch.configure(bg=color);self.hex.set(color)
        for variable,value in zip(self.channels,rgb): variable.set(str(value))
        self.error.set('')

    def select_sv(self,event):
        self.field.focus_set()
        self.s=max(0,min(1,event.x/359));self.v=1-max(0,min(1,event.y/209));self.refresh()

    def select_hue(self,event):
        self.hue.focus_set();self.h=max(0,min(1,event.x/359));self.refresh()

    def nudge_sv(self,ds,dv):
        self.s=max(0,min(1,self.s+ds));self.v=max(0,min(1,self.v+dv));self.refresh()

    def nudge_hue(self,delta):
        self.h=(self.h+delta)%1;self.refresh()

    def read_input(self,hex_input):
        try:
            rgb=parse_hex(self.hex.get()) if hex_input else tuple(int(v.get()) for v in self.channels)
            if any(not 0<=v<=255 for v in rgb): raise ValueError('Введите R, G и B от 0 до 255.')
            h,s,v=colorsys.rgb_to_hsv(*(c/255 for c in rgb))
            if s: self.h=h
            self.s,self.v=s,v;self.refresh()
            return True
        except ValueError as exc:
            self.error.set(str(exc) if hex_input else 'Введите R, G и B от 0 до 255.')
            return False

    def confirm(self):
        if self.error.get(): return
        self.result=self.rgb();self.destroy()

def ask_color(parent, initial):
    picker=ColorPicker(parent,initial)
    parent.wait_window(picker)
    return picker.result
