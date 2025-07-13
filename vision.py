import os
import io
import base64
import random
import datetime
import time
from PIL import Image
import pyautogui
import cv2
import numpy as np
import win32gui
import win32ui
import win32con
from openai import OpenAI

client = OpenAI()
CACHE_DIR = "button_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def capture_screen(window_name="마비노기 모바일"):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd == 0:
        raise Exception(f"[❌] 창 '{window_name}'을 찾을 수 없습니다.")

    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width = right - left
    height = bottom - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), width, height, mfcDC, 0, 0, win32con.SRCCOPY)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    img = Image.frombuffer("RGB", (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                           bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return img

def save_failure_screenshot(label):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("screenshots", exist_ok=True)
    path = f"screenshots/missing_{label}_{timestamp}.png"
    screen = capture_screen()
    screen.save(path)
    print(f"[❌] 버튼 '{label}' 탐색 실패 - 스크린샷 저장됨: {path}")
    return path

def gpt_find_button_region(image: Image.Image, label: str):
    try:
        print(f"[GPT Vision] 버튼 '{label}' 탐색 중...")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            max_tokens=50,
            messages=[
                {"role": "system", "content": "다음 UI 버튼을 찾고 좌표를 반환하세요."},
                {"role": "user", "content": f"이 스크린샷에서 '{label}' 버튼의 좌상단(x, y), 우하단(x, y) 좌표를 알려줘."},
                {"role": "user", "content": {"image": image_bytes.getvalue(), "type": "image/png"}},
            ]
        )
        content = response.choices[0].message.content
        print(f"[GPT 응답] {content}")
        coords = [int(num) for num in content.replace("(", "").replace(")", "").replace(",", "").split() if num.isdigit()]
        return tuple(coords[:4]) if len(coords) == 4 else None
    except Exception as e:
        print(f"[GPT Vision 오류] {e}")
        return None

def smart_find_and_click(filename: str, fallback: str = None, label: str = None, threshold=0.75, retry_on_fail=False):
    attempts = 3 if retry_on_fail else 1
    for attempt in range(attempts):
        screen = capture_screen()
        screen_np = np.array(screen)

        if fallback:
            fallback_path = os.path.join(CACHE_DIR, fallback)
            if os.path.exists(fallback_path):
                template = cv2.imread(fallback_path, cv2.IMREAD_COLOR)
                screen_cv = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
                res = cv2.matchTemplate(screen_cv, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)
                if max_val >= threshold:
                    h, w = template.shape[:2]
                    center = (max_loc[0] + w // 2 + random.randint(-2, 2), max_loc[1] + h // 2 + random.randint(-2, 2))
                    pyautogui.click(center)
                    print(f"[✅] fallback 이미지 클릭: {fallback} at {center}")
                    return center

        if label:
            coords = gpt_find_button_region(screen, label)
            if coords:
                x1, y1, x2, y2 = coords
                center_x = (x1 + x2) // 2 + random.randint(-2, 2)
                center_y = (y1 + y2) // 2 + random.randint(-2, 2)
                pyautogui.click(center_x, center_y)
                print(f"[✅] GPT 클릭: {label} at ({center_x}, {center_y})")
                return (center_x, center_y)
        time.sleep(1)
    save_failure_screenshot(label or filename)
    return None

def find_on_screen(filename, threshold=0.8):
    screen = np.array(capture_screen())
    screen_cv = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    path = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(path):
        return False
    template = cv2.imread(path, cv2.IMREAD_COLOR)
    res = cv2.matchTemplate(screen_cv, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    return max_val >= threshold