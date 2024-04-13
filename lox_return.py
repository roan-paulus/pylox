class LoxReturn(Exception):
    def __init__(self, value, *args, **kwargs):
        super().__init__(args, kwargs)
        self.value: object = value

    def with_traceback(self):
        super().with_traceback(None)
