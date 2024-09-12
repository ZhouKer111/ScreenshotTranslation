import pyautogui
import tkinter as tk

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