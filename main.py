import re
import requests
import traceback
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from io import BytesIO
import webbrowser

stop_crawl = False


def download_pic(html, keyword, start_num, save_path, suffix, progress_var, total_images, progress_label):
    global stop_crawl
    headers = {'user-agent': 'Mozilla/5.0'}
    pic_urls = re.findall('"objURL":"(.*?)",', html, re.S)
    i = start_num
    success_count = 0
    subroot = os.path.join(save_path, keyword)
    txtpath = os.path.join(subroot, 'download_detail.txt')

    if not os.path.exists(subroot):
        os.makedirs(subroot)

    for each in pic_urls:
        if stop_crawl:
            break
        if success_count >= total_images:
            break
        a = f'图片 {i}, URL: {each}\n'
        print(f'正在下载 {a}')
        path = os.path.join(subroot, f'{i}.{suffix}')
        try:
            for attempt in range(3):  # 尝试下载3次
                try:
                    if not os.path.exists(path):
                        pic = requests.get(each, headers=headers, timeout=10)
                        img = Image.open(BytesIO(pic.content))  # 检查图片完整性
                        img.save(path)
                        with open(txtpath, 'a') as f:
                            f.write(a)
                        success_count += 1
                        progress = (success_count / total_images) * 100
                        progress_var.set(progress)
                        progress_label.config(text=f"{progress:.2f}%")
                        progress_bar.update()
                        i += 1
                        break  # 成功下载则跳出重试循环
                except Exception as e:
                    print(f'错误: 当前图片无法下载 {e}')
                    if attempt == 2:
                        print('多次尝试下载失败，跳过此图片')
                    time.sleep(0.2)  # 等待1秒后重试
        except:
            traceback.print_exc()
            print('错误: 当前图片无法保存')
            continue

    return success_count


def start_download():
    global stop_crawl
    stop_crawl = False
    keyword = entry_keyword.get().strip()
    save_path = entry_save_path.get().strip()
    num_images = int(entry_images.get().strip())
    frequency = int(entry_frequency.get().strip())
    suffix = combo_suffix.get().strip()
    start_num = int(entry_start_num.get().strip())

    if not keyword or not save_path or not suffix:
        messagebox.showerror("输入错误", "请填写所有字段")
        return

    headers = {'user-agent': 'Mozilla/5.0'}
    page_id = 0
    success_count = 0

    progress_var.set(0)
    progress_label.config(text="0%")
    progress_bar.update()

    while success_count < num_images and not stop_crawl:
        url = f'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word={keyword}&pn={page_id}&gsm=?&ct=&ic=0&lm=-1&width=0&height=0'
        page_id += 20
        html = requests.get(url, headers=headers).text
        success_count += download_pic(html, keyword, success_count + start_num, save_path, suffix, progress_var,
                                      num_images, progress_label)

        time.sleep(frequency)

    messagebox.showinfo("下载完成", f"关键词 '{keyword}' 的图片已下载完成")


def stop_download():
    global stop_crawl
    stop_crawl = True
    messagebox.showinfo("停止下载", "图片下载已手动停止")


def browse_save_path():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_save_path.delete(0, tk.END)
        entry_save_path.insert(0, folder_selected)


def open_save_path():
    path = entry_save_path.get().strip()
    if os.path.exists(path):
        webbrowser.open(path)
    else:
        messagebox.showerror("路径错误", "保存路径不存在")


# GUI Setup
root = tk.Tk()
root.title("图片下载器")
root.geometry("550x300")

style = ttk.Style()
style.configure("TButton", font=("Helvetica", 10))
style.configure("TLabel", font=("Helvetica", 10))
style.configure("TEntry", font=("Helvetica", 10))
style.configure("TCombobox", font=("Helvetica", 10))

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

frame.columnconfigure(1, weight=1)
frame.rowconfigure(7, weight=1)

ttk.Label(frame, text="关键词:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_keyword = ttk.Entry(frame, width=30)
entry_keyword.insert(0, "示例：猫")
entry_keyword.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(frame, text="保存路径:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_save_path = ttk.Entry(frame, width=30)
entry_save_path.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
ttk.Button(frame, text="浏览", command=browse_save_path).grid(row=1, column=2, padx=5, pady=5, sticky="ew")
ttk.Button(frame, text="打开", command=open_save_path).grid(row=1, column=3, padx=5, pady=5, sticky="ew")

ttk.Label(frame, text="爬取图片数量:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_images = ttk.Entry(frame, width=30)
entry_images.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(frame, text="爬取频率 (秒):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
entry_frequency = ttk.Entry(frame, width=30)
entry_frequency.insert(0, "1")
entry_frequency.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(frame, text="图片格式:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
combo_suffix = ttk.Combobox(frame, values=["jpg", "png", "jpeg"], state="readonly")
combo_suffix.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
combo_suffix.set("jpg")  # 默认值

ttk.Label(frame, text="起始编号:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
entry_start_num = ttk.Entry(frame, width=30)
entry_start_num.insert(0, "1")
entry_start_num.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

ttk.Button(frame, text="开始下载", command=start_download).grid(row=6, column=0, padx=5, pady=5, sticky="ew")
ttk.Button(frame, text="停止下载", command=stop_download).grid(row=6, column=1, padx=5, pady=5, sticky="ew")

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100)
progress_bar.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

progress_label = ttk.Label(frame, text="0%")
progress_label.grid(row=7, column=2, padx=5, pady=5, sticky="e")

root.mainloop()
