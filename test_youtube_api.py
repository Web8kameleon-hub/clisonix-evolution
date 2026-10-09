#!/usr/bin/env python3
"""Quick test of YouTube API integration"""
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load API key from .env file (NEVER hardcode secrets!)
load_dotenv()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

if not YOUTUBE_API_KEY:
    print("❌ ERROR: YOUTUBE_API_KEY not found in .env file")
    print("Add this to your .env file: YOUTUBE_API_KEY=your_key_here")
    exit(1)

try:
    # Initialize YouTube API client
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    # Test with a known video (Rick Astley - Never Gonna Give You Up)
    request = youtube.videos().list(
        part='snippet,statistics',
        id='dQw4w9WgXcQ'
    )
    response = request.execute()
    
    if response['items']:
        video = response['items'][0]
        print("✅ YouTube API CONNECTION SUCCESSFUL!\n")
        print(f"Title: {video['snippet']['title']}")
        print(f"Channel: {video['snippet']['channelTitle']}")
        print(f"Views: {int(video['statistics']['viewCount']):,}")
        print(f"Likes: {int(video['statistics']['likeCount']):,}")
        print(f"\n🎵 YouTube integration is ready!")
    else:
        print("⚠️ API works but no video found")
        
except Exception as e:
    print(f"❌ YouTube API Error: {e}")
    print("\nCheck:")
    print("1. API key is correct")
    print("2. YouTube Data API v3 is enabled")
    print("3. Quota not exceeded (10k requests/day)")

