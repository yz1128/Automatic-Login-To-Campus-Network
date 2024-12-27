from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tkinter as tk
from tkinter import messagebox, filedialog
import time
import json
import os
import pywifi

CONFIG_FILE = 'login_config.json'


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None


def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def create_input_window(default_values=None):
    if default_values is None:
        default_values = {
            'driver_path': r"C:\Program Files\Google\Chrome\Application\chromedriver.exe",
            'username': "",
            'password': ""
        }

    window = tk.Tk()
    window.title("登录信息")
    window.geometry("400x200")

    # 创建主Frame
    main_frame = tk.Frame(window, padx=20, pady=10)
    main_frame.pack(expand=True, fill='both')

    # Chrome驱动路径选择框
    path_frame = tk.Frame(main_frame)
    path_frame.pack(fill='x', pady=(0, 10))

    tk.Label(path_frame, text="Chrome驱动路径:", width=15, anchor='w').pack(side='left')

    path_input_frame = tk.Frame(path_frame)
    path_input_frame.pack(side='left', fill='x', expand=True)

    driver_path = tk.Entry(path_input_frame, width=30)
    driver_path.insert(0, default_values.get('driver_path', ''))
    driver_path.pack(side='left', padx=(0, 5))

    def browse_file():
        filename = filedialog.askopenfilename(
            title="选择ChromeDriver文件",
            filetypes=[("ChromeDriver", "chromedriver.exe"), ("All files", "*.*")]
        )
        if filename:
            driver_path.delete(0, tk.END)
            driver_path.insert(0, filename)

    browse_button = tk.Button(path_input_frame, text="浏览", command=browse_file)
    browse_button.pack(side='left')

    # 用户名输入框
    username_frame = tk.Frame(main_frame)
    username_frame.pack(fill='x', pady=5)
    tk.Label(username_frame, text="用户名:", width=15, anchor='w').pack(side='left')
    username = tk.Entry(username_frame, width=30)
    username.insert(0, default_values.get('username', ''))
    username.pack(side='left')

    # 密码输入框
    password_frame = tk.Frame(main_frame)
    password_frame.pack(fill='x', pady=5)
    tk.Label(password_frame, text="密码:", width=15, anchor='w').pack(side='left')
    password = tk.Entry(password_frame, width=30, show="*")
    password.insert(0, default_values.get('password', ''))
    password.pack(side='left')

    # 添加保存配置的复选框
    checkbox_frame = tk.Frame(main_frame)
    checkbox_frame.pack(fill='x', pady=5)
    save_var = tk.BooleanVar(value=True)
    tk.Checkbutton(checkbox_frame, text="保存配置", variable=save_var).pack()

    def submit():
        window.user_input = {
            'driver_path': driver_path.get(),
            'username': username.get(),
            'password': password.get(),
            'save_config': save_var.get()
        }
        window.destroy()

    # 确定按钮
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill='x', pady=5)
    tk.Button(button_frame, text="确定", command=submit, width=10).pack()

    # 居中显示窗口
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    window.mainloop()
    return getattr(window, 'user_input', None)


def get_current_wifi():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(1)  # 给扫描结果一些时间
    results = iface.scan_results()
    for profile in results:
        if iface.status() == pywifi.const.IFACE_CONNECTED:
            return profile.ssid
    return None


def main():
    # 检查当前WiFi名称
    current_wifi = get_current_wifi()
    target_wifi = "TargetWiFi"  # 替换为目标WiFi名称

    if current_wifi != target_wifi:
        messagebox.showinfo("信息", f"当前未连接到目标WiFi（{target_wifi}），操作已取消。")
        return

    # 加载配置文件
    config = load_config()

    # 获取用户输入
    user_input = create_input_window(config)
    if not user_input:
        return

    # 如果用户选择保存配置
    if user_input.get('save_config'):
        save_config({
            'driver_path': user_input['driver_path'],
            'username': user_input['username'],
            'password': user_input['password']
        })

    options = Options()
    options.add_argument("--headless")  # 启用无头模式
    service = Service(user_input['driver_path'])

    try:
        driver = webdriver.Chrome(service=service, options=options)
        # 打开目标网页
        driver.get("http://192.168.0.170/")

        # 等待元素加载，最多等待10秒
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_input.send_keys(user_input['username'])

        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        password_input.send_keys(user_input['password'])

        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "login"))
        )
        submit_button.click()

        time.sleep(5)
    except Exception as e:
        messagebox.showerror("错误", str(e))
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
