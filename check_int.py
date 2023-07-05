def check_int(n: str):
    try:
        n = int(n)
        return True
    except:
        return False