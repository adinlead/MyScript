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
        self.root.geometry("550x450")
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
        
        # 更改热键按钮
        self.change_hotkey_btn = ttk.Button(
            options_frame2,
            text="更改热键",
            command=self.change_hotkey
        )
        self.change_hotkey_btn.pack(side=tk.LEFT, padx=5)
        
        # 说明标签
        self.instructions_var = tk.StringVar(value=f"请在下方输入多行文本，按下 {self.hotkey.upper()} 键将输入并删除第一行内容")
        instructions = ttk.Label(
            self.root, 
            textvariable=self.instructions_var,
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
    
    def change_hotkey(self):
        """更改热键的处理函数"""
        # 创建一个临时对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("更改热键")
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)  # 设置为主窗口的子窗口
        dialog.grab_set()  # 模态窗口
        dialog.attributes('-topmost', True)
        
        # 居中显示
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_width() // 2) - (width // 2) + self.root.winfo_x()
        y = (self.root.winfo_height() // 2) - (height // 2) + self.root.winfo_y()
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # 提示标签
        ttk.Label(
            dialog, 
            text="请按下您想要设置的新热键（单键）",
            font=self.font
        ).pack(pady=10, padx=10)
        
        # 当前热键标签
        current_hotkey_var = tk.StringVar(value=f"当前热键: {self.hotkey.upper()}")
        ttk.Label(
            dialog, 
            textvariable=current_hotkey_var,
            font=self.font,
            foreground="gray"
        ).pack(pady=5)
        
        # 新热键变量
        new_hotkey_var = tk.StringVar()
        
        def on_key_press(event):
            """处理按键事件"""
            # 只接受单个按键
            if event.char or len(event.keysym) == 1:
                new_hotkey = event.char.lower()
            else:
                new_hotkey = event.keysym.lower()
            
            if new_hotkey:
                new_hotkey_var.set(new_hotkey)
                # 更新对话框
                current_hotkey_var.set(f"新热键: {new_hotkey.upper()}")
                # 3秒后自动关闭
                dialog.after(1000, lambda: update_hotkey(new_hotkey))
        
        def update_hotkey(new_hotkey):
            """更新热键"""
            try:
                # 移除旧的热键监听
                keyboard.unhook_all()
                
                # 更新热键
                self.hotkey = new_hotkey
                
                # 重新注册热键
                keyboard.add_hotkey(self.hotkey, self.on_hotkey_pressed)
                
                # 更新说明标签
                self.instructions_var.set(f"请在下方输入多行文本，按下 {self.hotkey.upper()} 键将输入并删除第一行内容")
                
                # 显示成功消息
                self.status_var.set(f"热键已更改为: {self.hotkey.upper()}")
                
                # 关闭对话框
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"设置热键失败: {str(e)}")
        
        # 绑定按键事件
        dialog.bind("<Key>", on_key_press)
        
        # 提示用户按任意键
        dialog.focus_set()
    
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
    # 设置窗口图标（LOGO）
    try:
        import base64
        from io import BytesIO
        
        # 请将下面的 base64 编码替换为实际的 ico 文件的 base64 编码
        # 这里使用一个空的 base64 编码作为示例，实际使用时需要替换
        logo_base64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACxklEQVR4ASyTz29VVRDHPzPnthu1z7Zqfa9A33tSscadMdjCArQ2SDSA1cSiboyyIGKtP/4Nha0boxj/koYqMUiffa1xISxdFAhL2ntmmHNh3p3cmTnznZn7nfPUrPbasucc6rVb+NnN9/Oe17bvRep6z/dzHTn7j7V2s1A31+xGEmUt9VnTWb5Kh+Pd55vRI3ydZvlWuqxVL0QOOBkzx0XIDoFHpRiAxC8iXM7/UUTMIsOxiCuphHAUTQmiiERjF0NFGmgkOj8EWES4Yre4bLe54rf53m9FCRBJJB0JgJKiSEojYI6iQhFNFatVv5hclG7oDKva50vpoQhPtl9lvDvP071jTPSPE9w0uerZGoOcSU4AulTNsOG4h2UkDKkSqkpSafJFhHhKTJvAL71pfjrU5ucDU1yd6fBbt8PVXodfu9P8ONNmZGQUMwt1JAoVUB2+ukt0iU7hlG+rRkdJ1Qjm2owpolThE1kgFLGYtrxTnOmjmLD11C5brV2GY7tshv3P+D3+HrvD9vhdBk/8z7+tewwn7rPTutPklQJeCrjlpoam6EyFZSHGKpSQgljziHkiB+vJQGIytYpHYpEblyM+gPbNLab+2qIz2A57h+nBDu0bQzo3BhwIe+rPTZ6/OWRqc5v2YPgY76jqaEwQPJw8gr/xEvbWHLb0Cr40hy/OYScPYydejLM4Xwx9czbOXm4KiCS0kOPhensca7Xw6Q7+7CT54DQ2OY5PTuGdg9StMey5Q1inhz0zgREojQkKr0XXT62yfnaVjcULbLx9kesnPmf99BdcO3OJa0ufcv397/jjnQv8fuozNk5fomBiVWi2HP2JgFLFrkU04sGKOylIlDJkXN1y83KsOp5mzYJQRJOm+GfVLHyyzNEPzzB//hzHzi/z+kfLzK+c4+jKWRbCn195j4XQ4x8v89oH7/Jg70FsKvMQAAD//3zP/YoAAAAGSURBVAMAn39KP7AcP0MAAAAASUVORK5CYII="
        
        if logo_base64:
            # 将 base64 数据解码为字节流
            logo_data = base64.b64decode(logo_base64)
            # 使用 BytesIO 将字节流转换为类文件对象
            logo_stream = BytesIO(logo_data)
            # 创建 PhotoImage 对象（使用data参数直接传递二进制数据）
            logo = tk.PhotoImage(data=logo_data)
            # 设置窗口图标
            root.iconphoto(True, logo)
        else:
            print("警告：未提供图标Base64数据，将使用默认图标。")
    except Exception as e:
        print(f"设置窗口图标时出错：{str(e)}")
        
    app = TextLineInputter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    
