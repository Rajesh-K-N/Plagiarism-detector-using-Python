import os
import requests
import time
import re
from difflib import SequenceMatcher

class PlagiarismChecker:
    def __init__(self, similarity_threshold=0.75, db_file="plagiarism_db.txt", serpapi_key="fcd6a1e749c3dc5632b2e2cac1dc8180503d1a061524d42b69a50e70327f6c67"):
        self.database = set()
        self.similarity_threshold = similarity_threshold
        self.db_file = db_file
        self.serpapi_key = serpapi_key
        self.load_database()

    def load_database(self):
        """Load previously checked documents from a file into a set."""
        if os.path.exists(self.db_file):
            with open(self.db_file, "r", encoding="utf-8") as file:
                self.database = set(line.strip() for line in file.readlines())

    def save_to_database(self, text):
        """Append new text to the file-based database."""
        with open(self.db_file, "a", encoding="utf-8") as file:
            file.write(text + "\n")

    def add_to_database(self, text):
        cleaned_text = self.clean_text(text)
        if cleaned_text not in self.database:
            self.database.add(cleaned_text)
            self.save_to_database(cleaned_text)

    def check_plagiarism(self, text):
        """Check for plagiarism locally and online."""
        cleaned_text = self.clean_text(text)

        # Step 1: Check Local Database
        for stored_text in self.database:
            similarity = self.calculate_similarity(cleaned_text, stored_text)
            if similarity >= self.similarity_threshold:
                return f"❌ Plagiarized! Similarity: {similarity:.2f}"

        # Step 2: Check Online Using SerpAPI (Google Search)
        print(f"🔍 Searching online for: {text[:50]}...")
        if self.search_online(text):
            return "❌ Plagiarized! Found similar content online."
        
        return "✅ Unique! No matches found online."

    def search_online(self, text, retries=3):
        """Uses SerpAPI to check if the text is found online."""
        url = "https://serpapi.com/search"
        params = {
            "q": text,
            "api_key": self.serpapi_key,
            "num": 5,
            "engine": "google"
        }
        
        for attempt in range(retries):
            try:
                response = requests.get(url, params=params, timeout=10)
                data = response.json()

                # If results exist, assume plagiarism
                if "organic_results" in data and data["organic_results"]:
                    return True  # Plagiarized

                return False  # Unique
            except Exception as e:
                print(f"⚠️ Error in online search (Attempt {attempt+1}): {e}")
                time.sleep(2)  # Retry after a short delay
        
        return False  # Assume unique if API fails

    def clean_text(self, text):
        """Preprocess text: remove special characters and lowercase it."""
        return re.sub(r"[^a-zA-Z0-9\s]", "", text).lower().strip()

    def calculate_similarity(self, text1, text2):
        """Use Levenshtein similarity for more accurate plagiarism detection."""
        return SequenceMatcher(None, text1, text2).ratio()

# Initialize the plagiarism checker
plagiarism_checker = PlagiarismChecker(serpapi_key="fcd6a1e749c3dc5632b2e2cac1dc8180503d1a061524d42b69a50e70327f6c67")

while True:
    user_text = input("\nEnter your text (or type 'exit' to quit): ").strip()
    if user_text.lower() == "exit":
        print("Exiting plagiarism checker...")
        break

    result = plagiarism_checker.check_plagiarism(user_text)
    print(result)

    # Add new text to the database after checking
    plagiarism_checker.add_to_database(user_text)
