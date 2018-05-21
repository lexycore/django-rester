from threading import Lock


class Singleton(type):
    #__singleton_lock = Lock()
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            #with cls.__singleton_lock:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
