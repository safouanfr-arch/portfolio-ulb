# Castle Escape

A small escape game in Python Turtle, adapted from Safouan Tassi's 2020 exercise. Explore the castle, collect the clue for the locked door, and reach the exit.

```sh
python3 maze.py
python3 -m unittest -v
```

The game requires Python 3 with Tk installed and a desktop display. Move with the arrow keys and press `R` to restart. The blue square contains the clue, the orange square is a locked door, and the green square is the exit.

The recovered source referenced a separate configuration module, map, inventory file, and question file. This edition supplies a new demonstration map, clue, and question in the script. It preserves the movement, inventory, and question-based door mechanics from the exercise.
