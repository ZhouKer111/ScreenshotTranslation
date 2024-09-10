import os
import keyboard
from PIL import ImageGrab, Image
import easyocr
import numpy as np
import tkinter as tk
from tkinter import scrolledtext
from paddleocr import PaddleOCR
import pyautogui
from pynput import mouse
import requests
from requests.exceptions import JSONDecodeError
from manga_ocr import MangaOcr


class TranslationWindow:
    # paddleocr_languages
    ocr_languages = {
        'English': 'en',
        'Chinese(Simplified)': 'ch',
        'Chinese(Traditional)': 'chinese_cht',
        'Japanese': 'japan',
        'Korean': 'korean',
    }
    selection_languages = {
        "Chinese(Simplified)": "Chinese(Simplified)",
        "Chinese(Traditional)":'Chinese(Traditional)',
        "English": "English",
        "Japanese": "Japanese",
        "Korean": "Korean"
    }
    translate_languages = {
        "English": "en",
        "Chinese(Simplified)": "zh-cn",
        "Chinese(Traditional)": "zh-tw",
        "French": "fr",
        "German": "de",
        "Japanese": "ja",
        "Korean": "ko",
        "Spanish": "es"
    }

    
    def __init__(self, root):
        # 创建窗口
        self.root = root
        self.root.title("Screen Translation")
        self.root.geometry("450x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
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
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both', padx=5, pady=5)
        self.create_bottom_buttons()
        self.create_language_selection()
        
        # 初始化截图对象和ocr对象
        self.screen_windows = ScreenWindow(root)
        self.ocrbody = OcrBody('paddle', TranslationWindow.ocr_languages['English'])

        # 初始化鼠标监听器,以及热键监听, ctrl+shift+alt创建截图区域, esc退出截图区域
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click, on_move=self.on_mouse_move)
        self.mouse_listener.start()

        keyboard.add_hotkey('ctrl+shift+alt', self.create_selection_window)
        keyboard.add_hotkey('esc', self.on_closing_selection_window)
        
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
        
        source_language = TranslationWindow.ocr_languages[source_language]
        self.ocrbody.set_ocr('paddle', source_language)
        
    def switch_changed(self):
        """
        日漫模式Comic mode 监听
        """
        is_checked = self.manga_switch_var.get()
        source_language = self.source_language_var.get()
        
        if source_language != 'Japanese' and is_checked:
            print(f"Comic mode only supports Japanese")
            return
        source_language = TranslationWindow.ocr_languages[source_language]
            
        if not is_checked:
            self.ocrbody.set_ocr('paddle', source_language)
        else:
            self.ocrbody.set_ocr('mangaocr', source_language)
             
    def clear_text(self):
        self.text_area.delete(1.0, tk.END)

    def append_text(self, text):
        self.text_area.insert(tk.END, text + '\n\n')
        self.text_area.see(tk.END)
        
    def on_closing_selection_window(self):
        if self.screen_windows:
            self.screen_windows.selection_window_destroy()
            self.is_selection_windows_init = False

    def on_closing(self):
        self.stop_flag = True
        self.on_closing_selection_window()
        self.mouse_listener.stop()
        self.root.destroy()

    def on_mouse_click(self, x, y, button, pressed):
        
        # ctrl 加鼠标左键来选取截图范围区域
        if button == mouse.Button.left and keyboard.is_pressed('ctrl'):

            if pressed:
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
                
                translate_source_language = TranslationWindow.translate_languages[source_language_key]
                translate_target_language = TranslationWindow.translate_languages[target_language_key]
                
                ocr_text = self.get_ocr_text()
                translate_text = self.translate_text(ocr_text, translate_source_language, translate_target_language)
                self.append_text(f"[Source Text]: {ocr_text}")
                self.append_text(f"[Translated Text]: {translate_text}")
                
                self.x_start, self.y_start, self.x_end, self.y_end = None, None, None, None
                
    def on_mouse_move(self, x, y):
        if self.ctrl_and_mouse_click:
            # print(f"Draw canvas: x_start:{self.x_start}, y_start:{self.y_start}")
            self.screen_windows.canvas_draw(self.x_start, self.y_start, x, y)
            
    def create_selection_window(self):
        self.screen_windows.create_selection_window()
        self.screen_windows.create_selection_canvas()
        self.is_selection_windows_init = True

    def get_ocr_text(self, languages = []):
        
        try:
            # 排序坐标, 截取选定区域
            self.x_start, self.x_end = sorted([self.x_start, self.x_end])
            self.y_start, self.y_end = sorted([self.y_start, self.y_end])
            
            screenshot = ImageGrab.grab(bbox=(self.x_start, self.y_start, self.x_end, self.y_end))
            # screenshot.show()
            screenshot_np = np.array(screenshot)
            
            text = self.ocrbody.get_ocr_text(screenshot_np)
            return text
        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {e}"

    def create_bottom_buttons(self):
        """
        创建清除文本按钮和漫画模式按钮, 并默认初始时置顶
        """
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill='x', pady=5, side='bottom')

        self.root.attributes("-topmost", True)
        
        self.switch_button = tk.Checkbutton(button_frame, text="Comic mode", variable=self.manga_switch_var, command=self.switch_changed)
        # self.switch_button.pack(side='right', padx=5)

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
    
    def translate_text(self, text, source_lang='',target_lang=''):
        """
        文本翻译,调用外部的翻译api
        """
        url = f"https://findmyip.net/api/translate.php?text={text}&source_lang={source_lang}&target_lang={target_lang}"
        response = requests.get(url)
        try:
            data = response.json()
            print(data)
            if response.status_code == 200:
                if data['code']== 200:
                    translation = data['data']['translate_result']
                    return translation
                elif data['code'] == 400:
                    return data['error']
                else:
                    return "Internal interface is incorrect, contact the developer"
            else:
                return "Internal interface is incorrect, contact the developer"    
        except JSONDecodeError as e:
                return f"JSON decoding error: {e}"
        except requests.RequestException as e:
                return f"Request error: {e}"
        
class ScreenWindow:
    
    def  __init__(self, tk_root):
        self.tk_root = tk_root
        self.selection_window = None
        self.canvas = None
        
    def create_selection_window(self):
        try:
            # 创建一个新的顶层窗口用于选择截图区域
            selection_window = tk.Toplevel(self.tk_root)
            selection_window.attributes('-fullscreen', True)
            selection_window.attributes('-alpha', 0.3)
            selection_window.configure(bg='gray')
            selection_window.overrideredirect(True)
            selection_window.attributes("-topmost", True)
            
            self.selection_window = selection_window
        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {e}"
            
    def create_selection_canvas(self):
        try:
            if not self.selection_window:
                raise Exception('Selection_window not exist.')
            
            screen_width, screen_height = pyautogui.size()
            canvas = tk.Canvas(self.selection_window, cursor='cross', width=screen_width, height=screen_height)
            canvas.pack(fill=tk.BOTH, expand=True)
            
            self.canvas = canvas
            # canvas.bind("<Button-1>", self.draw)
        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {e}"
        
    def canvas_draw(self, x_start, y_start, x_end, y_end):
        self.canvas.delete("selection")
        self.canvas.create_rectangle(x_start, y_start, x_end, y_end, outline='red', width=2, tags="selection")
        
    def selection_window_destroy(self):
        if self.selection_window:
            self.selection_window.destroy()
        self.selection_window = None
        self.canvas = None
    
    # def draw(self, event):
    #     """
    #     用来显示当前点击位置在canvas的坐标,用来比较
    #     """
    #     self.canvas.delete("all")
    #     x, y = event.x, event.y
    #     print(f"Canvas:({x},{y})")
    #     # 绘制一个十字表示点击位置
    #     self.canvas.create_line(x-10, y, x+10, y, fill="red")
    #     self.canvas.create_line(x, y-10, x, y+10, fill="red")
    #     # 显示坐标
    #     self.canvas.create_text(x, y, text=f"({x}, {y})", anchor="nw")
    
class OcrBody:
    
    def  __init__(self, ocr_type, languages):
        self.set_ocr(ocr_type, languages)
    
    def set_ocr(self, ocr_type, languages):
        """
        初始化ocr
        """
        self.ocr_type = ocr_type
        print(f"Set ocr language:[{languages}].")
        
        if ocr_type == 'mangaocr':
            self.ocr = MangaOcr()
        elif ocr_type == 'easyocr':
            self.ocr = easyocr.Reader(languages)
        elif ocr_type == 'paddle':
            self.ocr = PaddleOCR(use_angle_cls=True, lang=languages, max_text_length=1000)
        else:
            raise Exception('Unsupported ocr type.')
        
    def get_ocr_text(self, img, ocr_type=None):
        """
        返回识别文本
        """
        if not ocr_type:
            ocr_type = self.ocr_type

        if ocr_type == 'mangaocr':
            return self.get_manga_ocr_text(img)
        elif ocr_type == 'easyocr':
            return  self.get_easy_ocr_text(img)
        elif ocr_type == 'paddle':
            return self.get_paddle_ocr_text(img)
        else:
            raise Exception('Unsupported ocr type.')
        
    def get_paddle_ocr_text(self, img):
        """
        paddleocr识别
        """
        img = self.convert_img(img, 'ndarray')
        result = self.ocr.ocr(img, cls=True)
        texts = []
        for i in range(len(result[0])):
            texts.append(result[0][i][1][0]) 
            
        text = ' '.join([res for res in texts])
        print(f"Ocr text: {text}")
        return text
        
    def get_easy_ocr_text(self, img):
        """
        easyocr识别
        """
        img = self.convert_img(img, 'ndarray')
        result = self.ocr.readtext(img)
        text = ' '.join([res[1] for res in result])
        print(f"Ocr text: {text}")
        return text
    
    def get_manga_ocr_text(self, img):
        """
        日漫格式识别
        """
        img = self.convert_img(img, 'image')
        text = self.ocr(img)
        print(text)
        return text

    def convert_img(self, img, to_type):
        """
        转换图片格式
        """
        # 先将传进来得图片统一成Image
        if os.path.isfile(img):
            img = Image.open(img)
        elif isinstance(img, np.ndarray) and img.ndim == 3 and img.shape[2] in [3, 4]:
            img = Image.fromarray(img)
        elif isinstance(img, Image.Image):
            img = img
        else:
            print('Image not supported.')
            return None
        
        # 根据to_type转为所需要得图片格式
        match to_type:
            case 'image':
                return img
            case 'ndarray':
                img_np = np.array(img)
                return img_np
            case _:
                print(f'Can not convert to type:{to_type}.')
                return None
                
        
def main():
    root = tk.Tk()
    app = TranslationWindow(root)
    root.mainloop()
 
    
if __name__ == "__main__":
    main()
