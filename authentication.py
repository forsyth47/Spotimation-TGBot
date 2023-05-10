import requests
import json
import os
import time

playlisturl = "YOUR_PLAYLIST_LINK"
botkey = os.environ['botkey']
chatid = 'YOUR_TG_CHAT_ID'

def get_stoken():
	#auth_code=str(input("Enter code: "))
	auth_url = 'https://accounts.spotify.com/api/token'
	payload = {
	    'client_id': '5f573c9620494bae87890c0f08a60293',
	    'client_secret': '212476d9b0f3472eaa762d90b19b0ba8',
	    ##################################
	#    'grant_type': 'authorization_code',
	#    'code': auth_code,
	#    'redirect_uri': 'https://example.com'
	    ##################################
	    "grant_type": "client_credentials"
	}
	while True:
		###for authorization_code###
		#response = requests.post(auth_url, data=payload)
		###for client_credentials###
		response = requests.post(auth_url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
		access_token = response.json()['access_token']
		if access_token:
			with open('keys.json','w') as f:
				data = {'skey': access_token, 'botkey': botkey, 'chatid': chatid, 'playlisturl': playlisturl}
				json.dump(data, f, indent=4)
			break
		time.sleep(5)


