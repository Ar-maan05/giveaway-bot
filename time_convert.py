from check_int import check_int

def time_convert(t):
    
    if check_int(t):
        return int(t)
    
    t = t.strip()
    
    r = t[::-1]
    
    s = ""
    
    n = ""
    
    for x in r:
        if not check_int(x):
            s += x
            continue
        
        n += x
        
    n = int(n[::-1])
    
    s = s[::-1]
    
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600*24, "sec": 1, "min": 60, "hr": 3600, "day": 3600*24, "second": 1, "minute": 60, "hour": 3600, "days": 3600*24, "seconds": 1, "minutes": 60, "hours": 3600}
    
    if not s in time_dict:
        return -1
    
    val = time_dict[s]
    
    final = int(n * val)
    
    return -1 if final < 10 else final
    