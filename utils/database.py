import sqlite3
from datetime import datetime


class InstagramCache:
    def __init__(self, db_name):
        self.db = db_name
        self.conn = sqlite3.connect(self.db)
        self.cursor = self.conn.cursor()

    def SaveStory(self, storyId, storyHash, username, storyTime,):
        save_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_query = f"INSERT INTO stories VALUES ('{storyId}', '{storyHash}', '{username}', '{storyTime}', '{save_time}')"
        self.cursor.execute(save_query)
        self.conn.commit()

    def FetchStoryById(self, storyId):
        fetch_query = f"SELECT * FROM stories WHERE storyId = '{storyId}'"
        self.cursor.execute(fetch_query)
        return self.cursor.fetchone()