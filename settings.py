# 채집 항목명
GATHER_SKILLS = [
    "일상채집", "나무베기", "광석캐기", "약초채집",
    "양털깎기", "추수", "호미질", "곤충채집"
]

# 만렙 설정
LEVEL_CAPS = {
    "일상채집": 20,
    "나무베기": 30,
    "광석캐기": 30,
    "약초채집": 30,
    "양털깎기": 30,
    "추수": 30,
    "호미질": 30,
    "곤충채집": 30
}

def get_target_level(skill_name):
    return LEVEL_CAPS.get(skill_name, 10)