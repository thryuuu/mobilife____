import pyautogui
import time

def scroll_to_bottom():
    for _ in range(5):
        pyautogui.scroll(-500)
        time.sleep(0.5)