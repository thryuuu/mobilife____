import time
from vision import image_exists

def wait_for_gather_completion(timeout=180):
    start = time.time()
    while time.time() - start < timeout:
        if not image_exists("gather_quest.png"):
            print("✅ 채집 완료 감지됨")
            return
        time.sleep(3)
    print("⚠️ 채집 완료 감지 실패 (타임아웃)")