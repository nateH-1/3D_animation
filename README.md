# QuickSort Visualization with Manim

CS 465 group project by Jabali, Nathan, and Kidus.

This repository animates QuickSort in [Manim](https://www.manim.community/). The current scene shows how a last-element pivot is chosen, how the active range is partitioned, and how the two sides are sorted on their own rows.

## Learning objectives

- Explain the role of the pivot in QuickSort.
- Follow comparisons and swaps during partitioning.
- See how recursion splits the remaining work into smaller ranges.
- Recognize when a pivot reaches its final sorted position.
- See why a last-element pivot can produce one-sided partitions on already-sorted input.

## Algorithm

The trace uses Lomuto partitioning with the last element of the active range as the pivot:

1. Select the last element of the active range as the pivot.
2. Scan the other elements in that range.
3. When a value is less than or equal to the pivot, move it into the smaller-element region, swapping when needed.
4. After the scan, swap the pivot into the position just after that region. That index is its final place.
5. Sort the left and right ranges on their own.
6. Stop when a range is empty or holds one element.

Values equal to the pivot go to the left side.

## Example

The rendered scene starts from:

```python
VALUES = [4, 3, 1, 2, 6, 9, 7, 10, 5]
```

The first partition seats `5` and leaves:

```text
4  3  1  2  |  5  |  9  7  10  6
```

The finished order is:

```text
[1, 2, 3, 4, 5, 6, 7, 9, 10]
```

To animate a different array, change `VALUES` in `split_scene.py` and render again. The storyboard's main example, `[38, 27, 43, 3, 9, 82, 10]`, and the already-sorted case, `[3, 9, 10, 27, 38, 43, 82]`, are the planned follow-up inputs. With a last-element pivot, that sorted input picks the largest remaining value each time, so the right side stays empty.

QuickSort is O(n log n) on average and O(n²) in the worst case. The sorted input is that worst-case pattern for this pivot choice.

## What the scene shows

`QuicksortSplit` walks the event trace and draws one row per recursive range:

| Visual | Meaning |
| --- | --- |
| Numbered boxes | Values in the active range |
| Green border | Pivot just chosen |
| Green fill and a `pivot` label | Pivot seated in its final position |
| Brace under a side | Range still to be sorted |
| A new row | The next recursive range, placed under its parent |
| Boxes hopping | A swap |

Compare steps are recorded in the trace. This diagram marks the seated pivot and the side ranges, and it does not recolor a cell on each comparison.

## Project layout

| File | Role |
| --- | --- |
| `quicksort_trace.py` | Runs QuickSort and records each step |
| `split_scene.py` | Manim scene `QuicksortSplit` |
| `test_trace.py` | Checks the trace, including duplicates and the diagram array |

## Setup

Python 3.12 or newer, and Manim 0.21.0.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you use [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

## Run

Preview the partition scene:

```bash
manim -pql split_scene.py QuicksortSplit
```

`-p` opens the video when rendering finishes. `-ql` is a fast low-quality preview. Use `-qh` for a sharper render.

Check the algorithm trace:

```bash
python test_trace.py
```

A passing run prints `trace ok`.

The storyboard also plans a title, a short explanation, a final sorted comparison, and a separate already-sorted render. Those scenes are not in `QuicksortSplit` yet.

## Check before submitting a render

- The diagram array finishes as `[1, 2, 3, 4, 5, 6, 7, 9, 10]`.
- Every hop matches a swap in the trace.
- A seated pivot stays in that position.
- Later rows exclude the seated pivot and stop at one element.
- Captions, braces, and boxes do not overlap.
