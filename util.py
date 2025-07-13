import win32gui
import win32ui
import win32con
from PIL import Image
import io
import base64

def capture_window_base64(window_name="마비노기 모바일"):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd == 0:
        raise Exception("게임 창을 찾을 수 없습니다.")

    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width, height = right - left, bottom - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(bmp)
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    bmpinfo = bmp.GetInfo()
    bmpstr = bmp.GetBitmapBits(True)
    img = Image.frombuffer("RGB", (bmpinfo["bmWidth"], bmpinfo["bmHeight"]), bmpstr, "raw", "BGRX", 0, 1)

    win32gui.DeleteObject(bmp.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

def get_game_window_rect(window_name="마비노기 모바일"):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd == 0:
        return None
    rect = win32gui.GetWindowRect(hwnd)
    return rect  # (left, top, right, bottom)

def capture_window_image(window_name="마비노기 모바일"):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd == 0:
        raise Exception("게임 창을 찾을 수 없습니다.")

    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width, height = right - left, bottom - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(bmp)
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    bmpinfo = bmp.GetInfo()
    bmpstr = bmp.GetBitmapBits(True)
    img = Image.frombuffer("RGB", (bmpinfo["bmWidth"], bmpinfo["bmHeight"]), bmpstr, "raw", "BGRX", 0, 1)

    win32gui.DeleteObject(bmp.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return img  # PIL.Image 객체 반환
