import requests
import json
import os
import time
 
#=========VARIABLES=============
Telegram_BotKey = os.environ['Telegram_BotKey']
Telegram_ChatId = os.environ['Telegram_ChatId']

Spotify_PlaylistUrl = os.environ['Spotify_PlaylistUrl']
Spotify_ClientId = os.environ['Spotify_ClientId']
Spotify_ClientSecret = os.environ['Spotify_ClientSecret']
Spotify_PlaylistId = Spotify_PlaylistUrl.split('playlist/')[1].split('?')[0]
#=========VARIABLES-END=========

def Spotify_PlaylistInfo(Spotify_PlaylistId, access_token):
  endpoint = f"https://api.spotify.com/v1/playlists/{Spotify_PlaylistId}"
  headers = {"Authorization": f"Bearer {access_token}"}

  try:
      response = requests.get(endpoint, headers=headers)
      response.raise_for_status()
      playlist_data = response.json()
      return playlist_data['name'], playlist_data['owner']['display_name']
  except requests.exceptions.RequestException as e:
      return None, None


def getSpotfyAccessToken():
  auth_url = 'https://accounts.spotify.com/api/token'
  payload = {
      'client_id': Spotify_ClientId,
      'client_secret': Spotify_ClientSecret,
      ##################################
      # 'grant_type': 'authorization_code',
      # 'code': auth_code,
      # 'redirect_uri': 'https://example.com'
      ##################################
      "grant_type": "client_credentials"
  }
  while True:
    #========== for authorization_code ==========#
    # response = requests.post(auth_url, data=payload)
    
    #========== for client_credentials ==========#
    response = requests.post(auth_url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
    access_token = response.json()['access_token']
    Spotify_PlaylistName, Spotify_PlaylistUserName = Spotify_PlaylistInfo(Spotify_PlaylistId, access_token)
    if access_token:
      with open('keys.json','w') as f:
        data = {'spotfyAccessToken': access_token, 'Telegram_BotKey': Telegram_BotKey, 'Telegram_ChatId': Telegram_ChatId, 'Spotify_PlaylistUrl': Spotify_PlaylistUrl, 'Spotify_PlaylistId': Spotify_PlaylistId, 'Spotify_PlaylistName': Spotify_PlaylistName, 'Spotify_PlaylistUserName': Spotify_PlaylistUserName}
        json.dump(data, f, indent=4)
      break
    time.sleep(5)


