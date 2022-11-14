import hashlib
import os
from datetime import datetime
from urllib.request import urlopen


class Images:
    def HashRemote(self,url):
        hash = hashlib.sha512()
        total_read = 0
        max_file_size = 100 * 1024 * 1024
        data = urlopen(url).read(4096)
        while True:
            total_read += 4096

            if not data or total_read > max_file_size:
                break

            hash.update(data)

        return hash.hexdigest()

    def SaveImage(self, url, username, storyId, storyTime):
        save_folder = f"output/stories/{datetime.now().strftime('%Y-%m-%d')}"
        file_save_path = f"{save_folder}/{username}_{storyTime}_{storyId}.jpg"
        if not os.path.exists(file_save_path):
            os.makedirs(save_folder, exist_ok=True)

        with open(file_save_path, "wb") as f:
            f.write(urlopen(url).read())
            f.close()

