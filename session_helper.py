import re


def extract_session_id(session_str : str):
    match = re.search("/sessions/(.*?)/contexts/",session_str)
    if match:
        return match.group(1)
    return ""


def get_str_from_dict(food_dict):
    return ", ".join([f"{int(value)} {key}" for key,value in food_dict.items()])


