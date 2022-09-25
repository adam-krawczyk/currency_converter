class AnonymousUser:
    def __init__(self):
        pass

    @property
    def is_authenticated(self):
        return False
