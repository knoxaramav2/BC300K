

def group_fnc(*fncs):
    def cmb_fncs(*args, **argvs):
        for f in fncs:
            f(*args, **argvs)
    return cmb_fncs
