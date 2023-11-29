

def group_fnc(*fncs):
        def fncs(*args, **argvs):
            for f in fncs:
                f(args, argvs)
        return fncs
