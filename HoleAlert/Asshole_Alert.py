import win32gui
import win32ui
import win32con
import win32process
import psutil
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
import cv2
import numpy as np
import time
import winsound as sd
import base64


#img, b64
image_A = "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"
image_B = "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"

def loadb64(string):
    imgbytes = base64.b64decode(string)
    arr = np.frombuffer(imgbytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img

def get_hwnd(process_name):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                proc = psutil.Process(pid)
                if process_name.lower() in proc.name().lower():
                    hwnds.append(hwnd)
            except psutil.NoSuchProcess:
                pass
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None


def capture_window(hwnd):
    try:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
        cDC.SelectObject(dataBitMap)

        cDC.BitBlt((0, 0), (width, height), dcObj, (0, 0), win32con.SRCCOPY)

        bmp_info = dataBitMap.GetInfo()
        bmp_bytes = dataBitMap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmp_info['bmWidth'], bmp_info['bmHeight']),
            bmp_bytes, 'raw', 'BGRX', 0, 1
        )

        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        h_max = 800
        w_max = 1600
        w, h = img.size
        if w >= h:
            if w > w_max:
                scale = w_max / w
                img = img.resize((w_max, int(h * scale)), Image.LANCZOS)
        else:
            if h > h_max:
                scale = h_max / h
                img = img.resize((int(w * scale), h_max), Image.LANCZOS)

        return img
    except Exception as e:
        print(f"capture failed : {e}")
        return None

def beepsound():
    fr = 2000   
    du = 500    
    sd.Beep(fr, du)

def ScanImage(base_img, imgpath, color, label):
    # 세팅
    mindist = 5
    threshold=0.8
    scales=np.linspace(0.2, 1.0, 10)
    saturation=1.5

    base_cv = cv2.cvtColor(np.array(base_img), cv2.COLOR_RGB2BGR)

    # 채도
    hsv = cv2.cvtColor(base_cv, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = np.clip(s.astype(np.float32) * saturation, 0, 255).astype(np.uint8)
    boosted = cv2.merge([h, s, v])
    base_cv = cv2.cvtColor(boosted, cv2.COLOR_HSV2BGR)

    template = loadb64(imgpath)
    if template is None:
        print(f"load failed : '{label}'")
        return []

    boxes = []

    def isexisting(x1, y1, x2, y2):
        for bx1, by1, bx2, by2, _, _ in boxes:
            if abs(bx1 - x1) < mindist and abs(by1 - y1) < mindist:
                return True
        return False

    for scale in scales:
        resized = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        th, tw = resized.shape[:2]

        if th > base_cv.shape[0] or tw > base_cv.shape[1]:
            continue

        result = cv2.matchTemplate(base_cv, resized, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)

        for pt in zip(*loc[::-1]):
            x1, y1 = pt
            x2, y2 = x1 + tw, y1 + th

            if not isexisting(x1, y1, x2, y2):
                boxes.append((x1, y1, x2, y2, color, label))
    if len(boxes) > 0 and color == "blue":
        beepsound()
    return boxes


class Scanner:
    def __init__(self, hwnd, templates):
        self.hwnd = hwnd
        self.templates = templates
        self.root = tk.Tk()
        self.root.title("게임이 너무 쉬우면 재미없습니다")

        self.label = tk.Label(self.root)
        self.label.pack()

        self.chkvar = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(self.root, text='bypass', variable=self.chkvar)
        chk.pack(anchor='w')

        self.update_frame()
        self.root.mainloop()

    def update_frame(self):
        img = capture_window(self.hwnd)
        if img and not self.chkvar.get():
            draw = ImageDraw.Draw(img)

            for template_path, color, label in self.templates:
                boxes = ScanImage(img, template_path, color, label)
                for box in boxes:
                    x1, y1, x2, y2, clr, label = box
                    draw.rectangle([x1, y1, x2, y2], outline=clr, width=3)

                    draw.text((x1 + 2, y1 - 15), label, fill=clr)

            self.tk_img = ImageTk.PhotoImage(img)
            self.label.configure(image=self.tk_img)

        self.root.after(1000, self.update_frame)


if __name__ == "__main__":
    hwnd = get_hwnd("MabinogiMobile.exe")
    if hwnd:
        templates = [
            (image_A, "red", "Default"),
            (image_B, "blue", "Detected")
        ]
        Scanner(hwnd, templates)
    else:
        print("Cannot find the process")
