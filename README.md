# Pattern Lock Personality Test

A small Tkinter desktop app that lets you draw a 3x3 pattern-lock gesture and receive a personality-style insight based on the shape and complexity of the pattern.

## What It Does

- Draws a pattern on a 3x3 lock grid.
- Checks the pattern against a built-in access pattern: `1 -> 2 -> 5 -> 8`.
- Classifies the drawn shape as one of these pattern types:
  - `line`
  - `zigzag`
  - `square`
  - `l_shape`
  - `random`
- Picks a matching personality insight from `patternNature.json`.
- Scores pattern complexity from the total path distance.

## Requirements

- Python 3.x
- Tkinter available in your Python installation

No third-party packages are required.

## Run

From this folder:

```bash
python Pattern.py
```

If `python` is not mapped to Python 3 on your system, use:

```bash
py Pattern.py
```

## How To Use

1. Run the app.
2. Hold the left mouse button and drag across the nodes to create a pattern.
3. Release the mouse button to submit the pattern.
4. Read the access result and personality insight.

You can also click `Analyze Only` to analyze the current pattern without the access check.

## Controls

- Left mouse drag: draw a pattern
- Left mouse release: submit pattern
- `Clear Pattern`: clear the current drawing
- Right mouse click: clear the current drawing
- `Analyze Only`: show personality insight for the current pattern

## Project Files

- `Pattern.py`: main Tkinter application
- `patternNature.json`: personality messages grouped by pattern type

## Notes

- The app requires at least 2 selected nodes before a pattern is considered valid.
- After each submission, the drawing is briefly shown and then cleared.
- After 5 attempts, the app performs a full reset.
- If `patternNature.json` is missing, the app falls back to built-in default personality messages.

## Example Pattern Types

- Straight movement in one direction tends to be classified as `line`.
- A strong turn in a short pattern tends to be classified as `l_shape`.
- Multi-turn patterns may be classified as `zigzag`, `square`, or `random` depending on direction changes and angles.