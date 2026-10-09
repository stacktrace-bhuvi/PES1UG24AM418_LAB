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

        # Transition after reveal
        self.engine.is_revealing = False
        self.engine.current_card = Card("10", "Spades", 10)
        self.engine.deck.draw = lambda: Card("J", "Clubs", 11)
        self.engine.evaluate_guess("LOWER")
        self.assertEqual(self.engine.streak, 0)

    def test_consecutive_win_streak_multipliers(self):
        self.assertEqual(self.engine.streak, 0)
        self.assertEqual(self.engine.multiplier, 1)
        self.assertEqual(self.engine.score, 0)

        # Win 1
        self.engine.current_card = Card("9", "Hearts", 9)
        self.engine.deck.draw = lambda: Card("10", "Spades", 10)
        self.engine.evaluate_guess("HIGHER")
        self.assertEqual(self.engine.streak, 1)
        self.assertEqual(self.engine.score, 1)

        # Reset reveal flag for next turn simulation
        self.engine.is_revealing = False
        self.engine.current_card = Card("10", "Spades", 10)
        self.engine.deck.draw = lambda: Card("J", "Diamonds", 11)
        self.engine.evaluate_guess("HIGHER")
        self.assertEqual(self.engine.streak, 2)
        self.assertEqual(self.engine.score, 3)

        # Win 3
        self.engine.is_revealing = False
        self.engine.current_card = Card("J", "Diamonds", 11)
        self.engine.deck.draw = lambda: Card("Q", "Clubs", 12)
        self.engine.evaluate_guess("HIGHER")
        self.assertEqual(self.engine.streak, 3)
        self.assertEqual(self.engine.score, 6)

        # Loss
        self.engine.is_revealing = False
        self.engine.current_card = Card("Q", "Clubs", 12)
        self.engine.deck.draw = lambda: Card("5", "Hearts", 5)
        self.engine.evaluate_guess("HIGHER")
        self.assertEqual(self.engine.streak, 0)
        self.assertEqual(self.engine.multiplier, 1)
        self.assertEqual(self.engine.score, 5)

    def test_tie_evaluation_push(self):
        self.engine.current_card = Card("9", "Hearts", 9)
        self.engine.deck.draw = lambda: Card("10", "Spades", 10)
        self.engine.evaluate_guess("HIGHER")

        self.engine.is_revealing = False
        self.engine.current_card = Card("10", "Spades", 10)
        self.engine.deck.draw = lambda: Card("J", "Diamonds", 11)
        self.engine.evaluate_guess("HIGHER")

        self.assertEqual(self.engine.streak, 2)
        self.assertEqual(self.engine.score, 3)

        # Tie
        self.engine.is_revealing = False
        self.engine.current_card = Card("J", "Diamonds", 11)
        self.engine.deck.draw = lambda: Card("J", "Spades", 11)
        self.engine.evaluate_guess("HIGHER")

        self.assertEqual(self.engine.score, 3)
        self.assertEqual(self.engine.streak, 2)
        self.assertIn("PUSH", self.engine.status_msg)

    def test_side_by_side_reveal_and_rapid_click_protection(self):
        self.engine.current_card = Card("7", "Hearts", 7)
        self.engine.deck.draw = lambda: Card("9", "Spades", 9)
        
        # Initial guess triggers reveal state
        self.engine.evaluate_guess("HIGHER")
        self.assertTrue(self.engine.is_revealing)
        self.assertEqual(self.engine.previous_card.numeric_rank, 7)
        self.assertEqual(self.engine.next_card.numeric_rank, 9)
        initial_score = self.engine.score

        # Rapid second click during reveal must be ignored
        self.engine.evaluate_guess("LOWER")
        self.assertEqual(self.engine.score, initial_score)  # Score unchanged!

        # Complete reveal duration update
        self.engine.reveal_start_time = pygame.time.get_ticks() - 1500  # simulate time past duration
        self.engine.update()
        self.assertFalse(self.engine.is_revealing)
        self.assertEqual(self.engine.current_card.numeric_rank, 9)


if __name__ == "__main__":
    unittest.main()
