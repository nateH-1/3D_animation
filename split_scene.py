from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UL,
    UP,
    UR,
    BraceBetweenPoints,
    FadeIn,
    FadeOut,
    Line,
    MoveAlongPath,
    Rectangle,
    RoundedRectangle,
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
MUTED = "#5A6B78"
PIVOT_INK = "#1F8A5B"
ACTIVE = "#D6E4F0"
ACTIVE_INK = "#3D5A73"
TYPEFACE = "Helvetica"

CELL_W = 0.78
CELL_H = 0.56
ROOT_Y = 2.7
ROW_DY = 1.62
MIN_ROW_DY = 0.9
ROW_FLOOR = -1.5
# This start order seats into the diagram: 4 3 1 2 | 5 | 9 7 10 6.
VALUES = [1, 2, 3, 4, 5, 6, 7]


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
        self.note: Text | None = None
        self.note_ready_at = 0.0
        self.said: set[str] = set()
        self._mount_theme()
        self._intro()
        events, self.final = trace_quicksort(VALUES)
        self.values = list(VALUES)
        self.rows: list[ArrayRow] = []
        self.active: ArrayRow | None = None
        self.lo = 0
        self.hi = len(self.values) - 1
        self.pivot_value: int | None = None
        max_depth = max(1, len(self.values) - 1)
        usable = ROOT_Y - ROW_FLOOR
        self.row_dy = min(ROW_DY, max(MIN_ROW_DY, usable / max_depth))
        self.tree = VGroup()
        self.add(self.tree)
        for event in events:
            self._play(event)
        self._say("The whole row is sorted.")
        self.wait(1.2)
        self._outro()

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

    def _mount_theme(self) -> None:
        width = self.camera.frame_width
        bar = Rectangle(
            width=width,
            height=0.1,
            fill_color=PIVOT_INK,
            fill_opacity=1,
            stroke_width=0,
        )
        bar.to_edge(UP, buff=0)
        brand = _label("QuickSort", 18, PIVOT_INK)
        brand.to_edge(UP, buff=0.22).to_edge(LEFT, buff=0.4)
        tag = _label("Divide and conquer", 14, MUTED)
        tag.next_to(brand, RIGHT, buff=0.28)
        tag.align_to(brand, DOWN)
        rule = Line(
            LEFT * (width / 2 - 0.35),
            RIGHT * (width / 2 - 0.35),
            color=BORDER,
            stroke_width=1.5,
        )
        rule.next_to(bar, DOWN, buff=0.44)
        rail = _panel(width - 0.7, 0.58)
        rail.to_edge(DOWN, buff=0.16)
        rail_edge = Line(
            rail.get_corner(UL),
            rail.get_corner(UR),
            color=PIVOT_INK,
            stroke_width=2.5,
        )
        rail.set_z_index(1)
        rail_edge.set_z_index(2)
        bar.set_z_index(3)
        brand.set_z_index(3)
        tag.set_z_index(3)
        rule.set_z_index(3)
        self.add(bar, brand, tag, rule, rail, rail_edge)
        self.caption_rail = rail
        self.chrome = [bar, brand, tag, rule, rail, rail_edge]

    def _intro(self) -> None:
        welcome = _label("Welcome, folks", 42)
        underline = Line(LEFT * 1.35, RIGHT * 1.35, color=PIVOT_INK, stroke_width=4)
        underline.next_to(welcome, DOWN, buff=0.16)
        subtitle = _label(
            "This is a 3D animation explaining\nthe QuickSort algorithm.",
            24,
            MUTED,
            line_spacing=0.18,
        )
        subtitle.next_to(underline, DOWN, buff=0.4)
        cover = VGroup(welcome, underline, subtitle)
        cover.move_to(ORIGIN).shift(UP * 0.15)
        self._say("A short look at the algorithm.")
        self.play(FadeIn(cover), run_time=0.6)
        self.wait(2.5)

        body = _label(
            "QuickSort is a divide-and-conquer sorting algorithm. It chooses a pivot, then splits the remaining values into a left group of items less than or equal to the pivot and a right group of items greater than the pivot. After that split, the pivot is already in its final place, and QuickSort repeats the same steps on each side until every group is sorted.",
            22,
            align="left",
            width=9.2,
        )
        definition = _text_card(body)
        definition.move_to(ORIGIN).shift(UP * 0.12)
        self.play(FadeOut(cover), FadeIn(definition), run_time=0.7)
        self._say("What is QuickSort?")
        self.wait(15)

        heading = _label("We start with this list:", 22)
        heading_rule = Line(LEFT * 1.6, RIGHT * 1.6, color=PIVOT_INK, stroke_width=3)
        cells = VGroup(*[_cell(value) for value in VALUES])
        cells.arrange(RIGHT, buff=0)
        heading_rule.next_to(heading, DOWN, buff=0.14)
        cells.next_to(heading_rule, DOWN, buff=0.4)
        numbers = VGroup(heading, heading_rule, cells)
        numbers.move_to(ORIGIN).shift(UP * 0.12)
        self.play(FadeOut(definition), FadeIn(numbers), run_time=0.7)
        self._say("These values are the input for the sort.")
        self.wait(2.5)
        self.play(FadeOut(numbers), run_time=0.5)
        self.wait(0.3)

    def _outro(self) -> None:
        self._clear_stage()
        heading = _label("The list is sorted.", 22)
        heading_rule = Line(LEFT * 1.35, RIGHT * 1.35, color=PIVOT_INK, stroke_width=3)
        cells = VGroup(*[_cell(value, fill=PIVOT_FILL) for value in self.final])
        for cell in cells:
            cell[0].set_stroke(PIVOT_INK, width=1.5)
        cells.arrange(RIGHT, buff=0)
        heading_rule.next_to(heading, DOWN, buff=0.14)
        cells.next_to(heading_rule, DOWN, buff=0.4)
        finished = VGroup(heading, heading_rule, cells)
        finished.move_to(ORIGIN).shift(UP * 0.12)
        self.play(FadeIn(finished), run_time=0.6)
        self._say("Every value is in its final place.")
        self.wait(2.6)

        body = _label(
            "Choose the last value as the pivot.\n"
            "Move smaller or equal values left, then seat the pivot.\n"
            "Repeat on each side until every value is in place.",
            22,
            align="left",
        )
        recap = _text_card(body)
        recap.move_to(ORIGIN).shift(UP * 0.12)
        self.play(FadeOut(finished), FadeIn(recap), run_time=0.7)
        self._say("The idea, in three steps.")
        self.wait(4.5)

        thanks = _label("Thanks for watching.", 42)
        underline = Line(LEFT * 1.7, RIGHT * 1.7, color=PIVOT_INK, stroke_width=4)
        underline.next_to(thanks, DOWN, buff=0.16)
        close = _label(
            "One pivot at a time,\nuntil the row is in order.",
            24,
            MUTED,
            line_spacing=0.18,
        )
        close.next_to(underline, DOWN, buff=0.4)
        ending = VGroup(thanks, underline, close)
        ending.move_to(ORIGIN).shift(UP * 0.15)
        self.play(FadeOut(recap), FadeIn(ending), run_time=0.7)
        self._say("QuickSort")
        self.wait(2.6)

    def _clear_stage(self) -> None:
        self._hold_note()
        keep = set(self.chrome)
        extras = [mob for mob in list(self.mobjects) if mob not in keep]
        if extras:
            self.play(*[FadeOut(mob) for mob in extras], run_time=0.55)
        self.note = None
        self.note_ready_at = 0.0

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
        if parent is None:
            group.set_x(0)
            group.set_y(ROOT_Y)
        else:
            anchors = [parent.cells[index] for index in range(event.lo, event.hi + 1)]
            group.set_x(_center_x(anchors))
            group.set_y(anchors[0].get_y() - self.row_dy)
        row = ArrayRow(event.lo, event.hi, depth, cells)
        self.rows.append(row)
        self.active = row
        self._ensure_visible(group)
        highlight = None
        if parent is not None:
            anchors = [parent.cells[index] for index in range(event.lo, event.hi + 1)]
            highlight = _range_box(anchors)
            self.play(FadeIn(highlight), run_time=0.2)
        if event.side == "start":
            self._say("Start with the whole row.")
        elif event.side == "left":
            self._say("Now sort the left side.")
        else:
            self._say("Now sort the right side.")
        self.tree.add(group)
        self.play(FadeIn(group), run_time=0.3)
        if highlight is not None:
            self.play(FadeOut(highlight), run_time=0.15)
        self.wait(0.15)

    def _choose(self, event: ChoosePivot) -> None:
        assert self.active is not None
        self.pivot_value = self.values[event.index]
        p = self.pivot_value
        self._say_first(
            "choose",
            f"Pick the last value, {p}, as the pivot.",
            f"The pivot is {p}.",
        )
        box = self.active.cells[event.index][0]
        self.play(box.animate.set_stroke(PIVOT_INK, width=2.5), run_time=0.25)

    def _compare(self, event: Compare) -> None:
        assert self.active is not None
        p = self.pivot_value
        self._say_once(
            "compare",
            f"Values up to {p} go left. Bigger values stay right.",
        )
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

    def _seat(self, event: SeatPivot) -> None:
        assert self.active is not None
        self.active.pivot = event.index
        cell = self.active.cells[event.index]
        label = _pivot_label(cell)
        braces = _side_braces(self.active, self.lo, event.index, self.hi)
        p = self.pivot_value
        self._say_first("seat", f"{p} is now in its final place.", f"{p} is in place.")
        self.tree.add(label, *braces)
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
        if parent is None:
            cell.set_x(0)
            cell.set_y(ROOT_Y)
        else:
            anchor = parent.cells[event.index]
            cell.set_x(anchor.get_x())
            cell.set_y(anchor.get_y() - self.row_dy)
        label = _pivot_label(cell)
        self.rows.append(ArrayRow(event.index, event.index, depth, {event.index: cell}))
        value = self.values[event.index]
        self._say_first("base", "A single value is already sorted.", f"{value} is already sorted.")
        self._ensure_visible(cell)
        label.next_to(cell, UP, buff=0.05)
        self.tree.add(cell, label)
        self.play(FadeIn(cell), FadeIn(label), run_time=0.3)

    def _empty(self, event: EmptyRange) -> None:
        self._say_first(
            "empty",
            f"The {event.side} side is empty, so that call ends right away.",
            f"The {event.side} side is empty.",
        )
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
        if parent.depth == 0 and parent.pivot is not None:
            side = "left" if event.hi < parent.pivot else "right"
            self._say(f"The {side} half is sorted.")
        else:
            self._say_once("return", "That side is sorted, so it moves back up.")
        anims = []
        arrivals: list[tuple[int, VGroup]] = []
        for offset, index in enumerate(range(event.lo, event.hi + 1)):
            copy = row.cells[index].copy()
            copy.set_z_index(8)
            self.tree.add(copy)
            anims.append(copy.animate.move_to(targets[offset]))
            arrivals.append((index, copy))
        self.play(*anims, run_time=1.0)
        for index, copy in arrivals:
            parent.cells[index] = copy
        parent_cells = [parent.cells[index] for index in range(event.lo, event.hi + 1)]
        done = _range_box(parent_cells)
        self.play(FadeOut(highlight), FadeIn(done), run_time=0.25)
        self.wait(0.5)
        self.play(FadeOut(done), run_time=0.2)

    def _flash(self, cells: list[VGroup], hold: float) -> None:
        box = _range_box(cells)
        self.play(FadeIn(box), run_time=0.25)
        self.wait(hold)
        self.play(FadeOut(box), run_time=0.2)

    def _ensure_visible(self, mob: VMobject) -> None:
        bottom = mob.get_bottom()[1]
        if bottom >= ROW_FLOOR:
            return
        lift = ROW_FLOOR - bottom
        movers = [mob]
        if len(self.tree) > 0:
            movers.insert(0, self.tree)
        self.play(*[item.animate.shift(UP * lift) for item in movers], run_time=0.35)

    def _hold_note(self) -> None:
        leftover = self.note_ready_at - self.renderer.time
        if self.note is not None and leftover > 0:
            self.wait(leftover)

    def _say_once(self, key: str, message: str) -> None:
        if key in self.said:
            return
        self.said.add(key)
        self._say(message)

    def _say_first(self, key: str, first: str, later: str) -> None:
        if key in self.said:
            self._say(later)
            return
        self.said.add(key)
        self._say(first)

    def _say(self, message: str) -> None:
        self._hold_note()
        note = _label(message, 20)
        note.move_to(self.caption_rail.get_center())
        note.set_z_index(2)
        if self.note is None:
            self.play(FadeIn(note), run_time=0.15)
        else:
            self.play(FadeOut(self.note), FadeIn(note), run_time=0.15)
        self.note = note
        self.note_ready_at = self.renderer.time + max(1.6, 0.9 + 0.3 * len(message.split()))


def _wrap_text(message: str, font_size: int, max_width: float) -> str:
    words = message.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        trial_width = Text(
            trial,
            font=TYPEFACE,
            font_size=font_size,
            disable_ligatures=True,
        ).width
        if current and trial_width > max_width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return "\n".join(lines)


def _label(
    message: str,
    font_size: int,
    color: str = NUMBER,
    line_spacing: float = -1,
    align: str = "center",
    width: float | None = None,
) -> VMobject:
    if width is not None:
        message = _wrap_text(message, font_size, width)
    if "\n" in message:
        rows = [
            Text(
                line,
                font=TYPEFACE,
                font_size=font_size,
                color=color,
                disable_ligatures=True,
            )
            for line in message.split("\n")
            if line.strip()
        ]
        block = VGroup(*rows)
        gap = font_size * 0.012 if line_spacing < 0 else font_size * 0.008 * (1 + line_spacing)
        block.arrange(DOWN, buff=gap, aligned_edge=LEFT if align == "left" else ORIGIN)
        return block
    return Text(
        message,
        font=TYPEFACE,
        font_size=font_size,
        color=color,
        line_spacing=line_spacing,
        disable_ligatures=True,
    )


def _text_card(body: VMobject) -> VGroup:
    pad_x = 0.5
    pad_y = 0.42
    accent_w = 0.09
    gap = 0.32
    card = RoundedRectangle(
        corner_radius=0.16,
        width=body.width + pad_x + accent_w + gap + 0.42,
        height=body.height + pad_y * 2,
        fill_color=CELL_FILL,
        fill_opacity=1,
        stroke_color=BORDER,
        stroke_width=1.25,
    )
    accent = RoundedRectangle(
        corner_radius=0.045,
        width=accent_w,
        height=max(0.4, card.height - 0.42),
        fill_color=PIVOT_INK,
        fill_opacity=1,
        stroke_width=0,
    )
    accent.move_to(card.get_center()).align_to(card, LEFT).shift(RIGHT * 0.2)
    body.next_to(accent, RIGHT, buff=gap)
    body.set_y(card.get_y())
    return VGroup(card, accent, body)


def _panel(width: float, height: float) -> Rectangle:
    return Rectangle(
        width=width,
        height=height,
        fill_color=CELL_FILL,
        fill_opacity=1,
        stroke_color=BORDER,
        stroke_width=1.5,
    )


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
    number = _label(str(value), 24)
    number.move_to(box)
    return VGroup(box, number)


def _pivot_label(cell: VGroup) -> Text:
    label = _label("pivot", 16, PIVOT_INK)
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
