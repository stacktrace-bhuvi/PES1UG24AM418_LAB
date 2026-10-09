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
        # Test HIGHER prediction when card is actually higher (10 vs 9)
        self.engine.current_card = Card("9", "Hearts", 9)
        # Mock deck draw
        self.engine.deck.draw = lambda: Card("10", "Spades", 10)
        self.engine.evaluate_guess("HIGHER")
        self.assertEqual(self.engine.score, 1)

        # Test LOWER prediction when card is higher (J vs 10) -> WRONG
        self.engine.current_card = Card("10", "Spades", 10)
        self.engine.deck.draw = lambda: Card("J", "Clubs", 11)
        self.engine.evaluate_guess("LOWER")
        self.assertEqual(self.engine.score, 0)


if __name__ == "__main__":
    unittest.main()
