import unittest
import pygame

pygame.init()
pygame.font.init()

from game.card import Card
from game.deck import Deck
from game.game_engine import GameEngine


class TestCardPredictor(unittest.TestCase):

    def setUp(self):
        self.engine = GameEngine(650, 440)

    def test_deck_ranks(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)
        rank_dict = {card.rank_str: card.numeric_rank for card in deck.cards}
        self.assertEqual(rank_dict["2"], 2)
        self.assertEqual(rank_dict["9"], 9)
        self.assertEqual(rank_dict["10"], 10)
        self.assertEqual(rank_dict["J"], 11)
        self.assertEqual(rank_dict["Q"], 12)
        self.assertEqual(rank_dict["K"], 13)
        self.assertEqual(rank_dict["A"], 14)

    def test_rank_comparison_boundary(self):
        c9 = Card("9", "Hearts", 9)
        c10 = Card("10", "Spades", 10)
        cJ = Card("J", "Clubs", 11)
        cQ = Card("Q", "Diamonds", 12)
        cK = Card("K", "Hearts", 13)
        cA = Card("A", "Spades", 14)

        self.assertTrue(c10.numeric_rank > c9.numeric_rank)
        self.assertTrue(cJ.numeric_rank > c10.numeric_rank)
        self.assertTrue(cQ.numeric_rank > cJ.numeric_rank)
        self.assertTrue(cK.numeric_rank > cQ.numeric_rank)
        self.assertTrue(cA.numeric_rank > cK.numeric_rank)

    def test_evaluation_higher_lower(self):
        self.engine.current_card = Card("9", "Hearts", 9)
        self.engine.deck.draw = lambda: Card("10", "Spades", 10)
        self.engine.evaluate_guess("HIGHER")
        self.assertGreater(self.engine.score, 0)

        self.engine.current_card = Card("10", "Spades", 10)
        self.engine.deck.draw = lambda: Card("J", "Clubs", 11)
        self.engine.evaluate_guess("LOWER")
        self.assertEqual(self.engine.streak, 0)

    def test_consecutive_win_streak_multipliers(self):
        self.assertEqual(self.engine.streak, 0)
        self.assertEqual(self.engine.multiplier, 1)
        self.assertEqual(self.engine.score, 0)

        # Win 1: 9 -> 10 (HIGHER) -> streak=1, multiplier=1, +1 point (total score=1)
        self.engine.current_card = Card("9", "Hearts", 9)
        self.engine.deck.draw = lambda: Card("10", "Spades", 10)
        self.engine.evaluate_guess("HIGHER")
        self.assertEqual(self.engine.streak, 1)
        self.assertEqual(self.engine.multiplier, 1)
        self.assertEqual(self.engine.score, 1)

        # Win 2: 10 -> J (HIGHER) -> streak=2, multiplier=2, +2 points (total score=3)
        self.engine.deck.draw = lambda: Card("J", "Diamonds", 11)
        self.engine.evaluate_guess("HIGHER")
        self.assertEqual(self.engine.streak, 2)
        self.assertEqual(self.engine.multiplier, 2)
        self.assertEqual(self.engine.score, 3)

        # Win 3: J -> Q (HIGHER) -> streak=3, multiplier=3, +3 points (total score=6)
        self.engine.deck.draw = lambda: Card("Q", "Clubs", 12)
        self.engine.evaluate_guess("HIGHER")
        self.assertEqual(self.engine.streak, 3)
        self.assertEqual(self.engine.multiplier, 3)
        self.assertEqual(self.engine.score, 6)

        # Wrong guess: Q -> 5 (HIGHER) -> streak reset to 0, multiplier reset to 1, score -1 (total score=5)
        self.engine.deck.draw = lambda: Card("5", "Hearts", 5)
        self.engine.evaluate_guess("HIGHER")
        self.assertEqual(self.engine.streak, 0)
        self.assertEqual(self.engine.multiplier, 1)
        self.assertEqual(self.engine.score, 5)

    def test_tie_evaluation_push(self):
        # Build up streak first: 2 wins -> streak=2, score=3
        self.engine.current_card = Card("9", "Hearts", 9)
        self.engine.deck.draw = lambda: Card("10", "Spades", 10)
        self.engine.evaluate_guess("HIGHER")
        self.engine.deck.draw = lambda: Card("J", "Diamonds", 11)
        self.engine.evaluate_guess("HIGHER")

        self.assertEqual(self.engine.streak, 2)
        self.assertEqual(self.engine.score, 3)

        # Tie card: J of Spades (rank 11) vs current J of Diamonds (rank 11)
        self.engine.deck.draw = lambda: Card("J", "Spades", 11)
        self.engine.evaluate_guess("HIGHER")

        # Verify PUSH: score and streak unchanged
        self.assertEqual(self.engine.score, 3)
        self.assertEqual(self.engine.streak, 2)
        self.assertEqual(self.engine.multiplier, 2)
        self.assertIn("PUSH", self.engine.status_msg)


if __name__ == "__main__":
    unittest.main()
