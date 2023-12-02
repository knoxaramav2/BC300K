


class Settings:

    draw_outline           : bool = True

    def __init__(self):
        pass

__inst__: Settings = None
def get_settings():
    global __inst__
    if __inst__ == None:
        __inst__ = Settings()
    return __inst__