#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本行输入器
使用方法：
1. 运行脚本后，会弹出一个窗口。
2. 在窗口中输入要发送的文本行，每行文本结束后按Enter键。
3. 可以使用热键（默认是Pause键）来启动或停止输入。
4. 可以在窗口中勾选“窗口置顶”、“去除文本前后空格”和“粘贴模式”选项来调整功能。
注意事项：
1. 请确保在运行脚本前，目标应用窗口已经激活。
2. 输入的文本行将直接发送到当前活动窗口，请注意不要在其他重要操作中使用此脚本。
3. 脚本默认使用Pause键作为热键，您可以根据需要在代码中修改。
依赖：
1. Python 3.x
2. tkinter 库（通常预装）
3. keyboard 库（可以使用 `pip install keyboard` 安装）
4. pyautogui 库（可以使用 `pip install pyautogui` 安装）
5. pyperclip 库（可以使用 `pip install pyperclip` 安装）
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import keyboard
import pyautogui
import pyperclip
import threading
import time

class TextLineInputter:
    def __init__(self, root):
        self.root = root
        self.root.title("文本行输入器")
        self.root.geometry("500x450")
        self.root.resizable(True, True)
        
        # 设置中文字体支持
        self.font = ("SimHei", 10)
        
        # 功能开关状态
        self.topmost = False  # 窗口置顶状态
        self.trim_whitespace = False  # 去除空格状态
        self.paste_mode = False  # 粘贴模式状态
        
        # 热键状态
        self.hotkey = 'pause'
        self.running = True
        
        # 上次输入内容
        self.last_input = ""
        
        # 创建UI元素
        self.create_widgets()
        
        # 启动热键监听线程
        self.hotkey_thread = threading.Thread(target=self.listen_hotkey, daemon=True)
        self.hotkey_thread.start()
        
        # 窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widgets(self):
        # 第一排选项框架
        options_frame1 = ttk.Frame(self.root)
        options_frame1.pack(padx=10, pady=5, fill=tk.X)
        
        # 窗口置顶复选框
        self.topmost_var = tk.BooleanVar(value=self.topmost)
        self.topmost_check = ttk.Checkbutton(
            options_frame1,
            text="窗口置顶",
            variable=self.topmost_var,
            command=self.toggle_topmost
        )
        self.topmost_check.pack(side=tk.LEFT, padx=5)
        
        # 去除前后空格复选框
        self.trim_var = tk.BooleanVar(value=self.trim_whitespace)
        self.trim_check = ttk.Checkbutton(
            options_frame1,
            text="去除文本前后空格",
            variable=self.trim_var,
            command=self.toggle_trim_whitespace
        )
        self.trim_check.pack(side=tk.LEFT, padx=5)
        
        # 第二排选项框架
        options_frame2 = ttk.Frame(self.root)
        options_frame2.pack(padx=10, fill=tk.X)
        
        # 粘贴模式复选框
        self.paste_var = tk.BooleanVar(value=self.paste_mode)
        self.paste_check = ttk.Checkbutton(
            options_frame2,
            text="粘贴模式（一次性输入）",
            variable=self.paste_var,
            command=self.toggle_paste_mode
        )
        self.paste_check.pack(side=tk.LEFT, padx=5)
        
        # 说明标签
        instructions = ttk.Label(
            self.root, 
            text=f"请在下方输入多行文本，按下 {self.hotkey.upper()} 键将输入并删除第一行内容",
            font=self.font,
            wraplength=480,
            justify="left"
        )
        instructions.pack(pady=5, padx=10, anchor="w")
        
        # 上次输入内容标签
        self.last_input_var = tk.StringVar()
        self.last_input_var.set("上次输入: 暂无")
        self.last_input_label = ttk.Label(
            self.root, 
            textvariable=self.last_input_var,
            font=self.font,
            foreground="gray",
            wraplength=480,
            justify="left"
        )
        self.last_input_label.pack(pady=5, padx=10, anchor="w")
        
        # 文本框
        self.text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=self.font,
            undo=True
        )
        self.text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # 状态标签
        self.status_var = tk.StringVar()
        self.status_var.set("就绪 - 请输入文本")
        self.status_label = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            font=self.font,
            foreground="blue",
            anchor="w"
        )
        self.status_label.pack(pady=10, padx=10, fill=tk.X)
    
    def toggle_topmost(self):
        """切换窗口置顶状态"""
        self.topmost = self.topmost_var.get()
        self.root.attributes("-topmost", self.topmost)
        status = "已开启窗口置顶" if self.topmost else "已关闭窗口置顶"
        self.status_var.set(status)
    
    def toggle_trim_whitespace(self):
        """切换去除前后空格状态"""
        self.trim_whitespace = self.trim_var.get()
        status = "已开启去除文本前后空格" if self.trim_whitespace else "已关闭去除文本前后空格"
        self.status_var.set(status)
        
    def toggle_paste_mode(self):
        """切换粘贴模式状态"""
        self.paste_mode = self.paste_var.get()
        status = "已开启粘贴模式" if self.paste_mode else "已关闭粘贴模式"
        self.status_var.set(status)
    
    def get_first_line(self):
        """获取并删除文本框中的第一行，根据设置决定是否去除空格"""
        # 获取文本内容
        content = self.text_area.get("1.0", tk.END).rstrip("\n")
        
        if not content:
            return None
        
        # 找到第一行的结尾
        first_line_end = content.find("\n")
        if first_line_end == -1:  # 只有一行
            first_line = content
            new_content = ""
        else:
            first_line = content[:first_line_end]
            new_content = content[first_line_end+1:]
        
        # 如果启用了去除空格选项，则处理当前行
        if self.trim_whitespace:
            first_line = first_line.strip()
        
        # 更新文本框内容
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", new_content)
        
        return first_line
    
    def input_first_line(self):
        """输入第一行内容到当前光标位置"""
        first_line = self.get_first_line()
        
        if first_line is None:
            self.root.after(0, lambda: messagebox.showinfo("提示", "没有更多文本行可输入"))
            self.status_var.set("没有更多文本行可输入")
            return
        
        # 根据模式选择输入方式
        if self.paste_mode:
            # 粘贴模式：使用剪贴板一次性粘贴
            old_clipboard = pyperclip.paste()  # 保存原有剪贴板内容
            pyperclip.copy(first_line)  # 设置新的剪贴板内容
            pyautogui.hotkey('ctrl', 'v')  # 模拟粘贴操作
            time.sleep(0.1)  # 等待粘贴完成
            pyperclip.copy(old_clipboard)  # 恢复原有剪贴板内容
        else:
            # 普通模式：逐字输入
            pyautogui.typewrite(first_line)
        
        display_text = first_line if len(first_line) <= 30 else first_line[:30] + "..."
        self.status_var.set(f"已输入: {display_text}")
        
        # 更新上次输入内容
        self.last_input = first_line
        last_input_display = first_line if len(first_line) <= 50 else first_line[:50] + "..."
        self.last_input_var.set(f"上次输入: {last_input_display}")
    
    def listen_hotkey(self):
        """监听热键的线程函数"""
        # 注册热键回调
        keyboard.add_hotkey(self.hotkey, self.on_hotkey_pressed)
        
        # 保持线程运行
        while self.running:
            time.sleep(0.1)
        
        # 清理热键
        keyboard.unhook_all()
    
    def on_hotkey_pressed(self):
        """热键被按下时的处理函数"""
        # 使用after确保在主线程中更新UI
        self.root.after(0, self.input_first_line)
    
    def on_close(self):
        """窗口关闭时的处理"""
        self.running = False
        self.root.destroy()

def main():
    # 检查是否安装了必要的库
    try:
        import keyboard
        import pyautogui
        import pyperclip
    except ImportError:
        print("请先安装所需库，执行以下命令：")
        print("pip install keyboard pyautogui pyperclip")
        return
    
    # 创建并运行主窗口
    root = tk.Tk()
    app = TextLineInputter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    
