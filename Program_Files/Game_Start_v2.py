from tkinter import *
import tkinter.messagebox as messagebox
from tkinter import filedialog
import webbrowser
import os
import sys
from pathlib import Path
from PIL import Image, ImageTk
import subprocess
import winreg
import threading
import utils
import ctypes
import ctypes.wintypes

def resource_path(relative_path):
    """获取资源的绝对路径，适用于开发和打包环境"""
    try:
        # PyInstaller创建临时文件夹并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发模式下，从当前文件所在目录开始构建路径
        base_path = Path(__file__).parent
    
    return os.path.join(base_path, relative_path)  

def text_copy(root, text):
    root.clipboard_clear()
    root.clipboard_append(text)

def get_installed_softwares():

    global Soft_list
    # 要扫描的注册表路径
    paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
    file = resource_path(cache_file)

    if os.path.isfile(file):
        try:
            cache = utils.load_config(path)
            name = cache["name"]
            path = cache["path"]
            Soft_list.append([name, path + "\launcher.exe"])
            return
        except:
            pass
    os.makedirs(resource_path(cache_path), exist_ok=True)
    for hive in hives:
        for path in paths:
            try:
                key = winreg.OpenKey(hive, path)
                for i in range(1024):  # 最多扫1024项，足够了
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)

                        # 读取信息
                        name = None
                        path = None

                        try: name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        except: pass
                        try: path = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                        except: pass

                        if name and path:
                            if name in ["原神","崩坏：星穹铁道"]:
                                Soft_list.append([name, path + "\launcher.exe"])
                                cache = {
                                    "name": name,
                                    "path": path
                                }
                                utils.save_config(cache, file)
                                subkey.Close()
                                key.Close()
                                return

                        subkey.Close()
                    except:
                        break
                key.Close()
            except:
                continue

def ensure_icon_dir():
    icon_dir = resource_path(pic_cache_path)
    if not os.path.exists(icon_dir):
        os.makedirs(icon_dir, exist_ok=True)
    return icon_dir

def extract_and_save_exe_icon(exe_path, size=40):
    try:
        icon_dir = ensure_icon_dir()
        exe_name = os.path.basename(exe_path).replace(".exe", "")
        save_path = os.path.join(icon_dir, f"{exe_name}.png")

        # 已经有图标了，直接返回
        if os.path.exists(save_path):
            return save_path

        user32 = ctypes.WinDLL("user32", use_last_error=True)
        shell32 = ctypes.WinDLL("shell32", use_last_error=True)
        gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

        hicon = shell32.ExtractIconW(None, exe_path, 0)
        if hicon <= 0:
            return None

        # 正确定义 Windows 句柄类型
        HANDLE = ctypes.c_void_p
        HICON = HANDLE
        HDC = HANDLE
        HBITMAP = HANDLE

        # ICONINFO 结构体
        class ICONINFO(ctypes.Structure):
            _fields_ = [
                ("fIcon", ctypes.wintypes.BOOL),
                ("xHotspot", ctypes.wintypes.DWORD),
                ("yHotspot", ctypes.wintypes.DWORD),
                ("hbmMask", HBITMAP),
                ("hbmColor", HBITMAP),
            ]

        # 提取图标
        hicon = shell32.ExtractIconW(None, exe_path, 0)
        if hicon <= 0:
            return None

        # 获取图标信息
        icon_info = ICONINFO()
        user32.GetIconInfo(hicon, ctypes.byref(icon_info))

        # 创建绘图环境
        hdc = user32.GetDC(None)
        mem_dc = gdi32.CreateCompatibleDC(hdc)
        h_bitmap = gdi32.CreateCompatibleBitmap(hdc, size, size)
        gdi32.SelectObject(mem_dc, h_bitmap)

        # 绘制图标到内存 DC
        user32.DrawIconEx(mem_dc, 0, 0, hicon, size, size, 0, None, 0x0003)

        # 读取像素数据
        buffer_size = size * size * 4
        buffer = ctypes.create_string_buffer(buffer_size)
        gdi32.GetBitmapBits(h_bitmap, buffer_size, buffer)

        # 转为 PIL 图像
        img = Image.frombuffer("RGBA", (size, size), buffer, "raw", "BGRA", 0, 1)
        img.save(save_path, "PNG")

        # 释放资源
        gdi32.DeleteDC(mem_dc)
        user32.ReleaseDC(None, hdc)
        user32.DestroyIcon(hicon)

        return save_path

    except Exception as e:
        print(f"提取失败：{e}")
        return None

def open_web(url):

    chrome_path = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
    webbrowser.get("chrome").open(url)

class background:

    def __init__(self, root):
        #标签实现
        self.root = root
        self.img_path = Bck_list
        self.index = 0
        self.lens = len(Bck_list)
        self.bg = Image.open(self.img_path[self.index])
        self.bg_photo = ImageTk.PhotoImage(self.bg)
        self.bg_label = Label(root, image=self.bg_photo)
        self.bg_label.place(x=60, y=0, relwidth=1, relheight=1)

    def Monitor(self):
        self.root.bind("<Configure>", self.on_configure)
        
    def on_configure(self, event):
 
        # 只处理【主窗口】【大小变化】
        if event.widget != self.root or event.width==200:
            return
        
        # 只响应大小变化，忽略移动
        if hasattr(self, 'last_size'):
            w, h = self.last_size
            if event.width == w and event.height == h:
                return
            
        self.last_size = (event.width, event.height)
        self.resize_background(event)

    def deal_pic(self, current_w, current_y, switch = None):
        if switch != None:
            self.bg = Image.open(self.img_path[self.index])
            self.bg1 = self.bg.resize((current_w, current_y), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg1)
        else:
            self.bg1 = self.bg.resize((current_w, current_y), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg1)
        self.root.after(0, self._update_ui)

    def _update_ui(self):

        self.bg_label.config(image=self.bg_photo)
        self.bg_label.place(x=60, y=0, relwidth=1, relheight=1)

    def resize_background(self, event):
        """窗口大小改变时，自动缩放背景图片"""
        # 只响应根窗口的大小变化
        window_w = event.width
        window_h = event.height
        # print(window_w, window_h)

        threading.Thread(target = self.deal_pic, args=(window_w, window_h), daemon=True).start()

    def update_bg(self):
            
        switch = 1
        self.index += 1
        self.index = self.index % self.lens
        current_w = self.root.winfo_width()
        current_h = self.root.winfo_height()
        
        threading.Thread(target= self.deal_pic, args=(current_w, current_h, switch), daemon=True).start()
    
class Mainmenu:

    def __init__(self, root):
        self.element = ""
        self.root = root
        self.u1 = StringVar()
        self.u2 = StringVar()
        self.u3 = StringVar()
        # self.mune = Menu(root)
        self.right_menu = Menu(root, tearoff=False)
        self.files()
        self.edit()

        #菜单实现
        self.right_menu.add_command(label="显示", command=self.browse, accelerator="Ctrl+H")
        self.right_menu.add_command(label="查找", command=self.find)
        self.right_menu.add_command(label="帮助", command=self.helps)
        self.KeyBind()
        self.root.bind("<Button-3>", self.show_right_menu)
        

    def show_right_menu(self, event):
        self.right_menu.tk_popup(event.x_root, event.y_root )
        pass

    def files(self):
        filemenu = Menu(self.right_menu, tearoff=False)
        self.right_menu.add_cascade(label="文件", menu=filemenu)
        filemenu.add_command(label="添加", command=self.helps, accelerator="Ctrl+N")
        filemenu.add_command(label="打开", command=self.helps, accelerator="Ctrl+O")
        filemenu.add_command(label="保存", command=self.helps, accelerator="Ctrl+S")

    def edit(self):
        edit = Menu(self.right_menu, tearoff=False)
        self.right_menu.add_cascade (label="编辑", menu=edit)
        edit.add_command(label="剪切", command=self.helps, accelerator="Ctrl+X")
        edit.add_command(label="复制", command=self.helps, accelerator="Ctrl+C")
        edit.add_command(label="粘贴", command=self.helps, accelerator="Ctrl+V")

    def child_window(self, title, scale):
        child_window = Toplevel()
        child_window.title(title)
        child_window.iconbitmap(resource_path(icon_path))
        child_window.geometry(scale)
        child_window.update()
        child_window.attributes("-topmost", True)
        child_window.grab_set()

        return child_window

    def helps(self):
        messagebox.showinfo("周总劝学", "你丫，好好学习吧。")

    #显示快速查询表
    def browse(self):
        browse_win = self.child_window("浏览", f'150x200+{int(scr_width/2.2)}+{int(scr_height/2.5)}')
        browse = Text(browse_win, width=30, height=15)
        browse.pack()
        browse.insert(INSERT, "快速查找对应表:\n")
        for message in Message_list:
            # print(message)
            temp = message[0] + " <---> " +  message[1] + "\n"
            browse.insert(INSERT, temp)
            print(*message)

    #查找功能实现
    def find(self):
        find_win = self.child_window("查找", '250x50+500+400')
        label = Label(find_win, text="输入序号或名字")
        label.grid(row=1,column=0)
        entry = Entry(find_win, textvariable=self.u1)
        entry.grid(row=1,column=1)
        self.element = self.u1.get()
        button = Button(find_win, text="查找", command=self.inner_query)
        button.grid(row=2,column=1)

    #查询角色对应链接
    def inner_query(self):
        query_win = self.child_window("提示", f'400x80+{int(scr_width/2.2)}+{int(scr_height/2.5)}')
        sign = -1
        for row in Message_list:
            if self.u1.get() in row:
                sign = Message_list.index(row)
                break

        if sign != -1:
            Character = People[sign]
            Character.All_message()
            Msg_Info = Text(query_win, width=50, height=2)
            Msg_Info.pack()
            Msg_Info.insert(INSERT, "B站地址:\n" + Character.Pv_url)
            Msg_Info.configure(state='disabled')
            open_button = Button(query_win, text="打开", command=Character.PV_Play)
            open_button.place(x=0, y=0, relx=0.35, rely=0.5)
            copy_button = Button(query_win, text="复制", command=lambda:text_copy(query_win, Character.Pv_url))
            copy_button.place(x=0, y=0, relx=0.55, rely=0.5)

        else:
            messagebox.showinfo("提示！","未找到相应的角色!请重新输入\n")

    #绑定快捷键
    def KeyBind(self):
        root_window.bind("<Control-H>", lambda e:self.browse())
        root_window.bind("<Control-h>", lambda e:self.browse())
        root_window.bind("<Control-N>", lambda e:self.helps())    
        root_window.bind("<Control-n>", lambda e:self.helps())
        root_window.bind("<Control-O>", lambda e:self.helps())
        root_window.bind("<Control-o>", lambda e:self.helps())
        root_window.bind("<Control-S>", lambda e:self.helps())    
        root_window.bind("<Control-s>", lambda e:self.helps())
        root_window.bind("<Control-X>", lambda e:self.helps())    
        root_window.bind("<Control-x>", lambda e:self.helps())
        root_window.bind("<Control-C>", lambda e:self.helps())
        root_window.bind("<Control-c>", lambda e:self.helps())
        root_window.bind("<Control-V>", lambda e:self.helps())    
        root_window.bind("<Control-v>", lambda e:self.helps())

class down_frame:
    def __init__(self, root):
        self.botton_frame = Frame(root, width=60, height=40, bd =1)
        # self.botton_frame.pack(side="bottom", fill="x", padx=(60, 0), pady=(1, 1))
        # self.bottom_frame.lift()

class buttons:
    def __init__(self, root, arr):
        self.index = int(arr[0])
        self.button = Button(root.botton_frame, text=arr[1],  bg="#FCBB08", command=self.action)
        self.button.pack(side="left", fill="x", expand=True)

    def action(self):
        Character = People[self.index - 1]
        Character.All_message()
        Character.PV_Play()

class WenFaLuoSi:

    def __init__(self, site):
        self.Site = site

class person(WenFaLuoSi):

    def __init__(self, site, name, power, sex, Destiny, url):
        WenFaLuoSi.__init__(self, site)
        self.Name = name
        self.Power = power
        self.Sex = sex
        self.Destiny = Destiny
        self.Pv_url = url

    def All_message(self):
        print("归属：{}, 黄金裔姓名：{}, 权能：{}, 性别：{}, 命途：{}".format(self.Site, self.Name, self.Power, self.Sex, self.Destiny))
        # print(f"出生地：{self.site}, 黄金裔姓名：{self.name}, 权能：{self.power}, 性别：{self.sex}, 生日：{self.birthday}")

    def PV_Play(self):

        threading.Thread(target=open_web, args=(self.Pv_url.strip(), ), daemon=True).start()

class side_frame:
    def __init__(self, root):
        self.frame = Frame(root, bg='pink', width=60)
        self.frame.place(x=0, y=0,relheight=1)
        self.bg_label = Label(self.frame, bg="#00B7FF")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

class win_frame:
    def __init__(self, root):
        self.root = root
        self.pic_path = Win_piclist
        self.index = 0
        self.lens = len(Win_piclist)
        self.ORG_W = 224
        self.ORG_H = 126
        self.button_frame = down_frame(root)
        self.frame = Frame(root, bg='pink', width=224, height=126)
        self.frame.place(x=80, rely=1, y=-35, anchor="sw" )   # "sw"左下角对齐  y=-20 距离底部距离  rely=1 贴底部
        self.bg = Image.open(self.pic_path[self.index])
        self.bg = self.bg.resize((self.ORG_W, self.ORG_H), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg)
        self.bg_label = Label(self.frame, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.bind("<ButtonRelease-1>", self.label_click_l)
        self.bg_label.bind("<Button-3>", self.label_click_r)

        self.right_menu = Menu(self.root, tearoff=False)
        # 添加菜单项
        self.right_menu.add_command(label="切换图片", command=self.switch_pic)
        self.right_menu.add_command(label="显示按钮", command=self.show_button)
        self.right_menu.add_command(label="关闭按钮", command=self.close_show_button)
        self.auto_run(5000)

    def deal_pic(self, current_w, current_y):

        self.bg = Image.open(self.pic_path[self.index])
        self.bg = self.bg.resize((current_w, current_y), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg)
        self.root.after(0, self._update_pic)

    def _update_pic(self):

        self.bg_label.config(image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def switch_pic(self):

        self.index += 1
        self.index = self.index % self.lens
        threading.Thread(target= self.deal_pic, args=(self.ORG_W, self.ORG_H), daemon=True).start()

    def auto_run(self, ms):
        self.switch_pic()  # 先执行一次
        # 然后每隔 ms 再次调用自己
        self.root.after(ms, lambda: self.auto_run(ms))

    def label_click_l(self, event):
        threading.Thread(target=open_web, args=(resource_path(web_file), ), daemon=True).start()
        pass

    def label_click_r(self, event):
        self.right_menu.tk_popup(event.x_root, event.y_root )
        return "break"
        
    def show_button(self):
        self.button_frame.botton_frame.pack()
        pass

    def close_show_button(self):
        self.button_frame.botton_frame.pack_forget()
        pass

class StartGameButton:
    """自定义开始游戏按钮"""
    def __init__(self, root, path=None, pic_path = None, count = None):
        global index
        self.u1 = StringVar()
        self.num = index
        self.root = root.frame
        self.path = path
        self.pic_path = pic_path
        self.ORG_SIZE = 40
        self.count = count
        self.base_x = 10
        self.base_y = 10 + index * 50
        self.canvas = Canvas(self.root, width=self.ORG_SIZE, height=self.ORG_SIZE, highlightthickness=0)
        self.canvas.place(x=self.base_x, y=self.base_y)
        self.bg1 = Image.open(pic_path)
        self.bg2 = self.bg1.resize((self.ORG_SIZE, self.ORG_SIZE), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg2)
        self.ico = self.canvas.create_image(0, 0, anchor=NW, image=self.bg_photo)
        self.right_menu = Menu(self.root, tearoff=False)
        self.right_menu.add_command(label="更改图标", command=self.switch_ico)
        self.right_menu.add_command(label="删除游戏", command=self.delete_game)
        self.right_menu.add_command(label="恢复默认图标", command=self.recovery_pic)
        index += 1
        self.bind()

    def bind(self):
        self.canvas.tag_bind(self.ico, "<ButtonPress-1>", self._on_click_l)
        self.canvas.tag_bind(self.ico, "<ButtonRelease-1>", self._up_click_l)
        self.canvas.bind("<ButtonPress-3>", self._on_click_r)
        self.canvas.bind("<ButtonRelease-3>", self._up_click_r)
        
    def recovery_pic(self):
        if self.num == 0:
            return
        def task():
            content = utils.load_config(resource_path(data_file))
            pic_path = content["games"][self.num - 1]["pic_path"]
            self.bg1 = Image.open(pic_path)
            self.bg2 = self.bg1.resize((self.ORG_SIZE, self.ORG_SIZE), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg2)
            self.root.after(0, self._update_pic)
            self.file_revise(default_pic = 1)
            
        threading.Thread(target= task, daemon=True).start()

    def file_revise(self, default_pic= None):
        content = utils.load_config(resource_path(data_file))
        if default_pic != None:
            content["games"][self.num - 1]["default"] = 1
            utils.save_config(content, resource_path(data_file))
            return
        
        content["games"][self.num - 1]["self_path"] = self.pic_path
        content["games"][self.num - 1]["default"] = 2
        utils.save_config(content, resource_path(data_file))

    def child_window(self, title, scale):
        child_window = Toplevel()
        child_window.title(title)
        child_window.iconbitmap(resource_path(icon_path))
        child_window.geometry(scale)
        child_window.update()
        child_window.attributes("-topmost", True)
        child_window.grab_set()

        return child_window
    
    def deal_pic(self):
        def task():
            self.pic_path = self.u1.get().strip()
            self.bg1 = Image.open(self.pic_path)
            self.bg2 = self.bg1.resize((self.ORG_SIZE, self.ORG_SIZE), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg2)
            self.root.after(0, self._update_pic)
            self.file_revise()

        threading.Thread(target= task, daemon=True).start()

    def _update_pic(self):
        self.canvas.itemconfig(self.ico, image=self.bg_photo)
        
    def switch_ico(self):
        if self.num == 0:
            messagebox.showinfo("提示", "默认启动器不可删修改!")
            return "break"
        insert_win = self.child_window("选择文件", f'250x70+{int(scr_width/2.2)}+{int(scr_height/2.5)}')
        label1 = Label(insert_win, text="输入路径")
        label1.grid(row=1,column=0)

        entry1 = Entry(insert_win, textvariable=self.u1)
        entry1.grid(row=1,column=1)

        button1 = Button(insert_win, text="浏览", command=self.select_ico)
        button1.grid(row=1,column=2)
        
        button2 = Button(insert_win, text="确定更改", command=self.deal_pic)
        button2.grid(row=2,column=1)

    def delete_game(self):
        global index
        if self.num == 0:
            messagebox.showinfo("提示", "默认启动器不可删除!")
            return 
        
        self.canvas.delete("all")    # 清空画布内容
        self.canvas.destroy()        # 销毁画布
        self.bg_photo = None          # 清空图片（杜绝残影）
        self.bg1 = None
        self.bg2 = None
        del Starbtn[self.num]
        try:
            content = utils.load_config(resource_path(data_file))
            del content["games"][self.num - 1]
            utils.save_config(content, resource_path(data_file))

        except Exception as e:
            messagebox.showerror("文件操作错误", f"删除按钮失败：{str(e)}")

        for i in range(self.num, len(Starbtn)):
                Starbtn[i].num = i
                Starbtn[i].base_y = 10 + 50*i
                Starbtn[i].canvas.place(x=Starbtn[i].base_x , y=Starbtn[i].base_y)
        index -=1

        return "break"

    def cartoon(self, size):

        # 尺寸
        self.canvas.config(width=size, height=size)
        self.bg2 = self.bg1.resize((size, size), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg2)
        self.canvas.itemconfig(self.ico, image=self.bg_photo)
        # 居中偏移（临时计算，不破坏原始位置）
        offset = (self.ORG_SIZE - size) // 2
        self.canvas.place(x=self.base_x + offset, y=self.base_y + offset)

    def _on_click_l(self, event):
        self.cartoon(36)

    def _up_click_l(self, event):
        if self.count == None:
            print("正在启动游戏")
            def start_game():
                subprocess.Popen(self.path)
            threading.Thread(target=start_game, daemon=True).start()

        else:
            print("未发现米哈游启动器,正在跳转网站下载")
            def open_url():
                subprocess.Popen([self.path, "https://launcher.mihoyo.com/"])
            threading.Thread(target=open_url, daemon=True).start()
        self.cartoon(40)

    def _on_click_r(self, event):
        self.cartoon(36)
        return "break"

    def _up_click_r(self, event):
        self.cartoon(40)
        self.right_menu.tk_popup(event.x_root, event.y_root)
        return "break"
    # 选择图标路径
    def select_ico(self):
        path = filedialog.askopenfilename(title="选择图标", filetypes=[("图片文件", "*.png;*.jpg;*.ico")])
        if path:
            self.u1.set(path)
        
class insert_button:
    def __init__(self, root, pic_path = None):

        self.root = root.frame
        self.ORG_SIZE = 40
        self.base_x = 10
        self.base_y = -75
        self.u1 = StringVar()
        self.canvas = Canvas(self.root, width=self.ORG_SIZE, height=self.ORG_SIZE, highlightthickness=0)
        self.canvas.place(x=self.base_x, rely=1, y=self.base_y)
        self.bg1 = Image.open(pic_path)
        self.bg2 = self.bg1.resize((self.ORG_SIZE, self.ORG_SIZE), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg2)
        self.ico = self.canvas.create_image(0, 0, anchor=NW, image=self.bg_photo)
        self.canvas.tag_bind(self.ico, "<ButtonPress-1>", self._on_click_l)  #绑定左键按下的事件
        self.canvas.tag_bind(self.ico, "<ButtonRelease-1>", self._up_click_l) #绑定左键释放的事件

    def child_window(self, title, scale):
        child_window = Toplevel()
        child_window.title(title)
        child_window.iconbitmap(resource_path(icon_path))
        child_window.geometry(scale)
        child_window.update()
        child_window.attributes("-topmost", True)
        child_window.grab_set()

        return child_window

    def cartoon(self, size):
        #实现图标动画
        self.canvas.config(width=size, height=size)
        self.bg2 = self.bg1.resize((size, size), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg2)
        self.canvas.itemconfig(self.ico, image=self.bg_photo)
        # 居中偏移（临时计算，不破坏原始位置）
        offset = (self.ORG_SIZE - size) // 2
        self.canvas.place(x=self.base_x + offset, y=self.base_y + offset)

    def _on_click_l(self, event):
        self.cartoon(36)

    def _up_click_l(self, event):

        insert_win = self.child_window("添加程序", f'250x70+{int(scr_width/2.2)}+{int(scr_height/2.5)}')
        label1 = Label(insert_win, text="输入路径")
        label1.grid(row=1,column=0)

        entry1 = Entry(insert_win, textvariable=self.u1)
        entry1.grid(row=1,column=1)

        button1 = Button(insert_win, text="浏览", command=self.select_path)
        button1.grid(row=1,column=2)
        
        button2 = Button(insert_win, text="确定添加", command=self.insert_game)
        button2.grid(row=2,column=1)
        self.cartoon(40)
        
    # 选择文件路径
    def select_path(self):
        path = filedialog.askopenfilename(title="选择程序路径", filetypes=[("应用程序", "*.exe")])

        if path:
            self.u1.set(path)

    def insert_game(self):

        Path = self.u1.get()
        Pic_path = extract_and_save_exe_icon(Path, size=40)
        if not Pic_path:
            Pic_path = resource_path(pic_path)
            print("图标提取失败，使用默认图标")
        if Path[-4:].lower() == ".exe" and Pic_path[-4:].lower() in [".png", ".jpg", ".jpeg", ".gif"]:
            def save_file():
                Starbtn.append(StartGameButton(game_fram, path=Path, pic_path=Pic_path))
                content = utils.load_config(resource_path(data_file))
                content["games"].append({"path": Path, "pic_path": Pic_path, "self_path": "", "default": 1})
                utils.save_config(content, resource_path(data_file))
            threading.Thread(target=save_file, daemon=True).start()
        else:
            messagebox.showinfo("提示！","非法路径!请重新输入\n")

def Initial():
    global People 
    global Message_list
    global Bck_list
    
    with open(resource_path(os.path.join(start_rail_path,"roal_message.txt")), "r", encoding="UTF-8") as f1:  # 打开文件
        f1.seek(0)
        Content_Character = f1.readlines()
    with open(resource_path(os.path.join(start_rail_path,"url.txt")), "r", encoding="UTF-8") as f2:  # 打开文件
        f2.seek(0)
        Content_pv_url = f2.readlines()
    for line, url in zip(Content_Character, Content_pv_url):
        line = line.strip("1234567890,").split(",")
        url = url.strip("1234567890.")
        People.append(person(line[0], line[1], line[2], line[3], line[4], url))
    f1.close()
    f2.close()
    i = 1

    for Character in People:
        Message_list.append([str(i), Character.Name])
        i += 1
    
    for file_name in os.listdir(resource_path(background_dir)): 
        if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')): 
            Bck_list.append(os.path.join(resource_path(background_dir), file_name))

    for file_name in os.listdir(resource_path(win_pic_path)): 
        if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')): 
            Win_piclist.append(os.path.join(resource_path(win_pic_path), file_name))

def init_file_or_dir(path: str):
    global Starbtn
    """
    初始化文件/文件夹
    :param path: 路径
    :param is_dir: 是否是文件夹,True=文件夹,False=文件）
    """
    try:
        
        if not os.path.exists(path):
            # os.makedirs(cache_path, exist_ok=True)
            content = utils.load_config(path)

        else :
            content = utils.load_config(path)
            for game in content["games"]:

                paths = game["path"]
                pic_path = game["pic_path"]
                self_path = game["self_path"]
                
                if game["default"] == 1 :
                    Starbtn.append(StartGameButton(game_fram, path=paths, pic_path=pic_path))
                else:
                    Starbtn.append(StartGameButton(game_fram, path=paths, pic_path=self_path))
                pass

    except Exception as e:
        messagebox.showerror("初始化错误", f"无法创建/读取 {path}\n错误:{str(e)}")

def win_initial(root):
    global scr_width 
    global scr_height 
    win_width = cfg["Window"]["win_width"]   # 窗口宽度
    win_height = cfg["Window"]["win_height"]   # 窗口高度
    scr_width = root_window.winfo_screenwidth()   # 屏幕宽
    scr_height = root_window.winfo_screenheight() # 屏幕高
    x = int((scr_width - win_width) / 2)
    y = int((scr_height - win_height) / 2)
    root_window.title("Game Start")
    root_window.iconbitmap(resource_path(icon_path))
    root_window.geometry(f'{win_width}x{win_height}+{x}+{y}')

    # root_window.resizable(False,False)
    # root_window.attributes('-alpha', 0.8)

cfg = utils.load_config()
edge_path = cfg["Path"]["edge_path"]
win_pic_path = cfg["Path"]["win_pic_path"]
background_dir = cfg["Path"]["background_dir"]
start_rail_path = cfg["Path"]["start_rail_path"]
pic_cache_path = cfg["Path"]["pic_cache_path"]
cache_path = cfg["Path"]["cache_path"]

icon_path = cfg["File_Path"]["icon_file"]
pic_path = cfg["File_Path"]["pic_file"]
insert_ico = cfg["File_Path"]["insert_file"]
cache_file = cfg["File_Path"]["cache_file"]
data_file = cfg["File_Path"]["data_file"]
web_file = cfg["File_Path"]["web_file"]

scr_width = 0 
scr_height = 0
button_list = []
Starbtn = []
People = []
Message_list = []
Win_piclist = []
Bck_list = []
Soft_list = []
index = 0

if __name__=="__main__":
    print(cfg["Helps"])
    Initial() #载入文件资源
    #扫描注册表，获取默认启动器，未扫描到则指向下载地址
    threading.Thread(target=get_installed_softwares, daemon=True).start()
    #根窗口创建
    root_window = Tk()
    # 主界面的背景
    bg = background(root_window)
    # 主界面右键菜单/可注释掉
    Right_menu = Mainmenu(root_window)
    #控件-支撑左侧游戏按钮的基础框架
    game_fram = side_frame(root_window)
    #主界面左下角小窗口
    Win_frame = win_frame(root_window)
    #创建角色按钮，需要在小窗口右键显示按钮方可出现
    for Character in Message_list:
        button_list.append(buttons(Win_frame.button_frame, Character))
    #切换背景按钮
    background_button = Button(game_fram.frame, text="更换背景", bg="#08AFFC", command=bg.update_bg, highlightthickness=1).pack(side="bottom", padx=1)
    # 创建游戏初始按钮，继承game_fram
    if len(Soft_list) != 0:
        Starbtn.append(StartGameButton(game_fram, path=Soft_list[0][1], pic_path=resource_path(pic_path)))
    else:
        Starbtn.append(StartGameButton(game_fram, path=edge_path, pic_path=resource_path(pic_path), count=0))

    Insert_button = insert_button(game_fram, pic_path=resource_path(insert_ico))
    init_file_or_dir(resource_path(data_file))
    bg.Monitor()
    win_initial(root_window)
    
    root_window.mainloop()