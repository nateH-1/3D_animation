from manim import (
    RIGHT,
    UP,
    BraceBetweenPoints,
    FadeIn,
    MoveAlongPath,
    Rectangle,
    Scene,
    Text,
    VGroup,
    VMobject,
)

from quicksort_trace import (
    BaseCase,
    ChoosePivot,
    Compare,
    EnterRange,
    SeatPivot,
    Swap,
    trace_quicksort,
)

BACKGROUND = "#F4F7F8"
CELL_FILL = "#FFFFFF"
PIVOT_FILL = "#E5F5EA"
BORDER = "#D5DDE3"
NUMBER = "#243040"
PIVOT_INK = "#1F8A5B"

CELL_W = 0.78
CELL_H = 0.56
ROOT_Y = 2.7
ROW_DY = 1.62
# This start order seats into the diagram: 4 3 1 2 | 5 | 9 7 10 6.
VALUES = [4, 3, 1, 2, 6, 9, 7, 10, 5]


class ArrayRow:
    def __init__(self, lo: int, hi: int, depth: int, cells: dict[int, VGroup]) -> None:
        self.lo = lo
        self.hi = hi
        self.depth = depth
        self.cells = cells


class QuicksortSplit(Scene):
    def construct(self) -> None:
        self.camera.background_color = BACKGROUND
        events, _final = trace_quicksort(VALUES)
        self.values = list(VALUES)
        self.rows: list[ArrayRow] = []
        self.active: ArrayRow | None = None
        self.lo = 0
        self.hi = len(self.values) - 1
        for event in events:
            self._play(event)
        self.wait(1.2)

    def _play(self, event: object) -> None:
        if isinstance(event, EnterRange):
            self._enter(event)
        elif isinstance(event, ChoosePivot):
            self._choose(event)
        elif isinstance(event, Compare):
            # The diagram marks the seated pivot only, so a compare does not recolor a cell.
            return
        elif isinstance(event, Swap):
            self._swap(event)
        elif isinstance(event, SeatPivot):
            self._seat(event)
        elif isinstance(event, BaseCase):
            self._base(event)

    def _enter(self, event: EnterRange) -> None:
        self.lo = event.lo
        self.hi = event.hi
        parent = _parent(self.rows, event.lo, event.hi)
        depth = 0 if parent is None else parent.depth + 1
        cells: dict[int, VGroup] = {}
        ordered: list[VGroup] = []
        for index in range(event.lo, event.hi + 1):
            cell = _cell(self.values[index])
            cells[index] = cell
            ordered.append(cell)
        group = VGroup(*ordered)
        group.arrange(RIGHT, buff=0)
        group.set_y(ROOT_Y - depth * ROW_DY)
        if parent is None:
            group.set_x(0)
        else:
            anchors = [parent.cells[index] for index in range(event.lo, event.hi + 1)]
            group.set_x(_center_x(anchors))
        row = ArrayRow(event.lo, event.hi, depth, cells)
        self.rows.append(row)
        self.active = row
        self.play(FadeIn(group), run_time=0.3)
        self.wait(0.2)

    def _choose(self, event: ChoosePivot) -> None:
        assert self.active is not None
        box = self.active.cells[event.index][0]
        self.play(box.animate.set_stroke(PIVOT_INK, width=2.5), run_time=0.25)

    def _swap(self, event: Swap) -> None:
        assert self.active is not None
        first = self.active.cells[event.i]
        second = self.active.cells[event.j]
        self.play(
            _hop(first, second.get_x()),
            _hop(second, first.get_x()),
            run_time=0.45,
        )
        self.active.cells[event.i] = second
        self.active.cells[event.j] = first
        self.values[event.i], self.values[event.j] = self.values[event.j], self.values[event.i]

    def _seat(self, event: SeatPivot) -> None:
        assert self.active is not None
        cell = self.active.cells[event.index]
        label = _pivot_label(cell)
        braces = _side_braces(self.active, self.lo, event.index, self.hi)
        self.play(
            cell[0].animate.set_fill(PIVOT_FILL).set_stroke(PIVOT_INK, width=1.5),
            FadeIn(label),
            *[FadeIn(brace) for brace in braces],
            run_time=0.4,
        )
        self.wait(0.15)

    def _base(self, event: BaseCase) -> None:
        parent = _parent(self.rows, event.index, event.index)
        depth = 0 if parent is None else parent.depth + 1
        cell = _cell(self.values[event.index], fill=PIVOT_FILL)
        cell[0].set_stroke(PIVOT_INK, width=1.5)
        cell.set_y(ROOT_Y - depth * ROW_DY)
        if parent is None:
            cell.set_x(0)
        else:
            cell.set_x(parent.cells[event.index].get_x())
        label = _pivot_label(cell)
        self.rows.append(ArrayRow(event.index, event.index, depth, {event.index: cell}))
        self.play(FadeIn(cell), FadeIn(label), run_time=0.3)


def _cell(value: int, fill: str = CELL_FILL) -> VGroup:
    box = Rectangle(
        width=CELL_W,
        height=CELL_H,
        fill_color=fill,
        fill_opacity=1,
        stroke_color=BORDER,
        stroke_width=1.5,
    )
    number = Text(str(value), font_size=24, color=NUMBER)
    number.move_to(box)
    return VGroup(box, number)


def _pivot_label(cell: VGroup) -> Text:
    label = Text("pivot", font_size=16, color=PIVOT_INK)
    label.next_to(cell, UP, buff=0.05)
    return label


def _parent(rows: list[ArrayRow], lo: int, hi: int) -> ArrayRow | None:
    matches = [
        row
        for row in rows
        if row.lo <= lo and hi <= row.hi and (row.hi - row.lo) > (hi - lo)
    ]
    if not matches:
        return None
    return min(matches, key=lambda row: row.hi - row.lo)


def _center_x(cells: list[VGroup]) -> float:
    left = min(cell.get_left()[0] for cell in cells)
    right = max(cell.get_right()[0] for cell in cells)
    return (left + right) / 2


def _side_braces(row: ArrayRow, lo: int, pivot: int, hi: int) -> list[BraceBetweenPoints]:
    braces = []
    if lo < pivot:
        braces.append(_brace([row.cells[index] for index in range(lo, pivot)]))
    if pivot < hi:
        braces.append(_brace([row.cells[index] for index in range(pivot + 1, hi + 1)]))
    return braces


def _brace(cells: list[VGroup]) -> BraceBetweenPoints:
    left = min(cell.get_left()[0] for cell in cells)
    right = max(cell.get_right()[0] for cell in cells)
    bottom = min(cell.get_bottom()[1] for cell in cells)
    return BraceBetweenPoints(
        [left, bottom, 0],
        [right, bottom, 0],
        buff=0.06,
        color=PIVOT_INK,
    )


def _hop(cell: VGroup, target_x: float) -> MoveAlongPath:
    start = cell.get_center()
    end = start.copy()
    end[0] = target_x
    mid = (start + end) / 2
    mid[1] += 0.45
    path = VMobject()
    path.set_points_smoothly([start, mid, end])
    return MoveAlongPath(cell, path)
