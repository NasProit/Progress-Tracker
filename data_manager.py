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
        # Initialize users with admin credentials for MdNasir
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({
                    "MdNasir": {
                        "password": "8a5f32b3c46ef1d9f8b2e3f4a7c6d5b2",  # Hashed "125Nasir"
                        "role": "admin"
                    }
                }, f)

        # Ensure admin user exists with correct credentials
        with open(self.users_file, 'r') as f:
            users = json.load(f)
        users["MdNasir"] = {
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

    def add_topic(self, topic_name):
        with open(self.topics_file, 'r') as f:
            data = json.load(f)

        if topic_name not in data["topics"]:
            data["topics"][topic_name] = []
            data["last_updated"] = datetime.now().isoformat()

            with open(self.topics_file, 'w') as f:
                json.dump(data, f)
            return True
        return False

    def add_subtopic(self, topic_name, subtopic_name):
        with open(self.topics_file, 'r') as f:
            data = json.load(f)

        if topic_name in data["topics"] and subtopic_name not in data["topics"][topic_name]:
            data["topics"][topic_name].append(subtopic_name)
            data["last_updated"] = datetime.now().isoformat()

            with open(self.topics_file, 'w') as f:
                json.dump(data, f)
            return True
        return False

    def remove_topic(self, topic_name):
        with open(self.topics_file, 'r') as f:
            data = json.load(f)

        if topic_name in data["topics"]:
            del data["topics"][topic_name]
            data["last_updated"] = datetime.now().isoformat()

            with open(self.topics_file, 'w') as f:
                json.dump(data, f)
            return True
        return False

    def remove_subtopic(self, topic_name, subtopic_name):
        with open(self.topics_file, 'r') as f:
            data = json.load(f)

        if topic_name in data["topics"] and subtopic_name in data["topics"][topic_name]:
            data["topics"][topic_name].remove(subtopic_name)
            data["last_updated"] = datetime.now().isoformat()

            with open(self.topics_file, 'w') as f:
                json.dump(data, f)
            return True
        return False

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