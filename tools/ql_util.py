import random
import string


# 随机生成数字与小写字母字符串
def get_random_str(rdm_leg: int = 8, status: bool = False):
    random_str = ''
    base_str = string.octdigits
    if status:
        base_str = base_str + string.ascii_lowercase
    length = len(base_str) - 1
    for i in range(rdm_leg):
        random_str += base_str[random.randint(0, length)]
    return random_str
