# pip install -U --force spotdl pytz
# pip install python-telegram-bot==13.15 pytz spotdl
# ffmpeg

import requests
import json
import re
import os
from authentication import getSpotfyAccessToken
import telegram
from telegram.ext import *
import subprocess
import time
from datetime import datetime
import pytz
from webserver import keep_alive

if not os.path.exists('keys.json'):
  getSpotfyAccessToken()
with open('keys.json', 'r') as f:
    keysdata = json.load(f)

def start_command(update, context):
  Spotify_PlaylistUserName_Clean = re.sub(r'\W+', ' ', keysdata['Spotify_PlaylistUserName'])
  
  Spotify_PlaylistName_Clean = re.sub(r'\W+', ' ', keysdata['Spotify_PlaylistName'])
  
  Spotify_PlaylistUrl_Clean = keysdata['Spotify_PlaylistUrl'].strip("'")
  print(f"THIS IS CLEANED NAME: {Spotify_PlaylistUserName_Clean}")
  update.message.reply_text(
      f"***\\(✿◠‿◠\\) BOT IS ACTIVE***\n\nLinked to the playlist ***[[{Spotify_PlaylistName_Clean}]({Spotify_PlaylistUrl_Clean})]*** from user ***{Spotify_PlaylistUserName_Clean}*** and to the following chat id ***[{update.message.from_user.name}](tg://user?id={os.environ['Telegram_ChatId']})***\n\nUse /c command to clear music cache from server\\.",
    parse_mode="MarkdownV2",
  )

def clear_c(update, context):
  if int(update.message.chat_id) == int(keysdata['Telegram_ChatId']):
    subprocess.run('cd Music && rm -rf *.mp3', shell=True)
    update.message.reply_text('Cache is cleared!')
  else:
    update.message.reply_text('Unauthorized access!')
  
# Log errors
def error(update, context):
  nowx = datetime.now(pytz.timezone(f"{os.environ['Timezone']}"))
  global errorout
  errorout = (nowx.strftime("[%d/%m/%Y %H:%M:%S] "), f'Update {update} caused error {context.error}')
  print(errorout)

def errorLogManual(e):
  print(f"An error occurred: {e}")
  with open ('error.txt', 'a+') as f:
    f.write(datetime.now(pytz.timezone(f"{os.environ['Timezone']}")).strftime("[%d/%m/%Y %H:%M:%S] "))
    f.write(f"An error occurred: {e}")
    f.write(str(data))
    f.write('\n' * 5)

def autoCleanOldSongs():
  # Delete Old songs, clearing space for new onw.
  path = "Music"  # replace with your directory path
  threshold_size = 700 * 1024 * 1024  # 700 MB in bytes
  files = []

  # check total size of directory
  total_size = sum(os.path.getsize(os.path.join(path, f)) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
  if total_size > threshold_size:
      # get list of files in directory
    for file in os.listdir(path):
      file_path = os.path.join(path, file)
      if os.path.isfile(file_path):
        files.append((file_path, os.path.getmtime(file_path)))  # store file path and modified time

      # sort files by oldest first
    files.sort(key=lambda x: x[1])

      # delete first 25 files
    for i in range(25):
      if files:
        file_path = files.pop(0)[0]
        os.remove(file_path)
      else:
        break
  else:
    pass


# Run the program #use_context=True,
if __name__ == '__main__':
  with open('keys.json', 'r') as f:
    keysdata = json.load(f)
  Telegram_BotKey = keysdata['Telegram_BotKey']
  updater = Updater(Telegram_BotKey, use_context=True)
  dp = updater.dispatcher
  keep_alive()
  print('====================BOT-STARTED====================')

  # Commands
  dp.add_handler(CommandHandler('start', start_command))
  dp.add_handler(CommandHandler('c', clear_c))

  # Log all errors
  dp.add_error_handler(error)

  # Run the bot
  updater.start_polling(1.0)

  while True:
    bot = telegram.Bot(token=Telegram_BotKey)
    Spotify_PlaylistUrl = keysdata['Spotify_PlaylistUrl']
    playlistid = re.search(r"playlist/([a-zA-Z0-9]+)", Spotify_PlaylistUrl).group(1)
    url = f"https://api.spotify.com/v1/playlists/{playlistid}/tracks"
    chat_id = keysdata['Telegram_ChatId']
    apidata = []
    
    while True:
      try:
        getSpotfyAccessToken()
        with open('keys.json', 'r') as f:
          keysdata = json.load(f)
          spotfyAccessToken = keysdata['spotfyAccessToken']
        response = requests.get(url, headers={"Authorization": f"Bearer {spotfyAccessToken}"})
        data = response.json()
        apidata.extend(data['items'])
        if data['next'] is not None:
          url = data['next']
        else:
          break
      except Exception as e:
        errorLogManual(e)
        time.sleep(5)
    if not os.path.exists('localdata.json'):
      with open('localdata.json', 'w') as f:
        json.dump({"sent": []}, f)
    if not os.path.exists('Music'):
      os.mkdir('Music')
    with open('localdata.json', 'r') as f:
        localdata = json.load(f)
  
    localsong = [lsong['name'] for lsong in localdata['sent']]
    apisong = [asong['track']['name'] for asong in apidata]
    print('No. of songs in API:', len(apisong))
    print('No. of songs in Local: ',len(localsong))
    for song in apisong:
      if song not in localsong:
        sentmessage = bot.sendMessage(chat_id=chat_id, text=f"Adding <b>{song}!</b> It exists in Spotify but not in Local database.", parse_mode='html')
        print("Adding! '{0:<50}' exists in Spotify but not in Local database.".format(song))
        for asong in apidata:
          if song == asong['track']['name']:
            try:
              subprocess.run('cd Music && spotdl --config ' + asong['track']['external_urls']['spotify'], shell=True)
            except:
              bot.sendMessage(chat_id=chat_id, text=f'Unable to Add <b>{song}</b> due to system error! \nMight wanna remove that one from your Spotify playlist to prevent unexpected errors.', parse_mode='html')
            fname = subprocess.run(f"cd Music && find . -maxdepth 1 -type f -iname '*{song}*' -printf '%f\n' | grep -i '{song}' | head -n 1", shell=True, capture_output=True, text=True).stdout.strip()
            if len(fname)==0:
              fname = subprocess.run("cd Music && ls -t | head -n 1", shell=True, capture_output=True, text=True).stdout.strip()
            sentaudio = bot.sendAudio(chat_id=chat_id, audio=open(f'Music/{fname}', 'rb'))
            item = {"name": asong['track']['name'], "link": asong['track']['external_urls']['spotify'], "messageid": sentaudio.message_id, "addedon": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("[%d/%m/%Y %H:%M:%S] ")}
            localdata["sent"].append(item)
            with open('localdata.json', 'w') as f:
              json.dump(localdata, f, indent=4, ensure_ascii=False)
            bot.delete_message(chat_id=chat_id, message_id=sentmessage.message_id)
          else:
            continue
    for song in localsong:
      if song not in apisong:
        print("Removed! {0:<50} exists in Local database but removed from Spotify.".format(song))
        for i in localdata['sent']:
          if i['name'] == song:
            bot.sendMessage(chat_id=chat_id, text=f"Removed <b>{song}!</b>, as it has been removed from Spotify.\n<b>{song}</b> was added to database on <b>{i['addedon']}</b>", parse_mode='html')
            localdata['sent'].remove(i)
            # Uncomment the following line to detete the file from the chat in the telegram bot when deleted from spotify playlist.
            #bot.delete_message(chat_id=chat_id, message_id=i['messageid'])
            break
        with open('localdata.json', 'w') as f:
          json.dump(localdata, f, indent=4, ensure_ascii=False)

    # Refreshes every 5 Seconds and logs output in shell
    print(datetime.now(pytz.timezone(f"{os.environ['Timezone']}")).strftime("[%d/%m/%Y %H:%M:%S] ") + 'No changes to be made!')
    time.sleep(5)

    # Delete Old songs, clearing space for new onw.
    autoCleanOldSongs()
    
  updater.idle()
