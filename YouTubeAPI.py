# Packages

from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns
import openpyxl
from bs4 import BeautifulSoup

pd.set_option('display.max_columns', None)

api_key = 'VALID API KEY GOES HERE'
channel_ids = ['UCrPseYLGpNygVi34QpGNqpA']  # Ludwig's channel ID

youtube = build('youtube', 'v3', developerKey=api_key)


# Function to get channel statistics

def get_channel_stats(youtube, channel_ids):
    all_data = []
    request = youtube.channels().list(
        part='snippet,contentDetails,statistics',
        id=','.join(channel_ids))
    response = request.execute()

    for i in range(len(response['items'])):
        data = dict(Channel_name=response['items'][i]['snippet']['title'],
                    Playlist_id=response['items'][i]['contentDetails']['relatedPlaylists']['uploads'],
                    Subscribers=response['items'][i]['statistics']['subscriberCount'],
                    Views=response['items'][i]['statistics']['viewCount'],
                    Total_videos=response['items'][i]['statistics']['videoCount'], )
        all_data.append(data)

    return all_data


channel_statistics = get_channel_stats(youtube, channel_ids)
channel_data = pd.DataFrame(channel_statistics)

channel_data['Subscribers'] = pd.to_numeric(channel_data['Subscribers'])
channel_data['Views'] = pd.to_numeric(channel_data['Views'])
channel_data['Total_videos'] = pd.to_numeric(channel_data['Total_videos'])


# Function to get video IDs

playlist_id = channel_data.loc[channel_data['Channel_name'] == 'Ludwig', 'Playlist_id'].iloc[0]


def get_video_ids(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=50)
    response = request.execute()

    video_ids = []

    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])

    next_page_token = response.get('nextPageToken')
    more_pages = True

    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token)
            response = request.execute()

            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])

            next_page_token = response.get('nextPageToken')

    return video_ids


video_ids = get_video_ids(youtube, playlist_id)


# Function to get video details

def get_video_details(youtube, video_ids):
    all_video_stats = []

    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids[i:i + 50]))
        response = request.execute()

        for video in response['items']:
            video_stats = dict(Title=video['snippet']['title'],
                               Published_date=video['snippet']['publishedAt'],
                               Views=video['statistics']['viewCount'],
                               Likes=video['statistics']['likeCount'],
                               Comments=video['statistics']['commentCount'], )
            all_video_stats.append(video_stats)

    return all_video_stats


video_details = get_video_details(youtube, video_ids)
video_data = pd.DataFrame(video_details).sort_values('Published_date', ascending=True)
video_data.insert(0, 'Rolling_Video_Count', range(1, 1 + len(video_data)))



video_data['Published_date'] = pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
video_data['Views'] = pd.to_numeric(video_data['Views'])

Total_likes = video_data['Likes'].sum()
channel_data['Total_likes'] = Total_likes

top10_videos = video_data.sort_values(by='Views', ascending=False).head(10)

print(video_data)
print(channel_data)
print(top10_videos)

channel_data.to_csv('C:/Users/Relef/OneDrive/Desktop/channel_data.csv', index=False)
top10_videos.to_csv('C:/Users/Relef/OneDrive/Desktop/top10_videos_data.csv', index=False)
video_data.to_csv('C:/Users/Relef/OneDrive/Desktop/video_data.csv', index=False)