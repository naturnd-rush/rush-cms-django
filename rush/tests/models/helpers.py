from unittest.mock import Mock


class MockFile(Mock):

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __repr__(self) -> str:
        return f'<MockFile: "{self.name}">'
