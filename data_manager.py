import json
import os
import pandas as pd
from datetime import datetime

class DataManager:
    def __init__(self):
        self.users_file = "users.json"
        self.progress_file = "progress.json"
        self.topics_file = "topics.json"
        self.logo_path = "assets/logo.png"
        self._initialize_storage()

    def _initialize_storage(self):
        # Initialize users with admin credentials for Nasir
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({
                    "Nasir": {
                        "password": "8a5f32b3c46ef1d9f8b2e3f4a7c6d5b2",  # Hashed "125Nasir"
                        "role": "admin"
                    }
                }, f)

        # Ensure admin user exists even if file exists
        else:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            if "Nasir" not in users:
                users["Nasir"] = {
                    "password": "8a5f32b3c46ef1d9f8b2e3f4a7c6d5b2",  # Hashed "125Nasir"
                    "role": "admin"
                }
                with open(self.users_file, 'w') as f:
                    json.dump(users, f)

        if not os.path.exists(self.progress_file):
            with open(self.progress_file, 'w') as f:
                json.dump({}, f)

        if not os.path.exists(self.topics_file):
            with open(self.topics_file, 'w') as f:
                json.dump({
                    "topics": {},
                    "last_updated": None
                }, f)

        if not os.path.exists("assets"):
            os.makedirs("assets")

    def save_user(self, username, password, role="student"):
        with open(self.users_file, 'r') as f:
            users = json.load(f)
        users[username] = {"password": password, "role": role}
        with open(self.users_file, 'w') as f:
            json.dump(users, f)

    def get_user(self, username):
        with open(self.users_file, 'r') as f:
            users = json.load(f)
        return users.get(username)

    def save_progress(self, username, topic, subtopic, progress):
        with open(self.progress_file, 'r') as f:
            all_progress = json.load(f)

        if username not in all_progress:
            all_progress[username] = {}

        if topic not in all_progress[username]:
            all_progress[username][topic] = {}

        all_progress[username][topic][subtopic] = {
            "progress": progress,
            "timestamp": datetime.now().isoformat()
        }

        with open(self.progress_file, 'w') as f:
            json.dump(all_progress, f)

    def get_student_progress(self, username):
        with open(self.progress_file, 'r') as f:
            all_progress = json.load(f)
        return all_progress.get(username, {})

    def get_all_progress(self):
        with open(self.progress_file, 'r') as f:
            return json.load(f)

    def save_topics_from_csv(self, csv_content):
        try:
            df = pd.read_csv(csv_content)
            topics_dict = {}

            for _, row in df.iterrows():
                topic = row['Topic']
                subtopic = row['Subtopic']
                if topic not in topics_dict:
                    topics_dict[topic] = []
                topics_dict[topic].append(subtopic)

            with open(self.topics_file, 'w') as f:
                json.dump({
                    "topics": topics_dict,
                    "last_updated": datetime.now().isoformat()
                }, f)
            return True
        except Exception as e:
            print(f"Error saving topics: {str(e)}")
            return False

    def get_topics(self):
        with open(self.topics_file, 'r') as f:
            data = json.load(f)
        return data.get("topics", {})

    def save_logo(self, logo_file):
        try:
            if not os.path.exists("assets"):
                os.makedirs("assets")
            logo_path = os.path.join("assets", "logo.png")
            with open(logo_path, "wb") as f:
                f.write(logo_file.getvalue())
            return True
        except Exception as e:
            print(f"Error saving logo: {str(e)}")
            return False