# 채집 항목명
GATHER_SKILLS = [
    "일상채집", "나무베기", "광석캐기", "약초채집",
    "양털깎기", "추수", "호미질", "곤충채집"
]

# 만렙 설정
LEVEL_CAPS = {
    "일상채집": 10,
    "나무베기": 10,
    "광석캐기": 10,
    "약초채집": 10,
    "양털깎기": 10,
    "추수": 10,
    "호미질": 10,
    "곤충채집": 10
}

def get_target_level(skill_name):
    return LEVEL_CAPS.get(skill_name, 10)