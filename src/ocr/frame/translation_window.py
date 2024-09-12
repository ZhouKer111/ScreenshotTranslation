
import tkinter as tk
from tkinter import scrolledtext
import keyboard
from pynput import mouse
import numpy as np
from PIL import ImageGrab
from ocr.body_util import OcrContext,OcrBodyFactory
from ocr.util import TranslationUtil
from ocr.frame import ScreenWindow

class TranslationWindow:

    selection_languages = {
        "Chinese(Simplified)": "Chinese(Simplified)",
        "Chinese(Traditional)":'Chinese(Traditional)',
        "English": "English",
        "Japanese": "Japanese",
        "Korean": "Korean"
    }

    def __init__(self):
        # 创建窗口
        self.root = tk.Tk()
        self.root.title("Screen Translation")
        self.root.geometry("450x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.attributes("-topmost", True)
        
        # 初始化一些属性
        self.stop_flag = False
        self.ctrl_and_mouse_click = False
        self.is_selection_windows_init = False
        
        # 控件变量,以及监听变量变化
        self.manga_switch_var = tk.BooleanVar(value=False)
        self.source_language_var = tk.StringVar(value='English')
        self.source_language_var.trace_add("write", self.on_language_change)
        self.target_language_var = tk.StringVar(value='Chinese(Simplified)')

        # 初始化文本区域, 以及 底部按钮和语言选择 区域
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both', padx=5, pady=5)
        self.create_bottom_buttons()
        self.create_language_selection()
        
        # 初始化截图对象和ocr对象
        self.screen_windows = ScreenWindow(self.root)
        self.ocrbody = OcrBodyFactory.create_ocr_Body('easyocr', self.source_language_var.get())
        self.ocr_context = OcrContext(self.ocrbody)

        # 初始化鼠标监听器,以及热键监听, ctrl+shift+alt创建截图区域, esc退出截图区域
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click, on_move=self.on_mouse_move)
        self.mouse_listener.start()

        keyboard.add_hotkey('ctrl+shift+alt', self.create_selection_window)
        keyboard.add_hotkey('esc', self.on_closing_selection_window)
        
    def create_bottom_buttons(self):
        """
        创建清除文本按钮和漫画模式按钮
        """
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill='x', pady=5, side='bottom')
        
        self.switch_button = tk.Checkbutton(button_frame, text="Comic mode", variable=self.manga_switch_var, command=self.switch_changed)

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_text)
        self.clear_button.pack(side='left', padx=5)

    def create_language_selection(self):
        """
        创建源语言 以及 目标语言的选择
        """
        language_frame = tk.Frame(self.root)
        language_frame.pack(fill='x', pady=5, side='bottom')

        source_frame = tk.Frame(language_frame)
        source_frame.pack(side='left', padx=5, fill='y')

        self.source_label = tk.Label(source_frame, text="Source Language:")
        self.source_label.pack(anchor='w')

        self.source_menu = tk.OptionMenu(source_frame, self.source_language_var, *TranslationWindow.selection_languages.keys())
        self.source_menu.pack(anchor='w')

        target_frame = tk.Frame(language_frame)
        target_frame.pack(side='right', padx=5, fill='y')

        self.target_label = tk.Label(target_frame, text="Target Language:")
        self.target_label.pack(anchor='e')

        self.target_menu = tk.OptionMenu(target_frame, self.target_language_var, *TranslationWindow.selection_languages.keys())
        self.target_menu.pack(anchor='e')
    
    def on_mouse_click(self, x, y, button, pressed):
        """
        监听鼠标左键事件
        """
        # ctrl 加鼠标左键来选取截图范围区域
        if button == mouse.Button.left:
            if keyboard.is_pressed('ctrl') and pressed:
                if not self.is_selection_windows_init:
                    return
                self.x_start, self.y_start = x, y
                self.ctrl_and_mouse_click = True
                print(f'Init x_start:{self.x_start},y_start:{self.y_start}')
            else:
                if not self.ctrl_and_mouse_click:
                    return
                self.x_end, self.y_end = x, y
                self.ctrl_and_mouse_click = False
                self.screen_windows.selection_window_destroy()
                
                source_language_key = self.source_language_var.get()
                target_language_key = self.target_language_var.get()
                if source_language_key == target_language_key:
                    self.append_text("Don't choose the same language")
                    return
                
                ocr_text = self.get_ocr_text()
                translate_text = TranslationUtil.translate_text(ocr_text, source_language_key, target_language_key)
                self.append_text(f"[Source Text]: {ocr_text}")
                self.append_text(f"[Translated Text]: {translate_text}")
                
                self.x_start, self.y_start, self.x_end, self.y_end = None, None, None, None

    def get_ocr_text(self, languages = []):
        """
        得到ocr文本以及翻译文本进行展示
        """
        try:
            # 排序坐标, 截取选定区域
            self.x_start, self.x_end = sorted([self.x_start, self.x_end])
            self.y_start, self.y_end = sorted([self.y_start, self.y_end])
            
            screenshot = ImageGrab.grab(bbox=(self.x_start, self.y_start, self.x_end, self.y_end))
            # screenshot.show()
            screenshot_np = np.array(screenshot)
            
            text = self.ocr_context.get_ocr_text(screenshot_np)
            return text
        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {e}"
        
    def on_mouse_move(self, x, y):
        if self.ctrl_and_mouse_click:
            self.screen_windows.canvas_draw(self.x_start, self.y_start, x, y)
        
    def clear_text(self):
        self.text_area.delete(1.0, tk.END)

    def append_text(self, text):
        self.text_area.insert(tk.END, text + '\n\n')
        self.text_area.see(tk.END)
        
    def on_closing_selection_window(self):
        if self.screen_windows:
            self.screen_windows.selection_window_destroy()
            self.is_selection_windows_init = False
            
    def create_selection_window(self):
        self.screen_windows.create_selection_window()
        self.screen_windows.create_selection_canvas()
        self.is_selection_windows_init = True
        
    def on_language_change(self, *args):
        """
        源语言变化 监听
        """
        source_language = self.source_language_var.get()
        print(f"Soucre language change({source_language}).")
        
        # 如果是日文识别,提供manga ocr开关
        if source_language == 'Japanese':
            self.switch_button.pack(side='right', padx=5)
        else:
            # 隐藏复选框
            self.switch_button.pack_forget()
            self.manga_switch_var.set(False)
        
        self.ocrbody = OcrBodyFactory.create_ocr_Body('easyocr', source_language)
        self.ocr_context.set_body(self.ocrbody)
        
    def switch_changed(self):
        """
        日漫模式Comic mode 监听
        """
        is_checked = self.manga_switch_var.get()
        source_language = self.source_language_var.get()
        
        if source_language != 'Japanese' and is_checked:
            print(f"Comic mode only supports Japanese")
            return
            
        if not is_checked:
            self.ocrbody = OcrBodyFactory.create_ocr_Body('easyocr', source_language)
        else:
            self.ocrbody = OcrBodyFactory.create_ocr_Body('mangaocr', source_language)
        self.ocr_context.set_body(self.ocrbody)

    def on_closing(self):
        self.stop_flag = True
        self.on_closing_selection_window()
        self.mouse_listener.stop()
        self.root.destroy()
    
    def satrt(self):
        self.root.mainloop()