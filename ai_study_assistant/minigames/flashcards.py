"""
Flashcard game module for interactive learning.
"""
import json
import os
import random
import uuid
import logging
from datetime import datetime

class FlashcardGame:
    """
    Manages flashcard sets for spaced repetition learning.
    """
    
    def __init__(self, storage_dir="./data/flashcards"):
        """
        Initialize the flashcard game.
        
        Args:
            storage_dir (str): Directory to store flashcard sets
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def create_set(self, title, description=""):
        """
        Create a new flashcard set.
        
        Args:
            title (str): Title of the flashcard set
            description (str): Description of the set
            
        Returns:
            dict: The created flashcard set
        """
        set_id = str(uuid.uuid4())
        
        flashcard_set = {
            "id": set_id,
            "title": title,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "cards": []
        }
        
        # Save the set
        self._save_set(flashcard_set)
        
        return flashcard_set
    
    def add_card(self, set_id, front, back, tags=None):
        """
        Add a card to a flashcard set.
        
        Args:
            set_id (str): ID of the flashcard set
            front (str): Front side content of the card
            back (str): Back side content of the card
            tags (list): List of tags for the card
            
        Returns:
            dict: The updated flashcard set
        """
        flashcard_set = self.get_set(set_id)
        if not flashcard_set:
            return None
            
        card_id = str(uuid.uuid4())
        
        new_card = {
            "id": card_id,
            "front": front,
            "back": back,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "last_reviewed": None,
            "review_count": 0,
            "difficulty": 0  # 0-3 scale: 0=easy, 3=hard
        }
        
        flashcard_set["cards"].append(new_card)
        flashcard_set["updated_at"] = datetime.now().isoformat()
        
        # Save the updated set
        self._save_set(flashcard_set)
        
        return flashcard_set
    
    def get_set(self, set_id):
        """
        Get a flashcard set by ID.
        
        Args:
            set_id (str): ID of the flashcard set
            
        Returns:
            dict: The flashcard set or None if not found
        """
        try:
            file_path = os.path.join(self.storage_dir, f"{set_id}.json")
            
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            self.logger.error(f"Error loading flashcard set: {e}")
            return None
    
    def list_sets(self):
        """
        List all flashcard sets.
        
        Returns:
            list: List of flashcard sets
        """
        sets = []
        
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.storage_dir, filename)
                    with open(file_path, 'r') as file:
                        flashcard_set = json.load(file)
                        # Add summary info
                        flashcard_set["card_count"] = len(flashcard_set.get("cards", []))
                        # Remove cards array to keep the response light
                        if "cards" in flashcard_set:
                            del flashcard_set["cards"]
                        sets.append(flashcard_set)
        except Exception as e:
            self.logger.error(f"Error listing flashcard sets: {e}")
            
        return sets
    
    def get_cards_to_review(self, set_id, count=10):
        """
        Get cards that need review from a set.
        Uses spaced repetition principles to select cards.
        
        Args:
            set_id (str): ID of the flashcard set
            count (int): Maximum number of cards to return
            
        Returns:
            list: Cards that need review
        """
        flashcard_set = self.get_set(set_id)
        if not flashcard_set or not flashcard_set.get("cards"):
            return []
            
        # Sort cards based on review priority
        cards = flashcard_set["cards"]
        
        # Sort logic: prioritize cards that haven't been reviewed and those with higher difficulty
        cards_to_review = sorted(
            cards,
            key=lambda card: (
                0 if card["last_reviewed"] is None else 1,  # Never reviewed first
                card["difficulty"],                          # Then by difficulty (highest first)
                -card["review_count"]                        # Then by least reviewed
            )
        )
        
        return cards_to_review[:count]
    
    def generate_quiz(self, set_id, count=5):
        """
        Generate a quiz from a flashcard set.
        
        Args:
            set_id (str): ID of the flashcard set
            count (int): Number of quiz questions
            
        Returns:
            dict: Quiz with questions and answers
        """
        flashcard_set = self.get_set(set_id)
        if not flashcard_set or not flashcard_set.get("cards") or len(flashcard_set["cards"]) < 2:
            return None
            
        # Get cards and shuffle
        cards = flashcard_set["cards"].copy()
        random.shuffle(cards)
        
        # Take up to 'count' cards
        quiz_cards = cards[:min(count, len(cards))]
        
        # Create quiz
        quiz = {
            "set_id": set_id,
            "set_title": flashcard_set["title"],
            "questions": []
        }
        
        for card in quiz_cards:
            # For each question, provide the correct answer and 3 distractors
            correct_answer = card["back"]
            
            # Get distractors from other cards
            potential_distractors = [c["back"] for c in cards if c["id"] != card["id"]]
            
            # If we have enough distractors
            if len(potential_distractors) >= 3:
                distractors = random.sample(potential_distractors, 3)
            else:
                # If not enough cards for distractors, generate some
                distractors = potential_distractors + [
                    f"Incorrect answer {i}" for i in range(3 - len(potential_distractors))
                ]
            
            # Create question
            answers = distractors + [correct_answer]
            random.shuffle(answers)
            
            question = {
                "card_id": card["id"],
                "question": card["front"],
                "answers": answers,
                "correct_index": answers.index(correct_answer)
            }
            
            quiz["questions"].append(question)
        
        return quiz
    
    def record_review(self, set_id, card_id, difficulty):
        """
        Record a card review.
        
        Args:
            set_id (str): ID of the flashcard set
            card_id (str): ID of the card
            difficulty (int): Difficulty rating (0-3)
            
        Returns:
            dict: The updated flashcard set
        """
        flashcard_set = self.get_set(set_id)
        if not flashcard_set:
            return None
            
        # Find the card
        for card in flashcard_set["cards"]:
            if card["id"] == card_id:
                card["last_reviewed"] = datetime.now().isoformat()
                card["review_count"] += 1
                card["difficulty"] = max(0, min(3, difficulty))  # Ensure difficulty is 0-3
                break
        
        flashcard_set["updated_at"] = datetime.now().isoformat()
        
        # Save the updated set
        self._save_set(flashcard_set)
        
        return flashcard_set
    
    def _save_set(self, flashcard_set):
        """
        Save a flashcard set to disk.
        
        Args:
            flashcard_set (dict): Flashcard set to save
        """
        try:
            file_path = os.path.join(self.storage_dir, f"{flashcard_set['id']}.json")
            
            with open(file_path, 'w') as file:
                json.dump(flashcard_set, file, indent=2)
                
            self.logger.info(f"Saved flashcard set: {flashcard_set['title']}")
        except Exception as e:
            self.logger.error(f"Error saving flashcard set: {e}")