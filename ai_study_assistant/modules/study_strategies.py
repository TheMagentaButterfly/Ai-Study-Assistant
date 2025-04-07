"""
Study strategies module implementing effective learning techniques.
"""
import random
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class StudyStrategies:
    """
    Provides study strategies and techniques to improve learning.
    """
    
    def __init__(self):
        """Initialize the study strategies module."""
        # Load study tips and techniques from research
        self._load_study_strategies()
        
        # Initialize text vectorizer for matching content to study tips
        self.vectorizer = TfidfVectorizer(stop_words='english')
        # Vectorize the study tips for similarity matching
        study_texts = [tip['description'] for category in self.strategies.values() 
                      for tip in category]
        if study_texts:
            self.tip_vectors = self.vectorizer.fit_transform(study_texts)
        else:
            self.tip_vectors = None
        
    def _load_study_strategies(self):
        """Load evidence-based study strategies."""
        self.strategies = {
            "general": [
                {
                    "title": "Spaced Repetition",
                    "description": "Space out your studying over time instead of cramming. Review material at increasing intervals.",
                    "implementation": "Study a topic, then review it 1 day later, then 3 days later, then a week later.",
                    "research": "Research shows spaced learning is more effective than massed practice (cramming)."
                },
                {
                    "title": "Retrieval Practice",
                    "description": "Actively recall information rather than simply re-reading it. Test yourself frequently.",
                    "implementation": "After reading, close your book and write down everything you remember.",
                    "research": "Studies show that the act of retrieving knowledge strengthens memory more than re-exposure to the material."
                },
                {
                    "title": "Interleaving",
                    "description": "Mix different topics or types of problems within a study session rather than focusing on one topic at a time.",
                    "implementation": "Instead of studying one math concept for an hour, study three different concepts for 20 minutes each.",
                    "research": "Interleaving improves long-term retention and transfer of knowledge."
                },
                {
                    "title": "Elaboration",
                    "description": "Explain concepts in your own words and connect them to things you already know.",
                    "implementation": "Create analogies, teach concepts to others, or pretend you're explaining to someone who knows nothing about the topic.",
                    "research": "Elaboration creates richer connections between new information and existing knowledge."
                },
                {
                    "title": "Dual Coding",
                    "description": "Combine verbal materials with visuals to enhance learning.",
                    "implementation": "Draw diagrams, create mind maps, or visualize concepts while studying text-based material.",
                    "research": "Processing information in multiple formats strengthens memory encoding."
                }
            ],
            "focus": [
                {
                    "title": "Pomodoro Technique",
                    "description": "Work in focused bursts (typically 25 minutes) followed by short breaks (5 minutes).",
                    "implementation": "Set a timer for 25 minutes of focused work, then take a 5-minute break. After four cycles, take a longer 15-30 minute break.",
                    "research": "Helps maintain high concentration and prevents mental fatigue."
                },
                {
                    "title": "Digital Detox",
                    "description": "Eliminate digital distractions during study time.",
                    "implementation": "Put your phone in another room, use website blockers, or turn off notifications.",
                    "research": "Research shows that even the presence of a phone can reduce cognitive capacity."
                },
                {
                    "title": "Environment Design",
                    "description": "Create a consistent study environment that signals your brain it's time to focus.",
                    "implementation": "Designate a specific location for studying that's free from distractions and contains all necessary materials.",
                    "research": "Environmental cues can trigger productivity states through classical conditioning."
                }
            ],
            "memory": [
                {
                    "title": "Memory Palace (Method of Loci)",
                    "description": "Associate items to remember with specific locations in a familiar place.",
                    "implementation": "Visualize walking through your home and placing items to remember in specific locations.",
                    "research": "Spatial memory can be leveraged to enhance recall of non-spatial information."
                },
                {
                    "title": "Chunking",
                    "description": "Group individual pieces of information into larger units to improve memory capacity.",
                    "implementation": "Remember phone numbers in groups of 3-4 digits, or categorize vocabulary words by theme.",
                    "research": "Organizing information into meaningful groups helps overcome working memory limitations."
                },
                {
                    "title": "Mnemonic Devices",
                    "description": "Create associations, acronyms, or rhymes to remember information.",
                    "implementation": "For the order of planets: 'My Very Eager Mother Just Served Us Nachos' (Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune).",
                    "research": "Mnemonics provide memory cues and organization that improve recall."
                }
            ],
            "note_taking": [
                {
                    "title": "Cornell Note-Taking System",
                    "description": "Divide your notes into main points, details, and summary sections.",
                    "implementation": "Draw a vertical line 1/3 from the left edge of your paper. Take notes on the right, write main points/questions on the left, and summarize at the bottom.",
                    "research": "Organizes information hierarchically and promotes active engagement."
                },
                {
                    "title": "Mind Mapping",
                    "description": "Create visual diagrams that show relationships between concepts.",
                    "implementation": "Place the main concept in the center and branch out with related ideas, using colors and images.",
                    "research": "Visual mapping helps reveal connections between ideas and improves conceptual understanding."
                }
            ],
            "exam_prep": [
                {
                    "title": "Practice Testing",
                    "description": "Take practice tests under exam-like conditions.",
                    "implementation": "Use past papers, create your own tests, or use flashcards to simulate test conditions.",
                    "research": "One of the most effective study techniques according to cognitive science research."
                },
                {
                    "title": "Feynman Technique",
                    "description": "Explain concepts in simple language as if teaching someone else.",
                    "implementation": "Choose a concept, explain it in simple terms, identify gaps in understanding, review and simplify further.",
                    "research": "Forcing yourself to explain a concept reveals what you don't fully understand."
                },
                {
                    "title": "Distributed Practice",
                    "description": "Spread out study sessions over time rather than cramming.",
                    "implementation": "Study for shorter periods (30-60 minutes) over several days or weeks instead of one long session.",
                    "research": "Distributed practice is more effective for long-term retention than massed practice."
                }
            ]
        }
    
    def get_tips(self, category="general", count=3):
        """
        Get study tips from a specific category.
        
        Args:
            category (str): Category of tips to retrieve
            count (int): Number of tips to return
            
        Returns:
            list: List of study tips
        """
        if category not in self.strategies:
            category = "general"
            
        tips = self.strategies[category]
        
        # Return random selection if more tips are available than requested
        if len(tips) > count:
            return random.sample(tips, count)
        return tips
    
    def get_related_tips(self, content, count=2):
        """
        Get study tips related to the content of a message.
        
        Args:
            content (str): Text content to match with tips
            count (int): Number of tips to return
            
        Returns:
            list: List of related study tips
        """
        if not content or not self.tip_vectors:
            return self.get_tips(count=count)
            
        # Vectorize the content
        try:
            content_vector = self.vectorizer.transform([content])
            
            # Calculate similarity with all tips
            similarity_scores = cosine_similarity(content_vector, self.tip_vectors)[0]
            
            # Get indices of the most similar tips
            top_indices = similarity_scores.argsort()[-count:][::-1]
            
            # Flatten the strategies for easy indexing
            all_tips = [tip for category in self.strategies.values() for tip in category]
            
            # Return the most relevant tips
            relevant_tips = [all_tips[i] for i in top_indices]
            return relevant_tips
        except Exception:
            # Fall back to random tips if there's an error
            return self.get_tips(count=count)
    
    def generate_study_plan(self, subject, duration_days, hours_per_day):
        """
        Generate a study plan for a specific subject.
        
        Args:
            subject (str): Subject to study
            duration_days (int): Duration of the study plan in days
            hours_per_day (float): Hours to study per day
            
        Returns:
            dict: Study plan with daily activities
        """
        # Sample study activities
        activities = [
            "Review previous material using retrieval practice",
            "Learn new concepts through active reading",
            "Practice problem-solving with exercises",
            "Create summary notes/mind maps",
            "Take practice quizzes/tests",
            "Teach concepts to others (or explain out loud)",
            "Apply knowledge to real-world examples",
            "Review and correct mistakes from practice tests"
        ]
        
        # Create a plan
        plan = {
            "subject": subject,
            "duration_days": duration_days,
            "hours_per_day": hours_per_day,
            "total_hours": duration_days * hours_per_day,
            "daily_plan": []
        }
        
        # Generate daily activities
        for day in range(1, duration_days + 1):
            # Calculate hours for each activity
            num_activities = min(3, round(hours_per_day))
            hours_per_activity = round(hours_per_day / num_activities, 1)
            
            # Select activities for the day
            daily_activities = random.sample(activities, num_activities)
            
            # Add spaced repetition on certain days
            if day > 1 and day % 3 == 0:
                daily_activities[0] = "Review material from previous days (spaced repetition)"
                
            # Create daily plan
            daily_plan = {
                "day": day,
                "activities": [
                    {"activity": activity, "duration_hours": hours_per_activity}
                    for activity in daily_activities
                ],
                "tips": self.get_tips(random.choice(list(self.strategies.keys())), 1)
            }
            
            plan["daily_plan"].append(daily_plan)
        
        return plan