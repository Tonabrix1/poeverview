import tkinter as tk
char_width = 10
line_height = 20
alpha = .9
default_col = '#2D2A2E'
offx, offy = 0.025, .02

# monokai pro font
"""
bg              #2D2A2E
fg              #1D1F21
bright_black:   #727072
black:			#403E41
orange:  		#FC9867
red:     		#FF6188
green:   		#A9DC76
yellow:  		#FFD866
blue:    		#FC9867
magenta: 		#AB9DF2
cyan:    		#78DCE8
white:   		#FCFCFA
"""


class UI:
    def __init__(self, mpos, text, additional=[], color=default_col, text_col='#FCFCFA'):
        self.color = color
        self.text_col = text_col
        self.add_windows = {}
        grid = [x for x in text.splitlines() if x]
        root = tk.Tk()
        self.root = root
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.screen_width = screen_width
        self.screen_height = screen_height
        x = int(char_width*longest(grid)) + int(char_width*1.5)
        y = int(line_height*len(grid))

        pos_x, pos_y = mpos
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.right_side = pos_x > screen_width // 2
        self.top_side = pos_y > screen_height // 2
        if self.right_side: pos_x -= x
        if self.top_side: pos_y -= y

        
        
        root.configure(bg=color)
        self.size_x = x
        self.size_y = y
        root.geometry(f"{self.size_x}x{self.size_y}")
        root.geometry(f"+{pos_x}+{pos_y}")
        root.overrideredirect(True)
        root.wait_visibility(root)
        root.attributes('-alpha', alpha)
        l = tk.Label(root,text=text,font='sans-serif 12 bold',fg=text_col, anchor='center')
        l.configure(bg=color)
        l.pack(expand=True)
        root.after_idle(self.add_additionals,root, additional)
        root.mainloop()

    def add_additionals(self, root, additional):
        for add in additional:
            if add['type'] == 'window': self.new_window(root, add['name'],add['text'],add.get('color',self.color))

    def new_window(self, main, name, txt, color):
        win = tk.Toplevel(main)
        grid = [x for x in txt.splitlines() if x]

        x = int(char_width*longest(grid))
        y = int(line_height*len(grid))
        offset_y = -(self.size_y + y + 5) if self.top_side else (self.size_y + 5) #use the main window size to calculate the y offset
        window_sizes_x = sum(b['size'][0] for b in self.add_windows.values()) + 5 * len(self.add_windows)
        offset_x = -(window_sizes_x + x) if self.right_side else window_sizes_x
        self.add_windows[name] = {'root': win, 'size':(x,y)}
        if (new_pos:=x+self.pos_x+offset_x)<0 or new_pos>self.screen_width: 
            offset_y += -(t:=(self.tallest_window_size()+5)) if self.top_side else t
            offset_x = -x if self.right_side else 0
        win.configure(bg=color)
        win.geometry(f"{x}x{y}")
        win.geometry(f"+{self.pos_x+offset_x}+{self.pos_y+offset_y}")
        win.overrideredirect(True)
        win.wait_visibility(win)
        win.attributes('-alpha', alpha)
        l = tk.Label(win,text=txt,font='sans-serif 12 bold',fg=self.text_col,anchor='center')
        l.configure(bg=color)
        l.pack(expand=True)

    def tallest_window_size(self): return max(x['size'][1] for x in self.add_windows.values())

    #def destroy_window(self, name): self.add_windows[name]['root'].destroy()

def longest(grid): return max(len(line) for line in grid)
