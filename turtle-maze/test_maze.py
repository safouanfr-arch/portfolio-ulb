import unittest

from maze import EscapeGame


class MazeTests(unittest.TestCase):
    def test_demo_level_can_be_completed(self):
        game = EscapeGame()

        def no_question(_):
            self.fail("Unexpected door on this part of the route")

        self.assertEqual(game.move(-1, 0, no_question), "The way is blocked.")
        to_clue = [(0, 1)] * 2 + [(1, 0)] * 2 + [(0, -1)] * 2 + [(1, 0)] * 2 + [(0, 1)]
        for dr, dc in to_clue:
            game.move(dr, dc, no_question)
        self.assertTrue(game.clue_found)

        for _ in range(3):
            game.move(0, 1, no_question)
        self.assertEqual(game.move(0, 1, lambda _: None), "The door is still locked.")
        self.assertEqual(game.position, (5, 5))
        self.assertEqual(game.move(0, 1, lambda _: " 42 "), "The door is open.")
        self.assertTrue(game.door_open)

        to_exit = [(0, 1)] * 3 + [(-1, 0)] * 2 + [(0, -1)] * 2 + [(-1, 0)] * 2 + [(0, 1)] * 4
        for dr, dc in to_exit:
            game.move(dr, dc, no_question)
        self.assertTrue(game.won)
        self.assertEqual(game.tile_at(*game.position), "E")


if __name__ == "__main__":
    unittest.main()
