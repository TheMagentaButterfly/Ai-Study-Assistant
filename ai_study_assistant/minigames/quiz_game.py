"""
Quiz game module for interactive learning.
"""
import json
import os
import random
import uuid
import logging
from datetime import datetime

class QuizGame:
    """
    Manages quiz games for active recall learning.
    """
    
    def __init__(self, storage_dir="./data/quizzes"):
        """
        Initialize the quiz game.
        
        Args:
            storage_dir (str): Directory to store quizzes
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def create_quiz(self, title, description="", category="general"):
        """
        Create a new quiz.
        
        Args:
            title (str): Title of the quiz
            description (str): Description of the quiz
            category (str): Category of the quiz
            
        Returns:
            dict: The created quiz
        """
        quiz_id = str(uuid.uuid4())
        
        quiz = {
            "id": quiz_id,
            "title": title,
            "description": description,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "questions": []
        }
        
        # Save the quiz
        self._save_quiz(quiz)
        
        return quiz
    
    def add_question(self, quiz_id, question_text, answers, correct_answer_index, explanation=""):
        """
        Add a question to a quiz.
        
        Args:
            quiz_id (str): ID of the quiz
            question_text (str): Text of the question
            answers (list): List of possible answers
            correct_answer_index (int): Index of the correct answer
            explanation (str): Explanation for the answer
            
        Returns:
            dict: The updated quiz
        """
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            return None
            
        question_id = str(uuid.uuid4())
        
        new_question = {
            "id": question_id,
            "question_text": question_text,
            "answers": answers,
            "correct_answer_index": correct_answer_index,
            "explanation": explanation
        }
        
        quiz["questions"].append(new_question)
        quiz["updated_at"] = datetime.now().isoformat()
        
        # Save the updated quiz
        self._save_quiz(quiz)
        
        return quiz
    
    def get_quiz(self, quiz_id):
        """
        Get a quiz by ID.
        
        Args:
            quiz_id (str): ID of the quiz
            
        Returns:
            dict: The quiz or None if not found
        """
        try:
            file_path = os.path.join(self.storage_dir, f"{quiz_id}.json")
            
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            self.logger.error(f"Error loading quiz: {e}")
            return None
    
    def list_quizzes(self, category=None):
        """
        List all quizzes, optionally filtered by category.
        
        Args:
            category (str, optional): Category to filter by
            
        Returns:
            list: List of quizzes
        """
        quizzes = []
        
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.storage_dir, filename)
                    with open(file_path, 'r') as file:
                        quiz = json.load(file)
                        
                        # Filter by category if specified
                        if category and quiz.get("category") != category:
                            continue
                            
                        # Add summary info
                        quiz["question_count"] = len(quiz.get("questions", []))
                        # Remove questions array to keep the response light
                        if "questions" in quiz:
                            del quiz["questions"]
                        quizzes.append(quiz)
        except Exception as e:
            self.logger.error(f"Error listing quizzes: {e}")
            
        return quizzes
    
    def get_random_questions(self, quiz_id, count=5):
        """
        Get random questions from a quiz.
        
        Args:
            quiz_id (str): ID of the quiz
            count (int): Number of questions to return
            
        Returns:
            list: Random questions from the quiz
        """
        quiz = self.get_quiz(quiz_id)
        if not quiz or not quiz.get("questions"):
            return []
            
        questions = quiz["questions"]
        
        # If we have more questions than requested count, randomize
        if len(questions) > count:
            return random.sample(questions, count)
        
        # Otherwise return all questions in random order
        random.shuffle(questions)
        return questions
    
    def create_quiz_session(self, quiz_id, user_id=None):
        """
        Create a new quiz session.
        
        Args:
            quiz_id (str): ID of the quiz
            user_id (str, optional): ID of the user
            
        Returns:
            dict: The created quiz session
        """
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            return None
            
        # Create a session with randomized questions
        questions = self.get_random_questions(quiz_id)
        if not questions:
            return None
            
        session_id = str(uuid.uuid4())
        
        session = {
            "id": session_id,
            "quiz_id": quiz_id,
            "user_id": user_id,
            "title": quiz["title"],
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "questions": questions,
            "current_question_index": 0,
            "answers": [],
            "score": None
        }
        
        # Remove correct answer indices to avoid cheating
        for question in session["questions"]:
            question["user_answer_index"] = None
            question["is_correct"] = None
        
        return session
    
    def answer_question(self, session, question_index, answer_index):
        """
        Record an answer for a question in a session.
        
        Args:
            session (dict): Quiz session
            question_index (int): Index of the question
            answer_index (int): Index of the selected answer
            
        Returns:
            dict: Updated quiz session with answer results
        """
        if question_index >= len(session["questions"]):
            return session
            
        question = session["questions"][question_index]
        
        # Get the correct answer from the original quiz
        quiz = self.get_quiz(session["quiz_id"])
        if not quiz:
            return session
            
        # Find the original question to get the correct answer
        original_question = None
        for q in quiz["questions"]:
            if q["id"] == question["id"]:
                original_question = q
                break
                
        if not original_question:
            return session
            
        correct_answer_index = original_question["correct_answer_index"]
        
        # Record the answer
        question["user_answer_index"] = answer_index
        question["is_correct"] = (answer_index == correct_answer_index)
        question["explanation"] = original_question.get("explanation", "")
        
        # Update session progress
        session["current_question_index"] = question_index + 1
        
        # Check if quiz is completed
        if session["current_question_index"] >= len(session["questions"]):
            session["completed_at"] = datetime.now().isoformat()
            
            # Calculate score
            correct_count = sum(1 for q in session["questions"] if q.get("is_correct", False))
            session["score"] = round((correct_count / len(session["questions"])) * 100)
        
        return session
    
    def generate_quiz_from_text(self, title, text_content, question_count=5):
        """
        Generate a quiz from text content.
        This is a placeholder - in a real implementation, this would use
        NLP or the AI core to generate questions.
        
        Args:
            title (str): Title for the quiz
            text_content (str): Text to generate questions from
            question_count (int): Number of questions to generate
            
        Returns:
            dict: Generated quiz
        """
        # Here we would use the AI to generate questions
        # For now, we'll just create a placeholder quiz
        quiz = self.create_quiz(title, f"Quiz generated from content: {title}", "auto-generated")
        
        # In a real implementation, we'd use AI to analyze the text and create questions
        # This is just a placeholder showing the structure
        self.add_question(
            quiz["id"],
            "What is the main purpose of this feature?",
            [
                "To demonstrate quiz functionality",
                "To test your knowledge",
                "To generate real questions from text",
                "To replace human-created quizzes"
            ],
            0,
            "This is just a placeholder showing the structure of auto-generated quizzes."
        )
        
        return quiz
    
    def _save_quiz(self, quiz):
        """
        Save a quiz to disk.
        
        Args:
            quiz (dict): Quiz to save
        """
        try:
            file_path = os.path.join(self.storage_dir, f"{quiz['id']}.json")
            
            with open(file_path, 'w') as file:
                json.dump(quiz, file, indent=2)
                
            self.logger.info(f"Saved quiz: {quiz['title']}")
        except Exception as e:
            self.logger.error(f"Error saving quiz: {e}")