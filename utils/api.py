class API:
    def __init__(self):
        self.base = "https://i.instagram.com/api/v1"
        self.UserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599"

    def GetStories(self):
        return f"{self.base}/feed/reels_tray/"

    def GetMediaById(self, id):
        return f"{self.base}/media/{id}/info/"

    def GetStoryByUserIds(self, ids):
        query = ""
        for userId in ids:
            query += f"reel_ids={userId}&"

        return f"{self.base}/feed/reels_media/?{query}"

    def MakeHeaders(self, Cookies):
        return {
            "User-Agent": self.UserAgent,
            "cookie": f"ds_user_id={Cookies['userId']}; sessionid={Cookies['sessionId']}; csrftoken={Cookies['csrftoken']}"
        }
