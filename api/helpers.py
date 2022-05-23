from random import choices

def generate_secret_key():
    return ''.join(choices(list(SYMBOLS), k=500))
