import re

SPAM = re.compile(r"([-\w\d:%._+~#=]*\.[\w\d]{2,6})|(@[\w\d_]*)")
CODE = re.compile(r"([0-9\s]{12})")


def is_malicious(message):
    return re.search(SPAM, message) is not None


def is_friend_code(message):
    return re.search(CODE, message) is not None
