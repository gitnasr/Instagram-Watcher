import time
from datetime import datetime, timedelta

import schedule
from threading import Thread

from requests.adapters import HTTPAdapter, Retry
from requests import Session
from termcolor import cprint

from utils.api import API
from utils.cookies import Cookies
from utils.database import InstagramCache
from utils.images import Images
from colorama import init
init(convert=True)

class Stroies:
    def __init__(self):
        
        self.Cookies = Cookies("instagram.com")
        self.API = API()
        self.Images = Images()
        self.Database = InstagramCache("stories.db")
        self.Session = Session()
        self.Headers = self.PrepareHeaders()
        self.retries = Retry(total=5, backoff_factor=1, )
        self.Session.mount('https://', HTTPAdapter(max_retries=self.retries))


        self.Run()

    def PrepareHeaders(self):
        userId = self.Cookies.get("ds_user_id")
        csrftoken = self.Cookies.get("csrftoken")
        sessionId = self.Cookies.get("sessionid")

        cookies = {
            "userId": userId,
            "csrftoken": csrftoken,
            "sessionId": sessionId
        }

        return self.API.MakeHeaders(cookies)

    def GetStories(self):
        stories_url = self.API.GetStories()
        stories = self.Session.get(stories_url, headers=self.Headers).json()

        return stories

    def GetStoriesByUserIds(self, userIds):
        storiesUrl = self.API.GetStoryByUserIds(userIds)
        stories = self.Session.get(storiesUrl, headers=self.Headers).json()

        if stories.get("reels") is None:
            cprint("No stories found", "red")
            return

        return stories

    def StoriesParser(self, stories):
        final_stories = []

        for story in stories["reels"]:
            for story_item in stories["reels"][story]['items']:
                story_items = self.StoryParser(story_item)
                if story_items.get("storyType") == 1:
                    story_items.update(
                        {"storyUserId": story, "storyUsername": stories["reels"][story]['user']['username']})
                    final_stories.append(story_items)
        return final_stories

    def FilterAndHandleStories(self):
        stories = self.GetStories()

        if stories.get("tray") is None:
            cprint("No stories found", "red")
            return
        userIds = []
        for story in stories["tray"]:
            storyUserId = story['id']

            for media in story['media_ids']:
                storyId = f"{media}_{storyUserId}"

                if self.Database.FetchStoryById(storyId):
                    continue
                else:
                    userIds.append(storyUserId)
                    
        userIds = list(set(userIds))
        new_stories = 0
        if len(userIds) > 30:
            for i in range(0, len(userIds), 30):
                stories = self.GetStoriesByUserIds(userIds[i:i + 30])
                stories = self.StoriesParser(stories)
                for story in stories:
                    isNew = self.SaveStory(story)
                    if isNew:
                        new_stories += 1
                        cprint(f"New story from {story['storyUsername']}", "green")
        else:
            stories = self.GetStoriesByUserIds(userIds)
            stories = self.StoriesParser(stories)
            for story in stories:
                isNew = self.SaveStory(story)
                if isNew:
                    new_stories += 1
                    cprint(f"New story from {story['storyUsername']}", "green")
        cprint(f"Task ended with {new_stories} new stories @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "yellow")

    def SaveStory(self, story):
        if story and self.Database.FetchStoryById(f"{story['storyId']}") is None:
            hash = self.Images.HashRemote(story["storyUrl"])
            Thread(target=self.Images.SaveImage,
                   args=(
                       story["storyUrl"], story["storyUsername"], story["storyId"], story["storyTime"])).start()
            self.Database.SaveStory(story['storyId'], hash, story["storyUsername"], story["storyTime"])
            return True
        return False

    def StoryParser(self, story):
        storyType = story["media_type"]

        storyUrl = story["image_versions2"]["candidates"][0]["url"]
        storyId = story["id"]
        storyTime = story["taken_at"]
        return {
            "storyType": storyType,
            "storyUrl": storyUrl,
            "storyId": storyId,
            "storyTime": storyTime,

        }

    def Run(self):
        cprint("Task started @ " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "yellow")
        self.FilterAndHandleStories()


if __name__ == '__main__':
    Stroies()
    schedule.every(30).minutes.do(Stroies)
    while True:
        schedule.run_pending()
        n = schedule.idle_seconds()
        x = datetime.now() + timedelta(seconds=n)
        cprint(f"Next task will run at {x.strftime('%Y-%m-%d %H:%M:%S')}", "yellow")
        time.sleep(n)
