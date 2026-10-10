from manim import (
    DOWN,
    RIGHT,
    UP,
    BraceBetweenPoints,
    FadeIn,
    FadeOut,
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
    EmptyRange,
    EnterRange,
    ReturnRange,
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
ACTIVE = "#D6E4F0"
ACTIVE_INK = "#3D5A73"

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
        self.pivot: int | None = None


class QuicksortSplit(Scene):
    def construct(self) -> None:
        self.camera.background_color = BACKGROUND
        events, _final = trace_quicksort(VALUES)
        self.values = list(VALUES)
        self.rows: list[ArrayRow] = []
        self.active: ArrayRow | None = None
        self.lo = 0
        self.hi = len(self.values) - 1
        self.pivot_value: int | None = None
        self.note: Text | None = None
        for event in events:
            self._play(event)
        self._say("The whole row is sorted.")
        self.wait(1.2)

    def _play(self, event: object) -> None:
        if isinstance(event, EnterRange):
            self._enter(event)
        elif isinstance(event, ChoosePivot):
            self._choose(event)
        elif isinstance(event, Compare):
            self._compare(event)
        elif isinstance(event, Swap):
            self._swap(event)
        elif isinstance(event, SeatPivot):
            self._seat(event)
        elif isinstance(event, BaseCase):
            self._base(event)
        elif isinstance(event, EmptyRange):
            self._empty(event)
        elif isinstance(event, ReturnRange):
            self._return(event)

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
        highlight = None
        if parent is not None:
            anchors = [parent.cells[index] for index in range(event.lo, event.hi + 1)]
            highlight = _range_box(anchors)
            self.play(FadeIn(highlight), run_time=0.2)
        self._say(_enter_line(event.side, depth))
        self.play(FadeIn(group), run_time=0.3)
        if highlight is not None:
            self.play(FadeOut(highlight), run_time=0.15)
        self.wait(0.15)

    def _choose(self, event: ChoosePivot) -> None:
        assert self.active is not None
        self.pivot_value = self.values[event.index]
        self._say(f"The pivot is {self.pivot_value}, the last value in this group.")
        box = self.active.cells[event.index][0]
        self.play(box.animate.set_stroke(PIVOT_INK, width=2.5), run_time=0.25)

    def _compare(self, event: Compare) -> None:
        assert self.active is not None
        value = self.values[event.index]
        if event.goes_left:
            self._say(f"{value} ≤ pivot, so it stays on the left.")
        else:
            self._say(f"{value} > pivot, so it stays on the right.")
        box = self.active.cells[event.index][0]
        color = box.get_stroke_color()
        width = box.get_stroke_width()
        self.play(box.animate.set_stroke(ACTIVE_INK, width=3), run_time=0.12)
        self.play(box.animate.set_stroke(color, width=width), run_time=0.12)

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
        self._say("These two values swap.")

    def _seat(self, event: SeatPivot) -> None:
        assert self.active is not None
        self.active.pivot = event.index
        cell = self.active.cells[event.index]
        label = _pivot_label(cell)
        braces = _side_braces(self.active, self.lo, event.index, self.hi)
        self.play(
            cell[0].animate.set_fill(PIVOT_FILL).set_stroke(PIVOT_INK, width=1.5),
            FadeIn(label),
            *[FadeIn(brace) for brace in braces],
            run_time=0.4,
        )
        if event.index == self.lo:
            self._say("The pivot is seated. The left side is empty.")
        else:
            self._say("The pivot is seated. The left group is next.")
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
        self._say("Base case.")

    def _empty(self, event: EmptyRange) -> None:
        self._say(_returned_line(event.side))
        self.wait(0.45)

    def _return(self, event: ReturnRange) -> None:
        row = _exact(self.rows, event.lo, event.hi)
        if row is None:
            return
        parent = _parent(self.rows, event.lo, event.hi)
        child_cells = [row.cells[index] for index in range(event.lo, event.hi + 1)]
        if parent is None:
            self._flash(child_cells, hold=0.45)
            return
        side = "left" if parent.pivot is not None and event.hi < parent.pivot else "right"
        highlight = _range_box(child_cells)
        self.play(FadeIn(highlight), run_time=0.25)
        self.wait(0.35)
        targets = [
            parent.cells[index].get_center().copy()
            for index in range(event.lo, event.hi + 1)
        ]
        self.play(
            *[FadeOut(parent.cells[index]) for index in range(event.lo, event.hi + 1)],
            run_time=0.25,
        )
        self.wait(0.15)
        anims = []
        arrivals: list[tuple[int, VGroup]] = []
        for offset, index in enumerate(range(event.lo, event.hi + 1)):
            copy = row.cells[index].copy()
            copy.set_z_index(8)
            self.add(copy)
            anims.append(copy.animate.move_to(targets[offset]))
            arrivals.append((index, copy))
        self.play(*anims, run_time=1.0)
        for index, copy in arrivals:
            parent.cells[index] = copy
        parent_cells = [parent.cells[index] for index in range(event.lo, event.hi + 1)]
        done = _range_box(parent_cells)
        self.play(FadeOut(highlight), FadeIn(done), run_time=0.25)
        self._say(_returned_line(side))
        self.wait(0.5)
        self.play(FadeOut(done), run_time=0.2)

    def _flash(self, cells: list[VGroup], hold: float) -> None:
        box = _range_box(cells)
        self.play(FadeIn(box), run_time=0.25)
        self.wait(hold)
        self.play(FadeOut(box), run_time=0.2)

    def _say(self, message: str) -> None:
        note = Text(message, font_size=20, color=NUMBER)
        note.to_edge(DOWN, buff=0.22)
        if self.note is None:
            self.play(FadeIn(note), run_time=0.15)
        else:
            self.play(FadeOut(self.note), FadeIn(note), run_time=0.15)
        self.note = note


def _returned_line(side: str) -> str:
    if side == "left":
        return "Left call returned."
    return "Right call returned."


def _enter_line(side: str, depth: int) -> str:
    if side == "start":
        return "Depth 0. Start with the whole row."
    if side == "left":
        return f"Depth {depth}. The left group is the next input."
    return f"Depth {depth}. The right group is the next input."


def _range_box(cells: list[VGroup]) -> Rectangle:
    left = min(cell.get_left()[0] for cell in cells)
    right = max(cell.get_right()[0] for cell in cells)
    bottom = min(cell.get_bottom()[1] for cell in cells)
    top = max(cell.get_top()[1] for cell in cells)
    box = Rectangle(
        width=(right - left) + 0.08,
        height=(top - bottom) + 0.08,
        stroke_color=ACTIVE_INK,
        stroke_width=2,
        fill_color=ACTIVE,
        fill_opacity=0.45,
    )
    box.move_to([(left + right) / 2, (bottom + top) / 2, 0])
    box.set_z_index(-1)
    return box


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


def _exact(rows: list[ArrayRow], lo: int, hi: int) -> ArrayRow | None:
    matches = [row for row in rows if row.lo == lo and row.hi == hi]
    if not matches:
        return None
    return matches[-1]


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
