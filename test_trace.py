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


def replay(values: list[int], events: list[object]) -> tuple[list[int], list[int], list[int]]:
    items = list(values)
    pivot = None
    seats: list[int] = []
    bases: list[int] = []
    for event in events:
        if isinstance(event, ChoosePivot):
            pivot = items[event.index]
        elif isinstance(event, Compare):
            assert pivot is not None
            assert event.goes_left == (items[event.index] <= pivot)
        elif isinstance(event, Swap):
            items[event.i], items[event.j] = items[event.j], items[event.i]
        elif isinstance(event, SeatPivot):
            assert items[event.index] == pivot
            seats.append(pivot)
            pivot = None
        elif isinstance(event, BaseCase):
            bases.append(items[event.index])
    return items, seats, bases


def main() -> None:
    source = [6, 3, 8, 1, 5, 2, 7, 4]
    events, final = trace_quicksort(source)
    assert source == [6, 3, 8, 1, 5, 2, 7, 4], "input stays unchanged"
    played, seats, bases = replay(source, events)
    assert played == [1, 2, 3, 4, 5, 6, 7, 8], "replay sorts the row"
    assert final == [1, 2, 3, 4, 5, 6, 7, 8], "trace result sorts the row"
    assert seats == [4, 2, 6, 8], "pivots seat in this order"
    assert [event.index for event in events if isinstance(event, SeatPivot)] == [
        3,
        1,
        5,
        7,
    ], "pivot seats land on these indexes"
    assert bases == [1, 3, 5, 7], "single bars finish as these values"
    assert isinstance(events[0], EnterRange) and (events[0].lo, events[0].hi) == (0, 7)
    assert isinstance(events[1], ChoosePivot) and events[1].index == 7

    dup_events, dup_final = trace_quicksort([2, 2])
    dup_played, dup_seats, dup_bases = replay([2, 2], dup_events)
    assert dup_played == [2, 2], "equal values stay sorted"
    assert dup_final == [2, 2], "equal values stay sorted"
    assert dup_seats == [2] and dup_bases == [2]

    diagram = [4, 3, 1, 2, 6, 9, 7, 10, 5]
    diagram_events, diagram_final = trace_quicksort(diagram)
    diagram_played, diagram_seats, diagram_bases = replay(diagram, diagram_events)
    assert diagram_played == [1, 2, 3, 4, 5, 6, 7, 9, 10], "diagram array sorts"
    assert diagram_final == [1, 2, 3, 4, 5, 6, 7, 9, 10], "diagram array sorts"
    assert diagram_seats == [5, 2, 3, 6, 9], "diagram pivots seat in this order"
    assert diagram_bases == [1, 4, 7, 10], "diagram singles finish as these values"

    assert trace_quicksort([]) == ([], [])
    one_events, one_final = trace_quicksort([4])
    assert one_final == [4]
    assert len(one_events) == 2
    assert isinstance(one_events[0], BaseCase) and one_events[0].index == 0
    assert isinstance(one_events[1], ReturnRange) and (one_events[1].lo, one_events[1].hi) == (0, 0)

    ordered = [1, 2, 3, 4, 5]
    ordered_events, ordered_final = trace_quicksort(ordered)
    assert ordered_final == [1, 2, 3, 4, 5], "sorted input stays sorted"
    assert not any(isinstance(event, Swap) for event in ordered_events), "sorted input does not swap"
    assert [event.side for event in ordered_events if isinstance(event, EmptyRange)] == [
        "right",
        "right",
        "right",
        "right",
    ], "sorted input leaves every right side empty"
    assert [(event.lo, event.hi) for event in ordered_events if isinstance(event, ReturnRange)] == [
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
    ], "sorted calls return from the left"

    ties = [2, 2, 1, 2]
    ties_events, ties_final = trace_quicksort(ties)
    ties_played, _, _ = replay(ties, ties_events)
    assert ties_played == ties_final == [1, 2, 2, 2], "duplicate values sort"

    assert [(event.lo, event.hi) for event in diagram_events if isinstance(event, ReturnRange)] == [
        (0, 0),
        (3, 3),
        (2, 3),
        (0, 3),
        (6, 6),
        (8, 8),
        (6, 8),
        (5, 8),
        (0, 8),
    ], "diagram calls return left, then right"
    assert [(event.side, event.lo, event.hi) for event in diagram_events if isinstance(event, EmptyRange)] == [
        ("left", 2, 1),
        ("left", 5, 4),
    ], "diagram empty sides"
    print("trace ok")


if __name__ == "__main__":
    main()
