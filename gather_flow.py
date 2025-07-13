from gather_tasks import run_gathering_sequence
from vision import smart_find_and_click
import time

def run_full_gather_routine():
    print("💡 자동 채집 루틴 시작")

    if smart_find_and_click("profile.png", fallback="profile_c.png", label="프로필 버튼") is None:
        print("❌ 프로필 버튼 탐색 실패")
        return
    time.sleep(2)

    if smart_find_and_click("life_skill.png", label="생활 스킬 버튼") is None:
        print("❌ 생활 스킬 버튼 탐색 실패")
        return
    time.sleep(2)

    run_gathering_sequence()