from app import app
from flask import render_template, request
from app.models import model, formopener
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import Play, VoiceResponse
from app import addSong
import sys
import redis
import re
import random

# NOTES:
# this was hacked together fairly quickly. i wouldn't use it anything other than learning purposes
# Twilio <Play> tag sort of randomly only supports mp3s and wavs. webms and other formats just dont work
# If the <Play> tag supported more audio types, then this project could probably also support YouTube links
# We print to stderr because logging is set to log errors only

# should probably have a config file...
account_sid = 'YOUR_SID_HERE' # ex. DsD9f1CZy1ZkdEc9vwEsOLhozLemWkbo10
auth_token = 'YOUR_TOK_HERE' # ex. 16b8OlWJN1P47KN8p0C96jdY3vGnwhCY
phone_number = 'YOUR_TWILIO_PHONE_HERE' # ex. +19149038435
client = Client(account_sid, auth_token)
r = redis.Redis(host="localhost", port=6379, db=0)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/addPhoneNumber', methods=["GET"])
def addPhoneNumber():
    # this isn't really used... it's possible that we should require sign-up through web before accepting SMS from a given number
    formattedPhoneNumber = re.sub('[^0-9]','', request.form["phone-number"])
    r.hset("numbers." + formattedPhoneNumber, "playlistURL", "None")
    message = client.messages \
                    .create(
                         body="Thank you for signing up. To set your playlist, send its YouTube link here.",
                         from_=phone_number,
                         to="+1" + formattedPhoneNumber
                        )

@app.route("/receiveSms", methods=['GET', 'POST'])
def receiveSms():
    resp = MessagingResponse()

    From = request.form["From"]
    Body = request.form["Body"]
    resp.message("Updated Soundcloud Url to: " + Body)
    r.hset("numbers." + From, "playlistUrl", Body)
    return str(resp)

@app.route("/receiveCall", methods=['GET', 'POST'])
def reciveCall():
    numWithPlus = request.form["From"]
    numWithoutPlus = numWithPlus[1:]
    # print(numWithPlus, file=sys.stderr)
    k = "numbers." + str(numWithPlus)
    playlist = r.hget(k, "playlistUrl")
    if playlist is None:
        print("NO PLAYLIST: " + k, file=sys.stderr)
        return "Something went wrong."
    else:
        playlist = playlist.decode('utf-8')
    player = addSong.MusicPlayer()
    player.addSongs(playlist, numWithoutPlus)
    response = VoiceResponse()
    response.play(player.songFileUrls[0], loop=10)
    # print(str(response), file=sys.stderr)
    return str(response)