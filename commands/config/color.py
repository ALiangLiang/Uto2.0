import random

WHITE = 0xffffff
RED = 0xff0000
GREEN = 0x00ff00
BLUE = 0x0000ff
YELLOW = 0xffff00
CYAN = 0x00ffff
PURPLE = 0xff00ff
BLACK = 0x000000
ORANGE = 0xff7b00
LIGHT_PURPLE =0xd561ff
LIGHT_BLUE = 0x204cf8
LIGHT_ORANGE = 0xffbc70
LIGHT_GREEN = 0x97ff7a

HAPPY_FACE = [
    "ヾ(•ω•`)o",
    "o(*°▽°*)o",
    "( •̀ ω •́ )y",
    "(・∀・(・∀・(・∀・*)",
    "◉‿◉",
    "٩(ˊᗜˋ )و",
    "┬┴┬┴┤･ω･)ﾉ",
    "ρ(・ω・、)",
    "(｡◕∀◕｡)",
    "(⁎⁍̴̛ᴗ⁍̴̛⁎)",
    "ಠ౪ಠ"
]
SAD_FACE = [
    "（；´д｀）ゞ",
    "o(TヘTo)",
    "(；′⌒`)",
    "ಠ_ಠ"
]

def Face(kind:str):
    if kind == "happy":
        return random.choice(HAPPY_FACE)
    elif kind == "sad":
        return random.choice(SAD_FACE)
    else:
        return ""