class ObjectNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class LoadingException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SavingException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
