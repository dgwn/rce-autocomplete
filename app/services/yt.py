
import os
import googleapiclient.discovery
import json
from dotenv import load_dotenv

load_dotenv()


def youtube(query: str):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.getenv("YOUTUBE_API_KEY") 
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video"
    )
    response = request.execute()
    items = response["items"]

    videos_info = {
        "videos": []
    }

    for item in items:
        snippet = item["snippet"]
        print("item idddd: ", item["id"])
        video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        video_info = {
            "title": snippet["title"],
            "description": snippet["description"],
            "channel_title": snippet["channelTitle"],
            "thumbnail": snippet["thumbnails"]["high"]["url"],
            "publish_time": snippet["publishTime"],
            "video_url": video_url
        }
        videos_info["videos"].append(video_info)

    return videos_info