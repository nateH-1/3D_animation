from dataclasses import dataclass


@dataclass(frozen=True)
class EnterRange:
    lo: int
    hi: int
    side: str = "start"


@dataclass(frozen=True)
class ChoosePivot:
    index: int


@dataclass(frozen=True)
class Compare:
    index: int
    goes_left: bool


@dataclass(frozen=True)
class Swap:
    i: int
    j: int


@dataclass(frozen=True)
class SeatPivot:
    index: int


@dataclass(frozen=True)
class BaseCase:
    index: int


@dataclass(frozen=True)
class EmptyRange:
    lo: int
    hi: int
    side: str


@dataclass(frozen=True)
class ReturnRange:
    lo: int
    hi: int


Event = EnterRange | ChoosePivot | Compare | Swap | SeatPivot | BaseCase | EmptyRange | ReturnRange


def trace_quicksort(values: list[int]) -> tuple[list[Event], list[int]]:
    items = list(values)
    events: list[Event] = []
    if items:
        _sort(items, 0, len(items) - 1, events)
    return events, items


def _sort(items: list[int], lo: int, hi: int, events: list[Event], side: str = "start") -> None:
    if hi < lo:
        events.append(EmptyRange(lo, hi, side))
        return
    if lo == hi:
        events.append(BaseCase(lo))
        events.append(ReturnRange(lo, lo))
        return
    events.append(EnterRange(lo, hi, side))
    pivot_at = _partition(items, lo, hi, events)
    _sort(items, lo, pivot_at - 1, events, "left")
    _sort(items, pivot_at + 1, hi, events, "right")
    events.append(ReturnRange(lo, hi))


def _partition(items: list[int], lo: int, hi: int, events: list[Event]) -> int:
    pivot = items[hi]
    events.append(ChoosePivot(hi))
    i = lo - 1
    for j in range(lo, hi):
        goes_left = items[j] <= pivot
        events.append(Compare(j, goes_left))
        if not goes_left:
            continue
        i += 1
        if i != j:
            _exchange(items, i, j, events)
    seat = i + 1
    if seat != hi:
        _exchange(items, seat, hi, events)
    events.append(SeatPivot(seat))
    return seat


def _exchange(items: list[int], i: int, j: int, events: list[Event]) -> None:
    items[i], items[j] = items[j], items[i]
    events.append(Swap(i, j))
