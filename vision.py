import os
import cv2
import numpy as np
import pyautogui
import random
import time
from PIL import Image
from util import capture_window_base64, capture_window_image, get_game_window_rect
import openai
from dotenv import load_dotenv
import pytesseract
import base64
import io

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

def image_exists(filename):
    path = os.path.join("button_cache", filename)
    return os.path.exists(path)

def smart_find_and_click(filename, fallback=None, label="버튼"):
    screen = capture_window_base64()
    template_path = os.path.join("button_cache", filename)

    # 1. 템플릿 이미지로 먼저 탐색
    if os.path.exists(template_path):
        coords = find_image_on_screen(screen, template_path)
        if coords:
            click_center(coords)
            return coords

    # 2. GPT Vision 사용
    coords = gpt_find_button_region(screen, label)
    if coords:
        save_button_image(screen, coords, template_path)
        click_center(coords)
        return coords

    # 3. OCR로 텍스트 기반 탐색 보완
    coords = ocr_find_text_coordinates(label)
    if coords:
        click_center(coords)
        return coords

    # 4. fallback 템플릿으로 시도
    if fallback:
        fallback_path = os.path.join("button_cache", fallback)
        if os.path.exists(fallback_path):
            coords = find_image_on_screen(screen, fallback_path)
            if coords:
                click_center(coords)
                return coords

    print(f"❌ '{label}' 버튼 탐색 실패")
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
                {
                    "role": "system",
                    "content": "화면에서 UI 버튼을 찾아서 (x1, y1, x2, y2) 형식으로 정확하게 알려줘."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"이 이미지에서 '{label}' 버튼의 영역을 찾아줘."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_img}",
                                "detail": "low"
                            }
                        }
                    ]
                }
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
    match = re.search(r"\\((\\d+),\\s*(\\d+),\\s*(\\d+),\\s*(\\d+)\\)", text)
    if match:
        return tuple(map(int, match.groups()))
    return None

def save_button_image(base64_img, coords, path):
    img_data = base64.b64decode(base64_img)
    img = Image.open(io.BytesIO(img_data))
    crop = img.crop(coords)
    crop.save(path)

def find_image_on_screen(base64_img, template_path):
    screenshot = Image.open(io.BytesIO(base64.b64decode(base64_img))).convert("RGB")
    screen_np = np.array(screenshot)
    screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)

    template_img = Image.open(template_path).convert("RGB")
    template_np = np.array(template_img)
    template_gray = cv2.cvtColor(template_np, cv2.COLOR_RGB2GRAY)

    best_score = -1
    best_coords = None

    for scale in [1.0, 0.95, 1.05, 0.9, 1.1, 0.85, 1.15]:
        resized_template = cv2.resize(template_gray, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        res = cv2.matchTemplate(screen_gray, resized_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        print(f"[matchTemplate] scale={scale:.2f}, match score={max_val:.4f}")
        if max_val > best_score:
            best_score = max_val
            h, w = resized_template.shape
            best_coords = (max_loc[0], max_loc[1], max_loc[0] + w, max_loc[1] + h)

    if best_score > 0.6:  # 스코어 기준 조정 가능
        return best_coords
    return None

def click_center(coords):
    x1, y1, x2, y2 = coords
    x = int((x1 + x2) / 2 + random.randint(-3, 3))
    y = int((y1 + y2) / 2 + random.randint(-3, 3))

    game_rect = get_game_window_rect()
    if game_rect:
        gx, gy = game_rect[0], game_rect[1]
        pyautogui.moveTo(gx + x, gy + y, duration=0.2)
        pyautogui.click()
    else:
        print("게임 창 위치를 찾을 수 없습니다. 화면 전체 기준으로 클릭합니다.")
        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click()

def ocr_find_text_coordinates(keyword):
    img = capture_window_image()
    ocr_data = pytesseract.image_to_data(img, lang="kor+eng", output_type=pytesseract.Output.DICT)
    for i, text in enumerate(ocr_data['text']):
        if keyword in text:
            x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
            return (x, y, x + w, y + h)
    return None
