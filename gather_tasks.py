from settings import GATHER_SKILLS, get_target_level
from vision import smart_find_and_click
from scroll_utils import scroll_to_bottom
from gather_monitor import wait_for_gather_completion
import time

def run_gathering_sequence():
    for skill in GATHER_SKILLS:
        if smart_find_and_click(f"{skill}.png", label=f"{skill} 버튼") is None:
            print(f"⚠️ {skill} 버튼 탐색 실패, 건너뜀")
            continue
        time.sleep(2)

        scroll_to_bottom()
        time.sleep(2)

        if smart_find_and_click("gather_detail.png", label="채집 항목 상세") is None:
            print(f"⚠️ 채집 항목 진입 실패, 건너뜀")
            continue
        time.sleep(2)

        if smart_find_and_click("find_location.png", label="가까운 위치 찾기") is None:
            print("⚠️ 가까운 위치 찾기 실패")
            continue

        print(f"⏳ {skill} 채집 중... 완료 대기")
        wait_for_gather_completion()