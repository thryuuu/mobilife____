import os
import cv2
import numpy as np
import pyautogui
import random
import time
from PIL import Image
from util import capture_window_base64
import openai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

def image_exists(filename):
    path = os.path.join("button_cache", filename)
    return os.path.exists(path)

def smart_find_and_click(filename, fallback=None, label="버튼"):
    screen = capture_window_base64()
    template_path = os.path.join("button_cache", filename)

    if os.path.exists(template_path):
        coords = find_image_on_screen(screen, template_path)
        if coords:
            click_center(coords)
            return coords

    coords = gpt_find_button_region(screen, label)
    if coords:
        save_button_image(screen, coords, template_path)
        click_center(coords)
        return coords

    if fallback:
        fallback_path = os.path.join("button_cache", fallback)
        if os.path.exists(fallback_path):
            coords = find_image_on_screen(screen, fallback_path)
            if coords:
                click_center(coords)
                return coords
    return None

def gpt_find_button_region(base64_img, label):
    if not base64_img or base64_img.strip() == "":
        print("❌ GPT Vision 요청 실패: base64_img 값이 비어 있습니다.")
        return None
    if not label or not isinstance(label, str):
        print("❌ GPT Vision 요청 실패: label이 유효하지 않습니다.")
        return None
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "화면에서 UI 버튼을 찾아서 영역을 알려주세요."},
                {"role": "user", "content": f"이 이미지에서 '{label}' 버튼의 영역을 찾아줘."},
                {"role": "user", "image": {"image": base64_img, "detail": "low"}}
            ],
            max_tokens=300
        )
        coords = parse_response_coords(response.choices[0].message.content)
        return coords
    except Exception as e:
        print(f"[GPT Vision 실패]: {e}")
        return None

def parse_response_coords(text):
    import re
    match = re.search(r"\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)", text)
    if match:
        return tuple(map(int, match.groups()))
    return None

def save_button_image(base64_img, coords, path):
    from PIL import Image
    import base64, io
    img_data = base64.b64decode(base64_img)
    img = Image.open(io.BytesIO(img_data))
    crop = img.crop(coords)
    crop.save(path)

def find_image_on_screen(base64_img, template_path):
    import base64, io
    from PIL import Image
    screenshot = Image.open(io.BytesIO(base64.b64decode(base64_img)))
    screen_np = np.array(screenshot)
    template = cv2.imread(template_path)
    res = cv2.matchTemplate(screen_np, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val > 0.8:
        h, w = template.shape[:2]
        return (max_loc[0], max_loc[1], max_loc[0]+w, max_loc[1]+h)
    return None

def click_center(coords):
    x1, y1, x2, y2 = coords
    x = int((x1 + x2) / 2 + random.randint(-3, 3))
    y = int((y1 + y2) / 2 + random.randint(-3, 3))
    pyautogui.moveTo(x, y, duration=0.2)
    pyautogui.click()