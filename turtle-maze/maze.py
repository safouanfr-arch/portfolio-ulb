"""A small Turtle escape game adapted from the 2020 project."""

# The original level data was not recovered. This level is a new demo.
LEVEL = (
    "#############",
    "#S....#....E#",
    "###.#.#.#####",
    "#...#.#.....#",
    "#.###.###.#.#",
    "#.I...D...#.#",
    "#############",
)
CLUE = "The password is 42."
QUESTION = "What is the two-digit password?"


class EscapeGame:
    def __init__(self):
        self.position = next(
            (row, column)
            for row, tiles in enumerate(LEVEL)
            for column, tile in enumerate(tiles)
            if tile == "S"
        )
        self.clue_found = False
        self.door_open = False
        self.won = False

    def tile_at(self, row, column):
        tile = LEVEL[row][column]
        if tile == "S" or (tile == "I" and self.clue_found) or (tile == "D" and self.door_open):
            return "."
        return tile

    def move(self, dr, dc, ask):
        if self.won:
            return "You escaped the castle."

        row, column = self.position
        row += dr
        column += dc
        if not (0 <= row < len(LEVEL) and 0 <= column < len(LEVEL[row])):
            return "The way is blocked."

        tile = self.tile_at(row, column)
        if tile == "#":
            return "The way is blocked."

        status = ""
        if tile == "D":
            answer = ask(QUESTION)
            if answer is None or answer.strip() != "42":
                return "The door is still locked."
            self.door_open = True
            status = "The door is open."
        elif tile == "I":
            self.clue_found = True
            status = "You found a note."
        elif tile == "E":
            self.won = True
            status = "You escaped the castle."

        self.position = (row, column)
        return status


def main():
    import turtle

    screen = turtle.Screen()
    screen.setup(720, 480)
    screen.title("Castle Escape")
    screen.bgcolor("#f3f6f8")
    screen.tracer(False)

    pen = turtle.Turtle(visible=False)
    pen.penup()
    game = EscapeGame()
    cell = 38
    left = -(len(LEVEL[0]) * cell) / 2
    top = 117
    tile_colors = {"#": "#414d58", ".": "#e1e8e7", "D": "#a7542d",
                   "I": "#bed5eb", "E": "#baddcd"}
    tile_symbols = {"D": "D", "I": "?", "E": "E"}

    def label(x, y, text, size, weight="normal", color="#182a36"):
        pen.goto(x, y)
        pen.color(color)
        pen.write(text, font=("Arial", size, weight))

    def draw(status=""):
        pen.clear()
        label(left, 172, "Castle Escape", 24, "bold")
        label(left, 134, "Inventory: " + (CLUE if game.clue_found else "empty"), 12)

        pen.setheading(0)
        for row, tiles in enumerate(LEVEL):
            for column in range(len(tiles)):
                tile = game.tile_at(row, column)
                x = left + column * cell
                y = top - row * cell
                pen.goto(x, y)
                pen.color("#f3f6f8", tile_colors[tile])
                pen.pendown()
                pen.begin_fill()
                for _ in range(4):
                    pen.forward(cell)
                    pen.right(90)
                pen.end_fill()
                pen.penup()
                if tile in tile_symbols:
                    label(x + 13, y - 27, tile_symbols[tile], 14, "bold",
                          "white" if tile == "D" else "#182a36")

        row, column = game.position
        pen.goto(left + (column + 0.5) * cell, top - (row + 0.5) * cell)
        pen.dot(22, "#bd3a31")
        label(left, -188, status, 13, "bold")
        screen.update()

    def ask(question):
        answer = screen.textinput("Locked door", question)
        screen.listen()
        return answer

    def move(dr, dc):
        draw(game.move(dr, dc, ask))

    def restart():
        nonlocal game
        game = EscapeGame()
        draw()

    for key, delta in {"Up": (-1, 0), "Down": (1, 0), "Left": (0, -1), "Right": (0, 1)}.items():
        screen.onkeypress(lambda direction=delta: move(*direction), key)
    screen.onkeypress(restart, "r")
    draw()
    screen.listen()
    screen.mainloop()


if __name__ == "__main__":
    main()
