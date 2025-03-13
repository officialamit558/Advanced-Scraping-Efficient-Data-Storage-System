import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Replace with your API key obtained from Google Cloud Console
API_KEY = "AIzaSyAVw38ZD3JV7Q0CuH0Xs9z32-ENRWZFWeI"

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey=API_KEY)

def scrape_youtube_data(video_id):
    """
    Scrapes YouTube video data including title, description, statistics, and comments using the YouTube Data API.

    Args:
        video_id (str): The unique ID of the YouTube video.

    Returns:
        dict: A dictionary containing the video title, description, stats, and comments.
    """
    try:
        # Get video details (snippet and statistics)
        video_details = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()

        if not video_details["items"]:
            raise ValueError(f"No video found with ID: {video_id}")

        # Extract video details
        video_info = video_details["items"][0]
        title = video_info["snippet"]["title"]
        description = video_info["snippet"]["description"]
        stats = video_info["statistics"]  # Includes viewCount, likeCount, etc.

        # Get video comments (if comments are enabled)
        comments = []
        try:
            next_page_token = None
            while True:
                comment_response = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    pageToken=next_page_token,
                    maxResults=100  # Max results per page (adjust as needed)
                ).execute()

                for item in comment_response["items"]:
                    comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                    comments.append(comment_text)

                next_page_token = comment_response.get("nextPageToken")
                if not next_page_token:
                    break
        except HttpError as e:
            if "commentsDisabled" in str(e):
                print("Comments are disabled for this video.")
            else:
                print(f"Error fetching comments: {e}")

        return {
            "title": title,
            "description": description,
            "statistics": stats,
            "comments": comments
        }

    except HttpError as e:
        print(f"An error occurred while fetching video details: {e}")
        return None

def save_to_txt(data, filename="youtube_data.txt"):
    """
    Saves the scraped YouTube data to a .txt file.

    Args:
        data (dict): The dictionary containing video data.
        filename (str): The name of the file to save the data to.
    """
    if not data:
        print("No data to save.")
        return

    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Title: {data['title']}\n")
        file.write(f"Description: {data['description']}\n\n")
        
        file.write("Statistics:\n")
        for key, value in data['statistics'].items():
            file.write(f"  {key}: {value}\n")
        
        file.write("\nComments:\n")
        if data['comments']:
            for i, comment in enumerate(data['comments'], 1):
                file.write(f"  {i}. {comment}\n")
        else:
            file.write("  No comments available.\n")

    print(f"Data saved to {filename}")

# Example usage
if __name__ == "__main__":
    # Replace with the video ID (e.g., "dQw4w9WgXcQ" for Rick Astley's "Never Gonna Give You Up")
    video_id = "GNZBSZD16cY"
    
    # Scrape the data
    data = scrape_youtube_data(video_id)
    
    # Save the data to a .txt file
    if data:
        save_to_txt(data, "youtube_data.txt")