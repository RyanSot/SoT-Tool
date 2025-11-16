# Project: SoT HUD Enhanced
# Author: Redcube

import os
import sys
import json
import math
import threading
import time
import zipfile
from io import BytesIO
from PIL import Image
import win32gui
import win32con
import win32api
from ctypes import windll
import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets
import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer
from OpenGL.GL import *
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    from windows_capture import WindowsCapture, Frame, InternalCaptureControl
    WINDOWS_CAPTURE_AVAILABLE = True
except ImportError:
    WINDOWS_CAPTURE_AVAILABLE = False
    print("Windows Capture not available - HUD features disabled")

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "Config", "Config.json")

def OpenConfigFolder():
    """Open the Config folder in Windows Explorer"""
    config_dir = os.path.join(script_dir, "Config")
    try:
        if os.path.exists(config_dir):
            os.startfile(config_dir)
        else:
            os.startfile(script_dir)
        return True
    except Exception as e:
        print(f"Failed to open config folder: {e}")
        return False

class Config:
    # Default settings
    lowhealthvar = 70
    lowhealthcolour = "#FF3745"
    healthcolour = "#43EF88"
    overhealcolour = "#4CEF7E"
    regenbgcolour = "#676767"
    numberhealthcolour = "#FFFFFF"
    numberammocolour = "#FFFFFF"
    numberregencolour = "#FFFFFF"
    crosshaircolour = "#FFFFFF"
    crosshairoutlinecolour = "#080808"
    font = "Times New Roman"
    ammosize = 25
    hpsize = 25
    regensize = 25
    ammotoggle = True
    ammodecotoggle = True
    crosshairtoggle = False
    staticcrosshair = False
    healthbartoggle = True
    healthbardecotoggle = True
    skulltoggle = True
    regentoggle = True
    overlaytoggle = False
    numberhealthtoggle = False
    numberammotoggle = False
    numberregentoggle = False
    healthanchor = "sw"
    xoffsethealth = 0
    yoffsethealth = 0
    ammoanchor = "e"
    xoffsetammo = 0
    yoffsetammo = 0
    regenanchor = "e"
    xoffsetregen = 0
    yoffsetregen = 0
    healthprefix = ""
    healthsuffix = "/100"
    ammoprefix = ""
    ammosuffix = "/5"
    regenprefix = ""
    regensuffix = ""

    # Constants
    MINREGENCOLOUR = [0, 88, 0]
    MAXREGENCOLOUR = [76, 239, 186]
    
    # UI state
    calibrated_ammo_colour = (0, 0, 0)
    show_UI = False
    hp_slider = 75.0
    regen_slider = 50.0
    ammo_slider = 5
    low_hp_slider = lowhealthvar
    lowhealthvarchanged = False
    Name = "My Config"
    popup = False
    current_font = 0

    # Crosshair settings
    custom_crosshair_toggle = False
    custom_crosshair_size = 20
    custom_crosshair_thickness = 2
    custom_crosshair_gap = 4
    custom_crosshair_outline_toggle = True
    custom_crosshair_outline_thickness = 1
    crosshair_hotkey = "f1"
    waiting_for_hotkey = False

    # AFK and Travel
    afk_overlay_visible = False
    afk_overlay_text = ""
    afk_overlay_timer = 0
    travel_overlay_visible = False
    travel_overlay_text = ""
    travel_step = 0

    @classmethod
    def load_from_file(cls, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in data.items():
                if hasattr(cls, k):
                    setattr(cls, k, v)
        except Exception:
            pass

    @classmethod
    def save_config(cls, export=False):
        cfg = {
            "lowhealthvar": cls.lowhealthvar,
            "lowhealthcolour": cls.lowhealthcolour,
            "healthcolour": cls.healthcolour,
            "overhealcolour": cls.overhealcolour,
            "regenbgcolour": cls.regenbgcolour,
            "numberhealthcolour": cls.numberhealthcolour,
            "numberammocolour": cls.numberammocolour,
            "numberregencolour": cls.numberregencolour,
            "crosshaircolour": cls.crosshaircolour,
            "crosshairoutlinecolour": cls.crosshairoutlinecolour,
            "font": cls.font,
            "ammosize": cls.ammosize,
            "hpsize": cls.hpsize,
            "regensize": cls.regensize,
            "ammotoggle": cls.ammotoggle,
            "ammodecotoggle": cls.ammodecotoggle,
            "crosshairtoggle": cls.crosshairtoggle,
            "staticcrosshair": cls.staticcrosshair,
            "healthbartoggle": cls.healthbartoggle,
            "healthbardecotoggle": cls.healthbardecotoggle,
            "skulltoggle": cls.skulltoggle,
            "regentoggle": cls.regentoggle,
            "overlaytoggle": cls.overlaytoggle,
            "numberhealthtoggle": cls.numberhealthtoggle,
            "numberammotoggle": cls.numberammotoggle,
            "numberregentoggle": cls.numberregentoggle,
            "healthanchor": cls.healthanchor,
            "xoffsethealth": cls.xoffsethealth,
            "yoffsethealth": cls.yoffsethealth,
            "ammoanchor": cls.ammoanchor,
            "xoffsetammo": cls.xoffsetammo,
            "yoffsetammo": cls.yoffsetammo,
            "regenanchor": cls.regenanchor,
            "xoffsetregen": cls.xoffsetregen,
            "yoffsetregen": cls.yoffsetregen,
            "healthprefix": cls.healthprefix,
            "healthsuffix": cls.healthsuffix,
            "ammoprefix": cls.ammoprefix,
            "ammosuffix": cls.ammosuffix,
            "regenprefix": cls.regenprefix,
            "regensuffix": cls.regensuffix,
            "calibrated_ammo_colour": cls.calibrated_ammo_colour,
            "custom_crosshair_toggle": cls.custom_crosshair_toggle,
            "custom_crosshair_size": cls.custom_crosshair_size,
            "custom_crosshair_thickness": cls.custom_crosshair_thickness,
            "custom_crosshair_gap": cls.custom_crosshair_gap,
            "custom_crosshair_outline_toggle": cls.custom_crosshair_outline_toggle,
            "custom_crosshair_outline_thickness": cls.custom_crosshair_outline_thickness,
            "crosshair_hotkey": cls.crosshair_hotkey
        }
        if export:
            cfg.pop("calibrated_ammo_colour", None)
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=4)
        except Exception:
            pass
    
    @classmethod
    def load_config(cls, path):
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(os.path.join(script_dir, "Config"))

def hex_to_rgb_f(hex_color):
    hex_color = hex_color.lstrip("#")
    return [
        int(hex_color[0:2], 16) / 255.0,
        int(hex_color[2:4], 16) / 255.0,
        int(hex_color[4:6], 16) / 255.0
    ]

def rgb_f_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

def get_dyn_pos_right(pos):
    try:
        hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
        return round(win32gui.GetClientRect(hwnd)[2] + get_dyn_x(pos-1920))
    except Exception:
        user32 = windll.user32
        sot_width = user32.GetSystemMetrics(0)
        return round(sot_width + get_dyn_x(pos-1920))

def get_dyn_x(pos):
    try:
        hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
        _, top, _, bot = win32gui.GetClientRect(hwnd)
        sot_height = bot - top
    except Exception:
        user32 = windll.user32
        sot_height = user32.GetSystemMetrics(1)
    normal_sot_width = (sot_height / 9) * 16
    return round((pos / 1920) * normal_sot_width)

def get_dyn_y(pos):
    try:
        hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
        _, top, _, bot = win32gui.GetClientRect(hwnd)
        sot_height = bot - top
    except Exception:
        user32 = windll.user32
        sot_height = user32.GetSystemMetrics(1)
    return round((pos / 1080) * sot_height)

# Anchor mapping
ALIGN_MAP = {
    "n": QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter,
    "ne": QtCore.Qt.AlignTop | QtCore.Qt.AlignRight,
    "e": QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter,
    "se": QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight,
    "s": QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter,
    "sw": QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft,
    "w": QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
    "nw": QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft,
    "x": QtCore.Qt.AlignCenter
}

def make_rect(x, y, xoffset, yoffset, anchor="x"):
    w = h = get_dyn_x(1920)
    half_w, half_h = w // 2, h // 2

    anchor_map = {
        "x": ((x + int(xoffset)) - half_w, (y + int(yoffset)) - half_h),
        "n": ((x + int(xoffset)) - half_w, (y + int(yoffset))),
        "ne": ((x + int(xoffset)) - w, (y + int(yoffset))),
        "e": ((x + int(xoffset)) - w, (y + int(yoffset)) - half_h),
        "se": ((x + int(xoffset)) - w, (y + int(yoffset)) - h),
        "s": ((x + int(xoffset)) - half_w, (y + int(yoffset)) - h),
        "sw": ((x + int(xoffset)), (y + int(yoffset)) - h),
        "w": ((x + int(xoffset)), (y + int(yoffset)) - half_h),
        "nw": ((x + int(xoffset)), (y + int(yoffset)))
    }
    
    x_pos, y_pos = anchor_map.get(anchor, anchor_map["x"])
    return QtCore.QRect(x_pos, y_pos, w, h)

# Capture setup
TARGET_WINDOW = "Sea of Thieves"
latest_frame = None
frame_ready = False

def start_capture():
    global capture
    if not WINDOWS_CAPTURE_AVAILABLE:
        return
        
    try:
        capture = WindowsCapture(
            cursor_capture=False,
            draw_border=False,
            window_name=TARGET_WINDOW
        )

        @capture.event
        def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
            global latest_frame, frame_ready
            latest_frame = frame.frame_buffer[:, :, :3]
            frame_ready = True

        @capture.event
        def on_closed():
            print("Capture stopped")

        capture.start_free_threaded()
    except Exception as e:
        print(f"Capture initialization failed: {e}")
    
def get_pixel(x, y):
    global latest_frame, frame_ready
    if not frame_ready or latest_frame is None:
        return None
    try:
        b, g, r = latest_frame[y, x]
        return (r, g, b)
    except:
        return None

class PixmapManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.cache = {}

    def load(self, name, size=None):
        key = (name, size)
        if key in self.cache:
            return self.cache[key]
            
        path = os.path.join(self.base_dir, name)
        if not os.path.exists(path):
            return None
            
        try:
            img = Image.open(path).convert("RGBA")
            if size:
                img = img.resize(size, Image.LANCZOS)
            buf = BytesIO()
            img.save(buf, format="PNG")
            pix = QtGui.QPixmap()
            if pix.loadFromData(buf.getvalue()):
                self.cache[key] = pix
                return pix
        except Exception:
            pass
        return None

class ConfigWatcher:
    def __init__(self, parent):
        self.parent = parent
        self.config_dir = os.path.join(os.path.dirname(__file__), "Config")
        self.observer = None
        self._start()

    def _start(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        event_handler = _ConfigEventHandler(self.parent.update_config)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.config_dir, recursive=True)
        self.observer.start()
        
    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()

class _ConfigEventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_any_event(self, event):
        if not event.is_directory:
            self.callback()

class InputSimulator:
    def SendKey(self, key, duration=50):
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(duration / 1000)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    def SendKeyCombo(self, key1, key2):
        win32api.keybd_event(key1, 0, 0, 0)
        win32api.keybd_event(key2, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(key2, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(key1, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    def SendMouseClick(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    
    def HoldKey(self, key, duration=1.0):
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(duration)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)

class SOTAssistant:
    def __init__(self):
        self.input = InputSimulator()
        self.afkActive = False
        self.travelBetaActive = False
        self.afkPaused = False
        self.travelTiles = 2
        self.travelStep = 0

    def AFKThread(self):
        while self.afkActive:
            if self.afkPaused:
                while self.afkPaused and self.afkActive:
                    time.sleep(0.1)
                if not self.afkActive:
                    break

            preset = (win32api.GetTickCount() % 4) + 1
            keys = [
                [0x57, 0x41, 0x53, 0x44],  # W, A, S, D
                [0x57, 0x44, 0x53, 0x41],  # W, D, S, A
                [0x41, 0x53, 0x44, 0x57],  # A, S, D, W
                [0x44, 0x57, 0x41, 0x53]   # D, W, A, S
            ]
            
            for key in keys[preset-1]:
                if not self.SendKeyWithCheck(key, 300):
                    break

            if self.afkActive and not self.afkPaused:
                time.sleep(3)

    def TravelBetaThread(self):
        self.travelStep = 1
        Config.travel_step = 1
        
        Config.travel_overlay_text = "TRAVEL BETA INSTRUCTIONS:\n\n1. MANUALLY grab cannon\n2. Press F5 to continue"
        
        f5_pressed = False
        for _ in range(300):
            if not self.travelBetaActive:
                return
            if keyboard.is_pressed('f5'):
                f5_pressed = True
                time.sleep(0.5)
                break
            time.sleep(0.1)
        
        if not f5_pressed or not self.travelBetaActive:
            self.StopTravel()
            return
        
        self.input.HoldKey(0x53, 0.5)
        time.sleep(0.2)
        self.input.HoldKey(0x57, 0.5)
        time.sleep(0.1)
        
        if not self.travelBetaActive:
            return
        
        self.travelStep = 2
        Config.travel_step = 2
        Config.travel_overlay_text = "TRAVEL BETA INSTRUCTIONS:\n\n3. MANUALLY climb into cannon\n4. Press F6 to fire\nWARNING: Distance may vary due to waves"
        
        f6_pressed = False
        for _ in range(300):
            if not self.travelBetaActive:
                return
            if keyboard.is_pressed('f6'):
                f6_pressed = True
                time.sleep(0.5)
                break
            time.sleep(0.1)
        
        if not f6_pressed or not self.travelBetaActive:
            self.StopTravel()
            return
        
        self.travelStep = 3
        Config.travel_step = 3
        
        self.input.SendMouseClick()
        time.sleep(0.1)
        
        time.sleep(4)
        if self.travelBetaActive:
            self.input.SendKeyCombo(win32con.VK_MENU, win32con.VK_RETURN)
        
        travel_duration = self.travelTiles * 5
        time.sleep(travel_duration - 4)
        
        if self.travelBetaActive:
            self.input.SendKeyCombo(win32con.VK_MENU, win32con.VK_SPACE)
        
        self.StopTravel()

    def SendKeyWithCheck(self, key, duration):
        if not self.afkActive or self.afkPaused:
            return False
        win32api.keybd_event(key, 0, 0, 0)
        steps = duration // 100
        for i in range(steps):
            if not self.afkActive or self.afkPaused:
                win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
                return False
            time.sleep(0.1)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        return True

    def StartAFK(self):
        if not self.afkActive:
            self.afkActive = True
            self.afkPaused = False
            threading.Thread(target=self.AFKThread, daemon=True).start()
            Config.afk_overlay_visible = True
            Config.afk_overlay_text = "AFK: ACTIVE - F3=Pause F4=Stop"
            Config.afk_overlay_timer = 0

    def StopAFK(self):
        if self.afkActive:
            self.afkActive = False
            self.afkPaused = False
            for key in [0x57, 0x41, 0x53, 0x44]:
                win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
            Config.afk_overlay_text = "AFK: STOPPED"
            Config.afk_overlay_timer = time.time()

    def ToggleAFKPause(self):
        if self.afkActive:
            self.afkPaused = not self.afkPaused
            Config.afk_overlay_text = "AFK: PAUSED - F3=Resume F4=Stop" if self.afkPaused else "AFK: ACTIVE - F3=Pause F4=Stop"
            Config.afk_overlay_timer = 0

    def StartTravelBeta(self, tiles):
        if not self.travelBetaActive and tiles > 0:
            self.travelTiles = tiles
            self.travelBetaActive = True
            self.travelStep = 0
            Config.travel_step = 0
            threading.Thread(target=self.TravelBetaThread, daemon=True).start()
            Config.travel_overlay_visible = True
            Config.travel_overlay_text = "TRAVEL: Starting... Get ready to grab cannon"

    def StopTravel(self):
        if self.travelBetaActive:
            self.travelBetaActive = False
            self.travelStep = 0
            Config.travel_step = 0
            Config.travel_overlay_visible = False

class Overlay(QtWidgets.QWidget):
    def __init__(self, screen_width, screen_height):
        self.config_watcher = ConfigWatcher(self)
        flags = QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool
        super().__init__(None, flags)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowTransparentForInput)
        self.setGeometry(0, 0, screen_width, screen_height)

        self.assistant = SOTAssistant()
        self.fonts = QtGui.QFontDatabase().families()
        
        # Initialize state
        self.reset_state()
        
        # Load images
        self.load_all()

        # Setup UI elements
        self.setup_ui_elements()

        # Timer for updates
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_loop)
        self.timer.start(50)  # 20 FPS

    def reset_state(self):
        self.screen_img = None
        self.ammo_states = [False] * 6
        self.numberammo_text = ""
        self.health_num_text = ""
        self.show_overlay = False
        self.regen_extent = 0
        self.regen_text = f"{Config.regenprefix}0{Config.regensuffix}"
        self.show_health = False
        self.show_regen = False
        self.show_skull_red = False
        self.show_skull_green = False
        self.current_hp = 0

    def setup_ui_elements(self):
        # Calibration label
        self.calibration_label = QtWidgets.QLabel(self)
        self.calibration_label.setStyleSheet("color: white; font-size: 28px; background: rgba(0,0,0,160); padding: 8px;")
        self.calibration_label.setAlignment(QtCore.Qt.AlignCenter)
        self.calibration_label.setFixedWidth(1100)
        self.calibration_label.hide()

        # AFK overlay label
        self.afk_overlay_label = QtWidgets.QLabel(self)
        self.afk_overlay_label.setStyleSheet("color: yellow; font-size: 24px; background: rgba(0,0,0,180); padding: 8px; border: 2px solid yellow;")
        self.afk_overlay_label.setAlignment(QtCore.Qt.AlignCenter)
        self.afk_overlay_label.setFixedWidth(500)
        self.afk_overlay_label.hide()

        # Travel overlay label
        self.travel_overlay_label = QtWidgets.QLabel(self)
        self.travel_overlay_label.setStyleSheet("color: cyan; font-size: 20px; background: rgba(0,0,0,180); padding: 8px; border: 2px solid cyan;")
        self.travel_overlay_label.setAlignment(QtCore.Qt.AlignCenter)
        self.travel_overlay_label.setFixedWidth(700)
        self.travel_overlay_label.hide()

    def set_click_through_native(self):
        try:
            hwnd = int(self.winId())
            exStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            exStyle &= ~win32con.WS_EX_APPWINDOW
            exStyle &= ~win32con.WS_EX_TOOLWINDOW            
            exStyle |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exStyle)
        except Exception as e:
            print("Failed to set native click-through:", e)
            
    def update_config(self):
        Config.load_from_file(config_path)
        time.sleep(0.1)
        self.load_all()
        self.update()

    def load_all(self):
        pm = PixmapManager(os.path.join(script_dir, "Config"))
        images = {
            'green_skull': ("Health_Bar_Skull_Green.png", (get_dyn_x(53), get_dyn_y(57))),
            'red_skull': ("Health_Bar_Skull_Red.png", (get_dyn_x(53), get_dyn_y(57))),
            'ammo_bg': ("ammogauge-BG-Frame.png", (get_dyn_x(352), get_dyn_y(126))),
            'ammo': ("ammogauge-pistol-ammunition.png", (get_dyn_x(22), get_dyn_y(22))),
            'healthbar_bg': ("Health_Bar_BG_Frame.png", (get_dyn_x(315), get_dyn_y(100))),
            'regen_skull': ("Regen_Meter_Skull.png", (get_dyn_x(60), get_dyn_y(60))),
            'overlay': ("General_Overlay.png", (get_dyn_x(1920), get_dyn_y(1080)))
        }
        
        for attr, (name, size) in images.items():
            setattr(self, f"{attr}_pix", pm.load(name, size))

    def draw_custom_crosshair(self, painter):
        if not Config.custom_crosshair_toggle:
            return
            
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        size = Config.custom_crosshair_size
        thickness = Config.custom_crosshair_thickness
        gap = Config.custom_crosshair_gap
        
        # Draw outline first if enabled
        if Config.custom_crosshair_outline_toggle:
            outline_thickness = Config.custom_crosshair_outline_thickness
            painter.setPen(QtGui.QPen(QtGui.QColor(Config.crosshairoutlinecolour), thickness + outline_thickness * 2))
            
            # Draw horizontal line outline
            painter.drawLine(center_x - size, center_y, center_x - gap, center_y)
            painter.drawLine(center_x + gap, center_y, center_x + size, center_y)
            
            # Draw vertical line outline
            painter.drawLine(center_x, center_y - size, center_x, center_y - gap)
            painter.drawLine(center_x, center_y + gap, center_x, center_y + size)
        
        # Draw main crosshair
        painter.setPen(QtGui.QPen(QtGui.QColor(Config.crosshaircolour), thickness))
        
        # Draw horizontal line
        painter.drawLine(center_x - size, center_y, center_x - gap, center_y)
        painter.drawLine(center_x + gap, center_y, center_x + size, center_y)
        
        # Draw vertical line
        painter.drawLine(center_x, center_y - size, center_x, center_y - gap)
        painter.drawLine(center_x, center_y + gap, center_x, center_y + size)

    def update_loop(self):
        # Update overlays
        self.update_overlays()
        
        # Calibration stage
        if Config.calibrated_ammo_colour == (0, 0, 0):
            self.handle_calibration()
            return

        try:
            foreground = win32gui.GetForegroundWindow()
            hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
            
            if hwnd and hwnd == foreground and not Config.show_UI:
                self.show_overlay = True
                self.detect_game_elements()
            elif not Config.show_UI:
                self.reset_hud()
            else:
                self.update()
                
        except Exception:
            pass

    def update_overlays(self):
        # AFK overlay
        if Config.afk_overlay_visible:
            if Config.afk_overlay_timer > 0 and time.time() - Config.afk_overlay_timer > 3:
                Config.afk_overlay_visible = False
            else:
                self.afk_overlay_label.setText(Config.afk_overlay_text)
                self.afk_overlay_label.move((self.screen_width - self.afk_overlay_label.width()) // 2, 100)
                self.afk_overlay_label.show()
        else:
            self.afk_overlay_label.hide()

        # Travel overlay
        if Config.travel_overlay_visible:
            step_info = {
                1: "\n\nCURRENT STEP: Grab cannon → Press F5",
                2: "\n\nCURRENT STEP: Climb into cannon → Press F6", 
                3: "\n\nCURRENT STEP: Flying... DO NOT TOUCH ANYTHING"
            }
            full_text = Config.travel_overlay_text + step_info.get(Config.travel_step, "") + f"\n\nTiles: {self.assistant.travelTiles} (≈{self.assistant.travelTiles * 5} seconds)\nWARNING: Distance may vary due to waves\nPress F2 to cancel"
            
            self.travel_overlay_label.setText(full_text)
            self.travel_overlay_label.move((self.screen_width - self.travel_overlay_label.width()) // 2, 150)
            self.travel_overlay_label.show()
        else:
            self.travel_overlay_label.hide()

    def handle_calibration(self):
        self.calibration_label.setText("Pull out a gun with full ammo to calibrate ammo colour")
        self.calibration_label.move((self.screen_width - self.calibration_label.width())//2, self.screen_height - 140)
        self.calibration_label.show()
        QtWidgets.QApplication.processEvents()
        
        try:
            hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
            if hwnd == 0:
                return
                
            px = get_pixel(get_dyn_pos_right(1772), get_dyn_y(980))
            positions = [get_dyn_pos_right(1746), get_dyn_pos_right(1720), get_dyn_pos_right(1694), get_dyn_pos_right(1668)]
            cond = all(px == get_pixel(pos, get_dyn_y(980)) for pos in positions) and (px[1] >= 178)
            
            if cond:
                Config.calibrated_ammo_colour = tuple(int(x) for x in px)
                self.calibration_label.hide()
                Config.save_config(False)
        except Exception:
            pass

    def detect_game_elements(self):
        # Ammo detection
        if Config.ammotoggle or Config.crosshairtoggle or Config.numberammotoggle:
            for i in range(6):
                x_pos = get_dyn_pos_right(1642) + get_dyn_x(26*i)
                if self.screen_height == 1440:
                    x_pos = get_dyn_pos_right(1648) + 33*i
                elif self.screen_height == 2160:
                    x_pos = get_dyn_pos_right(1641) + get_dyn_x(26*i)
                    
                px = get_pixel(x_pos, get_dyn_y(980))
                self.ammo_states[i] = px == tuple(Config.calibrated_ammo_colour)
                
            if Config.numberammotoggle:
                for i in range(6):
                    if self.ammo_states[i]:
                        ammocount = 6 - i
                        self.numberammo_text = f"{Config.ammoprefix}{ammocount}{Config.ammosuffix}"
                        break

        # Health/regen detection
        if Config.healthbartoggle or Config.regentoggle or Config.skulltoggle or Config.numberhealthtoggle:
            pixel_colour = get_pixel(get_dyn_x(169), get_dyn_y(977))
            control_colour = get_pixel(get_dyn_x(176), get_dyn_y(977))
            extra_px = get_pixel(get_dyn_x(141), get_dyn_y(955))
            
            if (pixel_colour and control_colour and extra_px and
                max(pixel_colour[:3]) <= 3 and extra_px != control_colour and 
                control_colour[1] >= 55 and not Config.show_UI):
                
                self.show_health = True
                self.show_regen = True
                self.detect_regen()
                self.detect_health(control_colour)
            else:
                self.hide_hud_elements()

        self.update()

    def detect_regen(self):
        regen_control_colour = get_pixel(get_dyn_x(141), get_dyn_y(958))
        if (regen_control_colour and
            regen_control_colour[0] <= Config.MAXREGENCOLOUR[0] and
            Config.MINREGENCOLOUR[1] <= regen_control_colour[1] <= Config.MAXREGENCOLOUR[1] and
            regen_control_colour[2] <= Config.MAXREGENCOLOUR[2]):
            
            for i in range(200):
                theta = (2 * math.pi / 200) * -(i+50)
                x = get_dyn_x(140 + 23 * math.cos(theta))
                y = get_dyn_y(982 + 23 * math.sin(theta))
                px = get_pixel(x, y)
                if (px and px[0] <= Config.MAXREGENCOLOUR[0] and
                    Config.MINREGENCOLOUR[1] <= px[1] <= Config.MAXREGENCOLOUR[1] and
                    px[2] <= Config.MAXREGENCOLOUR[2]):
                    
                    if Config.regentoggle:
                        overhealhp = 360 - (i * 1.8)
                        self.regen_extent = int(overhealhp)
                    self.regen_text = f"{Config.regenprefix}{200-i}{Config.regensuffix}"
                    if i >= 198:
                        self.regen_extent = 0
                        self.regen_text = f"{Config.regenprefix}0{Config.regensuffix}"
                    break

    def detect_health(self, control_colour):
        for hp in range(100):
            px = get_pixel(get_dyn_x(384 - (2*hp)), get_dyn_y(984))
            if px == control_colour and px[1] >= 55:
                self.current_hp = 100 - hp
                break

        if Config.skulltoggle:
            self.show_skull_red = (self.current_hp <= Config.lowhealthvar)
            self.show_skull_green = not self.show_skull_red

        if Config.numberhealthtoggle:
            self.health_num_text = f"{Config.healthprefix}{self.current_hp}{Config.healthsuffix}"

    def hide_hud_elements(self):
        self.show_health = False
        self.show_regen = False
        self.health_num_text = ""
        self.regen_text = f"{Config.regenprefix}0{Config.regensuffix}"
        self.show_skull_red = False
        self.show_skull_green = False
        self.current_hp = 0
        self.regen_extent = 0

    def reset_hud(self):
        self.screen_img = None
        self.ammo_states = [False] * 6
        self.numberammo_text = ""
        self.show_overlay = False
        self.hide_hud_elements()
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw overlay image
        if (self.show_overlay or Config.show_UI) and Config.overlaytoggle:
            if self.overlay_pix:
                painter.drawPixmap((self.screen_width - self.overlay_pix.width()) // 2,
                                 (self.screen_height - self.overlay_pix.height()) // 2,
                                 self.overlay_pix)
            else:
                painter.fillRect(0, 0, self.screen_width, self.screen_height, QtGui.QColor(0, 0, 0, 50))
        
        # Draw ammo decoration
        if (any(self.ammo_states) or Config.show_UI) and Config.ammodecotoggle:
            if self.ammo_bg_pix:
                painter.drawPixmap(get_dyn_pos_right(1546), get_dyn_y(919), self.ammo_bg_pix)
            else:
                painter.setBrush(QtGui.QColor(50, 50, 50, 200))
                painter.setPen(QtCore.Qt.NoPen)
                painter.drawRect(get_dyn_pos_right(1546), get_dyn_y(919), get_dyn_x(352), get_dyn_y(126))
        
        # Draw ammo images
        if (any(self.ammo_states) or Config.show_UI) and Config.ammotoggle:
            self.draw_ammo(painter)
        
        # Draw crosshair
        if ((any(self.ammo_states) or Config.staticcrosshair or Config.show_UI) and 
            Config.crosshairtoggle):
            if Config.custom_crosshair_toggle:
                self.draw_custom_crosshair(painter)
            else:
                painter.setBrush(QtGui.QColor(Config.crosshaircolour))
                painter.setPen(QtGui.QColor(Config.crosshairoutlinecolour))
                diameter = 4
                painter.drawEllipse(QtCore.QRectF(self.screen_width/2 - diameter/2, 
                                                self.screen_height/2 - diameter/2, 
                                                diameter, diameter))
        
        # Draw healthbar
        if ((self.show_health or Config.show_UI) and Config.healthbartoggle and 
            getattr(self, "current_hp", None) is not None):
            self.draw_healthbar(painter)
        
        # Draw healthbar decoration
        if (self.show_health or Config.show_UI) and Config.healthbardecotoggle:
            if self.healthbar_bg_pix:
                painter.drawPixmap(get_dyn_x(256) - self.healthbar_bg_pix.width()//2, 
                                 get_dyn_y(982) - self.healthbar_bg_pix.height()//2, 
                                 self.healthbar_bg_pix)
        
        # Draw regen meter
        if (self.show_regen or Config.show_UI) and Config.regentoggle:
            self.draw_regen_meter(painter)
        
        # Draw skulls
        if (self.show_health or Config.show_UI) and Config.skulltoggle:
            self.draw_skulls(painter)
        
        # Draw text elements
        self.draw_text_elements(painter)
        
        painter.end()

    def draw_ammo(self, painter):
        if not self.ammo_pix:
            return
            
        for i in range(6):
            if not self.ammo_states[i]:
                continue
                
            x = get_dyn_pos_right(1642) + get_dyn_x(26*i)
            y = get_dyn_y(980)
            
            if self.screen_height == 1440:
                x = get_dyn_pos_right(1648) + 33*i
                y = get_dyn_y(981)
            elif self.screen_height == 2160:
                x = get_dyn_pos_right(1641) + get_dyn_x(26*i)
                y = get_dyn_y(981)
                
            painter.drawPixmap(x - self.ammo_pix.width()//2, 
                             y - self.ammo_pix.height()//2, 
                             self.ammo_pix)

    def draw_healthbar(self, painter):
        hp = self.current_hp
        br_x = get_dyn_x(396 - (((396-192)/100)*(100-hp)))
        tr_x = get_dyn_x(380 - (((380-176)/100)*(100-hp)))
        pts = [
            QtCore.QPointF(get_dyn_x(165), get_dyn_y(973)),
            QtCore.QPointF(get_dyn_x(181), get_dyn_y(990)),
            QtCore.QPointF(br_x, get_dyn_y(990)),
            QtCore.QPointF(tr_x, get_dyn_y(973))
        ]
        poly = QtGui.QPolygonF(pts)
        color = Config.lowhealthcolour if self.current_hp <= Config.lowhealthvar else Config.healthcolour
        painter.setBrush(QtGui.QColor(color))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawPolygon(poly)

    def draw_regen_meter(self, painter):
        painter.setBrush(QtGui.QColor(Config.regenbgcolour))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(QtCore.QRectF(get_dyn_x(114), get_dyn_y(954), get_dyn_x(54), get_dyn_y(54)))
        
        rect = QtCore.QRectF(get_dyn_x(141-27), get_dyn_y(981-27), get_dyn_x(55), get_dyn_y(55))
        start16 = int(90 * 16)
        span16 = int(-self.regen_extent * 16)
        painter.setBrush(QtGui.QColor(Config.overhealcolour))
        painter.drawPie(rect, start16, span16)
        
        if self.regen_skull_pix:
            painter.drawPixmap(get_dyn_x(141) - self.regen_skull_pix.width()//2, 
                             get_dyn_y(982) - self.regen_skull_pix.height()//2, 
                             self.regen_skull_pix)

    def draw_skulls(self, painter):
        if self.show_skull_green and self.green_skull_pix:
            painter.drawPixmap(get_dyn_x(140) - self.green_skull_pix.width()//2, 
                             get_dyn_y(981) - self.green_skull_pix.height()//2, 
                             self.green_skull_pix)
        
        if self.show_skull_red and self.red_skull_pix:
            painter.drawPixmap(get_dyn_x(140) - self.red_skull_pix.width()//2, 
                             get_dyn_y(981) - self.red_skull_pix.height()//2, 
                             self.red_skull_pix)

    def draw_text_elements(self, painter):
        # Health number
        if ((self.health_num_text and self.show_health) or Config.show_UI) and Config.numberhealthtoggle:
            painter.setPen(QtGui.QColor(Config.numberhealthcolour))
            font_q = QtGui.QFont(Config.font, Config.hpsize)
            painter.setFont(font_q)
            healthrect = make_rect(get_dyn_x(170), get_dyn_y(973), 
                                 get_dyn_x(Config.xoffsethealth), get_dyn_y(Config.yoffsethealth), 
                                 Config.healthanchor)
            painter.drawText(healthrect, ALIGN_MAP[Config.healthanchor], self.health_num_text)

        # Regen number
        if (self.show_regen or Config.show_UI) and Config.numberregentoggle:
            painter.setPen(QtGui.QColor(Config.numberregencolour))
            font_q = QtGui.QFont(Config.font, Config.regensize)
            painter.setFont(font_q)
            regenrect = make_rect(get_dyn_x(100), get_dyn_y(980), 
                                get_dyn_x(Config.xoffsetregen), get_dyn_y(Config.yoffsetregen), 
                                Config.regenanchor)
            painter.drawText(regenrect, ALIGN_MAP[Config.regenanchor], self.regen_text)
            
        # Ammo number
        if ((any(self.ammo_states) or Config.show_UI) and Config.numberammotoggle):
            painter.setPen(QtGui.QColor(Config.numberammocolour))
            font_q = QtGui.QFont(Config.font, Config.ammosize)
            painter.setFont(font_q)
            ammorect = make_rect(get_dyn_pos_right(1620), get_dyn_y(980), 
                               get_dyn_x(Config.xoffsetammo), get_dyn_pos_right(Config.yoffsetammo), 
                               Config.ammoanchor)
            painter.drawText(ammorect, ALIGN_MAP[Config.ammoanchor], self.numberammo_text)

def draw_anchor_buttons(imgui, anchor_grid, config_attr, fonts):
    """Draw anchor button grid"""
    for row_idx, row in enumerate(anchor_grid):
        for col_idx, anchor in enumerate(row):
            is_selected = getattr(Config, config_attr) == anchor
            if is_selected:
                imgui.push_style_color(imgui.COLOR_BUTTON, 0.3, 0.6, 0.9, 1.0)
            else:
                imgui.push_style_color(imgui.COLOR_BUTTON, 0.4, 0.4, 0.4, 1.0)
                
            if imgui.button(anchor, width=25, height=25):
                setattr(Config, config_attr, anchor)
                
            imgui.pop_style_color()
            if col_idx < len(row) - 1:
                imgui.same_line()

def draw_hud_config_section(imgui, anchor_grid, screen_width, status_text, hotkey_mapping_active, hotkey_timeout, fonts):
    """Draw HUD configuration section with proper crosshair sliders"""
    # Healthbar section
    if imgui.tree_node("Healthbar Settings"):
        changed, Config.healthbartoggle = imgui.checkbox("Healthbar", Config.healthbartoggle)
        if Config.healthbartoggle:
            health_rgb = hex_to_rgb_f(Config.healthcolour)
            changed, health_rgb = imgui.color_edit3("Health colour", *health_rgb)
            if changed:
                Config.healthcolour = rgb_f_to_hex(health_rgb)
            
            changed, Config.low_hp_slider = imgui.slider_float("Critical health", Config.low_hp_slider, 0, 100, "%.0f%%")
            Config.lowhealthvar = int(Config.low_hp_slider)
            if imgui.is_item_hovered() or imgui.is_item_active():
                Config.lowhealthvarchanged = True
            else:
                Config.lowhealthvarchanged = False
                
            lowhealth_rgb = hex_to_rgb_f(Config.lowhealthcolour)
            changed, lowhealth_rgb = imgui.color_edit3("Low health colour", *lowhealth_rgb)
            if changed:
                Config.lowhealthcolour = rgb_f_to_hex(lowhealth_rgb)
                
        changed, Config.healthbardecotoggle = imgui.checkbox("Healthbar decorations", Config.healthbardecotoggle)
        changed, Config.numberhealthtoggle = imgui.checkbox("Health number", Config.numberhealthtoggle)
        
        if Config.numberhealthtoggle:
            changed, Config.hpsize = imgui.slider_int("Font Size", Config.hpsize, 1, 128, "%d px")
            changed, healthoffset = imgui.drag_int2("Position", Config.xoffsethealth, Config.yoffsethealth, 1, -screen_width, screen_width)
            Config.xoffsethealth, Config.yoffsethealth = healthoffset
            
            numberhealth_rgb = hex_to_rgb_f(Config.numberhealthcolour)
            changed, numberhealth_rgb = imgui.color_edit3("Number Color", *numberhealth_rgb)
            if changed:
                Config.numberhealthcolour = rgb_f_to_hex(numberhealth_rgb)
                
            imgui.text("Anchor:")
            draw_anchor_buttons(imgui, anchor_grid, "healthanchor", fonts)
            
        changed, Config.hp_slider = imgui.slider_float("Health test", Config.hp_slider, 0, 100, "%.0f%%")
        imgui.tree_pop()
    
    # Ammo section
    if imgui.tree_node("Ammo Settings"):
        changed, Config.ammotoggle = imgui.checkbox("Ammo", Config.ammotoggle)
        changed, Config.ammodecotoggle = imgui.checkbox("Ammo decorations", Config.ammodecotoggle)
        changed, Config.numberammotoggle = imgui.checkbox("Ammo number", Config.numberammotoggle)
        
        if Config.numberammotoggle:
            changed, Config.ammosize = imgui.slider_int("Font Size", Config.ammosize, 1, 128, "%d px")
            changed, ammooffset = imgui.drag_int2("Position", Config.xoffsetammo, Config.yoffsetammo, 1, -screen_width, screen_width)
            Config.xoffsetammo, Config.yoffsetammo = ammooffset
            
            numberammo_rgb = hex_to_rgb_f(Config.numberammocolour)
            changed, numberammo_rgb = imgui.color_edit3("Number Color", *numberammo_rgb)
            if changed:
                Config.numberammocolour = rgb_f_to_hex(numberammo_rgb)
                
            imgui.text("Anchor:")
            draw_anchor_buttons(imgui, anchor_grid, "ammoanchor", fonts)
            
        changed, Config.ammo_slider = imgui.slider_int("Ammo test", Config.ammo_slider, 0, 6, "%d shots")
        imgui.tree_pop()
    
    # Crosshair section - IMPROVED WITH PROPER SLIDERS
    if imgui.tree_node("Crosshair Settings"):
        changed, Config.crosshairtoggle = imgui.checkbox("Crosshair", Config.crosshairtoggle)
        if Config.crosshairtoggle:
            changed, Config.custom_crosshair_toggle = imgui.checkbox("Custom Crosshair", Config.custom_crosshair_toggle)
            
            if Config.custom_crosshair_toggle:
                # Proper crosshair sliders with min/max values and formatting
                imgui.text("Crosshair Size:")
                changed, Config.custom_crosshair_size = imgui.slider_int("##size", Config.custom_crosshair_size, 5, 100, "%d px")
                
                imgui.text("Crosshair Thickness:")
                changed, Config.custom_crosshair_thickness = imgui.slider_int("##thickness", Config.custom_crosshair_thickness, 1, 10, "%d px")
                
                imgui.text("Crosshair Gap:")
                changed, Config.custom_crosshair_gap = imgui.slider_int("##gap", Config.custom_crosshair_gap, 0, 50, "%d px")
                
                changed, Config.custom_crosshair_outline_toggle = imgui.checkbox("Outline", Config.custom_crosshair_outline_toggle)
                if Config.custom_crosshair_outline_toggle:
                    imgui.text("Outline Thickness:")
                    changed, Config.custom_crosshair_outline_thickness = imgui.slider_int("##outline_thickness", Config.custom_crosshair_outline_thickness, 1, 5, "%d px")
            else:
                changed, Config.staticcrosshair = imgui.checkbox("Static crosshair", Config.staticcrosshair)
            
            # Crosshair colors
            crosshair_rgb = hex_to_rgb_f(Config.crosshaircolour)
            changed, crosshair_rgb = imgui.color_edit3("Crosshair colour", *crosshair_rgb)
            if changed:
                Config.crosshaircolour = rgb_f_to_hex(crosshair_rgb)
                
            crosshairoutline_rgb = hex_to_rgb_f(Config.crosshairoutlinecolour)
            changed, crosshairoutline_rgb = imgui.color_edit3("Crosshair outline colour", *crosshairoutline_rgb)
            if changed:
                Config.crosshairoutlinecolour = rgb_f_to_hex(crosshairoutline_rgb)
            
            # Crosshair hotkey
            imgui.text("Crosshair Toggle Hotkey:")
            imgui.text(f"Current: {Config.crosshair_hotkey.upper()}")
            
            if hotkey_mapping_active:
                imgui.text_colored("Press any key... (5s timeout)", 1.0, 1.0, 0.0, 1.0)
                if imgui.button("Cancel Mapping"):
                    hotkey_mapping_active = False
                    Config.waiting_for_hotkey = False
            else:
                if imgui.button("Map Hotkey"):
                    hotkey_mapping_active = True
                    Config.waiting_for_hotkey = True
                    hotkey_timeout = time.time()
                    status_text = "Press any key to set as crosshair toggle..."
                    
        imgui.tree_pop()
    
    # Other HUD elements
    if imgui.tree_node("Other HUD Elements"):
        changed, Config.overlaytoggle = imgui.checkbox("General overlay", Config.overlaytoggle)
        changed, Config.regentoggle = imgui.checkbox("Regen meter", Config.regentoggle)
        
        if Config.regentoggle:
            regen_rgb = hex_to_rgb_f(Config.overhealcolour)
            changed, regen_rgb = imgui.color_edit3("Regen colour", *regen_rgb)
            if changed:
                Config.overhealcolour = rgb_f_to_hex(regen_rgb)
                
            regenbg_rgb = hex_to_rgb_f(Config.regenbgcolour)
            changed, regenbg_rgb = imgui.color_edit3("Regen background", *regenbg_rgb)
            if changed:
                Config.regenbgcolour = rgb_f_to_hex(regenbg_rgb)
                
        changed, Config.skulltoggle = imgui.checkbox("Healthbar skull", Config.skulltoggle)
        
        # Font selection
        try:
            Config.current_font = fonts.index(Config.font)
        except ValueError:
            Config.font = "MS Shell Dlg 2"
            Config.current_font = fonts.index(Config.font)
            
        clicked, Config.current_font = imgui.combo("Font", Config.current_font, fonts, 30)
        Config.font = fonts[Config.current_font]
        
        if imgui.button("Recalibrate ammo colour"):
            Config.calibrated_ammo_colour = (0,0,0)
        
        imgui.spacing()
        if imgui.button("Find Config Folder"):
            OpenConfigFolder()
        imgui.tree_pop()

def draw_macros_section(imgui, overlay, status_text):
    """Draw macros section"""
    imgui.text("AFK Macro (F3=Pause, F4=Stop)")
    if imgui.button("Start AFK Routine"):
        overlay.assistant.StartAFK()
        status_text = "AFK: STARTED - F3=Pause F4=Stop"
    imgui.same_line()
    if imgui.button("Stop AFK"):
        overlay.assistant.StopAFK()
        status_text = "AFK: STOPPED"
    
    imgui.spacing()
    imgui.text("Travel BETA Macro (F2=Cancel, F5/F6=Steps)")
    changed, travel_tiles = imgui.slider_int("Tiles", overlay.assistant.travelTiles, 1, 10, "%d tiles")
    if changed:
        overlay.assistant.travelTiles = travel_tiles
        
    if imgui.button("Start Travel BETA"):
        overlay.assistant.StartTravelBeta(overlay.assistant.travelTiles)
        status_text = f"TRAVEL BETA: STARTED - {overlay.assistant.travelTiles} tiles"
    
    imgui.spacing()
    imgui.text(status_text)

def draw_graphics_section(imgui, status_text):
    """Draw graphics section"""
    imgui.text("Graphics Presets (Game must be closed)")
    
    if imgui.button("Potato Preset", width=-1):
        if ApplyGraphicsPreset("potato"):
            status_text = "Graphics: Potato preset applied"
        else:
            status_text = "Graphics: Failed (Game running?)"
    
    if imgui.button("Low Preset", width=-1):
        if ApplyGraphicsPreset("low"):
            status_text = "Graphics: Low preset applied"
        else:
            status_text = "Graphics: Failed (Game running?)"
    
    if imgui.button("Medium Preset", width=-1):
        if ApplyGraphicsPreset("medium"):
            status_text = "Graphics: Medium preset applied"
        else:
            status_text = "Graphics: Failed (Game running?)"
    
    if imgui.button("Revert to Default", width=-1):
        if RevertGraphicsSettings():
            status_text = "Graphics: Reverted to default"
        else:
            status_text = "Graphics: Failed to revert"
    
    imgui.spacing()
    imgui.text(status_text)

def update_testing_values(overlay):
    """Update testing values for UI preview"""
    overlay.current_hp = Config.hp_slider
    overlay.show_skull_red = Config.hp_slider <= Config.lowhealthvar
    overlay.show_skull_green = not overlay.show_skull_red
    overlay.health_num_text = f"{Config.healthprefix}{int(Config.hp_slider)}{Config.healthsuffix}"
    overlay.regen_extent = Config.regen_slider * 1.8
    overlay.regen_text = f"{Config.regenprefix}{int(Config.regen_slider)}{Config.regensuffix}"
    overlay.ammo_states = [False] * len(overlay.ammo_states)
    for i in range(5, 5 - Config.ammo_slider, -1):
        overlay.ammo_states[i] = True
    overlay.numberammo_text = f"{Config.ammoprefix}{Config.ammo_slider}{Config.ammosuffix}"

def ApplyGraphicsPreset(preset):
    """Apply graphics preset - placeholder function"""
    # This would contain the graphics preset logic
    return False

def RevertGraphicsSettings():
    """Revert graphics settings - placeholder function"""
    # This would contain the revert logic
    return False

def imgui_thread(overlay):
    anchor_grid = [
        ["nw", "n", "ne"],
        ["w", "x", "e"],
        ["sw", "s", "se"]
    ]
    
    if not glfw.init():
        print("Could not initialize GLFW")
        return

    # Create window
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
    
    screen_width, screen_height = get_dyn_x(2200), get_dyn_y(1400)
    window = glfw.create_window(screen_width, screen_height, "SoT HUD UI", None, None)

    glfw.make_context_current(window)
    
    # Window styling
    hwnd = glfw.get_win32_window(window)
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~(win32con.WS_BORDER | win32con.WS_THICKFRAME | win32con.WS_DLGFRAME | win32con.WS_CAPTION)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    
    exStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    exStyle &= ~win32con.WS_EX_APPWINDOW
    exStyle |= win32con.WS_EX_TOOLWINDOW
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exStyle)

    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                         win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    
    def set_clickthrough(hwnd, enabled: bool):
        exStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if enabled:
            exStyle |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        else:
            exStyle &= ~win32con.WS_EX_TRANSPARENT
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exStyle)
    
    # ImGui setup
    imgui.create_context()
    impl = GlfwRenderer(window, attach_callbacks=True)
    
    status_text = "Ready"
    hotkey_mapping_active = False
    hotkey_timeout = 0
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()
        
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)
        impl.process_inputs()
        imgui.new_frame()
        
        # Handle hotkey mapping timeout
        if hotkey_mapping_active and time.time() - hotkey_timeout > 5:
            hotkey_mapping_active = False
            Config.waiting_for_hotkey = False
            status_text = "Hotkey mapping timed out"
        
        if Config.show_UI:
            imgui.get_io().font_global_scale = 1.4
            imgui.begin("SoT HUD Enhanced", 
                       flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE |
                             imgui.WINDOW_NO_SCROLLBAR |
                             imgui.WINDOW_NO_COLLAPSE |
                             imgui.WINDOW_MENU_BAR)
            
            # Menu bar
            if imgui.begin_menu_bar():
                if imgui.begin_menu('File'):
                    changed, _ = imgui.menu_item('Export config', None, False, True)
                    if changed:
                        Config.popup = True
                    with imgui.begin_menu('Open Config', True) as open_recent_menu:
                        if open_recent_menu.opened:
                            configs_dir = os.path.join(script_dir, "YourConfigs")
                            if os.path.exists(configs_dir):
                                for file in os.listdir(configs_dir):
                                    if file.endswith('.zip'):
                                        changed, _ = imgui.menu_item(file, None, False, True)
                                        if changed:
                                            Config.load_config(os.path.join(configs_dir, file))
                    imgui.end_menu()
                imgui.end_menu_bar()
                
            # Export popup
            if Config.popup:
                imgui.open_popup("select-popup")
                Config.popup = False
                
            if imgui.begin_popup("select-popup"):
                imgui.text("Save config as:")
                _, Config.Name = imgui.input_text("##Name", Config.Name, 29)
                if imgui.button("Confirm"):
                    Config.save_config(True)
                    configs_dir = os.path.join(script_dir, "YourConfigs")
                    os.makedirs(configs_dir, exist_ok=True)
                    with zipfile.ZipFile(os.path.join(configs_dir, Config.Name+".zip"), 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                        for root, _, files in os.walk(os.path.join(script_dir, "Config")):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, os.path.join(script_dir, "Config"))
                                zip_ref.write(file_path, arcname)
                    imgui.close_current_popup()
                imgui.end_popup()
                
            imgui.begin_tab_bar("MainTabBar")
            
            # HUD Configuration Tab
            if imgui.begin_tab_item("HUD Config")[0]:
                draw_hud_config_section(imgui, anchor_grid, screen_width, status_text, hotkey_mapping_active, hotkey_timeout, overlay.fonts)
                imgui.end_tab_item()
            
            # Macros Tab
            if imgui.begin_tab_item("Macros")[0]:
                draw_macros_section(imgui, overlay, status_text)
                imgui.end_tab_item()
            
            # Graphics Tab
            if imgui.begin_tab_item("Graphics")[0]:
                draw_graphics_section(imgui, status_text)
                imgui.end_tab_item()
            
            imgui.end_tab_bar()
            
            # Update testing values
            update_testing_values(overlay)
            
            imgui.end()

        # Render
        imgui.render()
        set_clickthrough(hwnd, not Config.show_UI)
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
        glfw.wait_events_timeout(0.01)

    impl.shutdown()
    glfw.terminate()

# Hotkey detection
def detect_hotkey():
    while True:
        if Config.waiting_for_hotkey:
            try:
                event = keyboard.read_event(suppress=True)
                if event.event_type == keyboard.KEY_DOWN:
                    key_name = event.name
                    if len(key_name) <= 3 and key_name not in ['shift', 'ctrl', 'alt', 'windows']:
                        Config.crosshair_hotkey = key_name.lower()
                        Config.waiting_for_hotkey = False
                        Config.save_config(False)
                        print(f"Crosshair hotkey set to: {Config.crosshair_hotkey}")
            except Exception:
                pass
        time.sleep(0.1)

def main():    
    app = QtWidgets.QApplication(sys.argv)
    
    # Start background threads
    if WINDOWS_CAPTURE_AVAILABLE:
        threading.Thread(target=start_capture, daemon=True).start()
    
    threading.Thread(target=detect_hotkey, daemon=True).start()
    
    # Setup overlay
    screen_geom = app.primaryScreen().geometry()
    overlay = Overlay(screen_geom.width(), screen_geom.height())
    overlay.show()

    Config.load_from_file(config_path)
    overlay.set_click_through_native()
    
    threading.Thread(target=imgui_thread, args=(overlay,), daemon=True).start()
    
    # Global hotkeys
    keyboard.add_hotkey('delete', lambda: (
        print("Exiting..."),
        Config.save_config(False),
        overlay.config_watcher.stop(),
        QtCore.QCoreApplication.quit()
    ))
    
    keyboard.add_hotkey('insert', lambda: (
        setattr(Config, 'show_UI', not Config.show_UI),
        setattr(overlay, 'regen_extent', 0),
        setattr(overlay, 'regen_text', f"{Config.regenprefix}0{Config.regensuffix}")
    ))
    
    # AFK hotkeys
    keyboard.add_hotkey('f3', lambda: overlay.assistant.ToggleAFKPause() if overlay.assistant.afkActive else None)
    keyboard.add_hotkey('f4', lambda: overlay.assistant.StopAFK() if overlay.assistant.afkActive else None)
    
    # Travel cancel hotkey
    keyboard.add_hotkey('f2', lambda: overlay.assistant.StopTravel() if overlay.assistant.travelBetaActive else None)
    
    # Crosshair toggle hotkey
    def toggle_crosshair():
        Config.crosshairtoggle = not Config.crosshairtoggle
        Config.save_config(False)
    
    keyboard.add_hotkey(Config.crosshair_hotkey, toggle_crosshair)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()