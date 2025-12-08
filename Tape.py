class Tape:
    def __init__(self, content: str, blank: str = "_") -> None:
        self.blank = blank
        # sparse: index -> symbol
        self.cells: dict[int, str] = {i: ch for i, ch in enumerate(content)}
        self.head: int = 0

    def read(self) -> str:
        return self.cells.get(self.head, self.blank)

    def write(self, symbol: str | None) -> None:
        if symbol is None:
            return
        self.cells[self.head] = symbol

    def move(self, direction: str) -> None:
        if direction == "L":
            self.head -= 1
        elif direction == "R":
            self.head += 1
        elif direction == "S":
            return
        else:
            raise ValueError(f"Invalid direction {direction!r}")

    def render(self) -> str:
        if not self.cells:
            return ""
        min_i = min(self.cells.keys())
        max_i = max(self.cells.keys())
        return "".join(self.cells.get(i, self.blank) for i in range(min_i, max_i + 1))
