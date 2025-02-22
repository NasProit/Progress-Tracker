import json
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.users_file = "users.json"
        self.progress_file = "progress.json"
        self._initialize_storage()

    def _initialize_storage(self):
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({"admin": {"password": "admin123", "role": "admin"}}, f)

        if not os.path.exists(self.progress_file):
            with open(self.progress_file, 'w') as f:
                json.dump({}, f)

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

    def save_progress(self, username, course, progress):
        with open(self.progress_file, 'r') as f:
            all_progress = json.load(f)
        
        if username not in all_progress:
            all_progress[username] = {}
        
        all_progress[username][course] = {
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
