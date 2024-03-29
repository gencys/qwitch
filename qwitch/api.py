import requests
import json
import subprocess
import re
from streamlink.options import Options
from streamlink.session import Streamlink
from . import config

CLIENT_ID = 's3e3q8l6ub08tf7ka9tg2myvetf5cf'

##
# twitch_api_get()
#
# Send a GET request to the Twitch API with Qwitch's client ID
#
# @param token string auth token gathered from authenticating user
# @param url string url on which to perform the get request
#
# @return dict containing the GET request's response
##
def twitch_api_get(token, url):
    headers = {
        'Client-Id': CLIENT_ID,
        'Authorization': 'Bearer ' + token
    }
    res_get = requests.get(url = url, headers = headers)
    config.debug_log('From URL:', url, 'with token:', token, 'API returned:', res_get)
    if res_get.status_code == 401:
        print('Your access token may have expired. Please authenticate again and try again.')
        config.auth_api()
        exit()
    return res_get.json()

##
# get_livestreams()
#
# Gets and prints followed channels currently streaming
#
# @param token string auth token gathered from authenticating user
#
# @return nothing
##
def get_livestreams(token):
    with open(config.home_dir + '/qwitch/config.json', 'r', encoding='utf-8') as cache:
            cache_json = json.loads(cache.read())
            config.debug_log('get_livestreams(): Config read:', cache_json)
    url = 'https://api.twitch.tv/helix/channels/followed?user_id=' + cache_json[0]['user_id']
    res_get = twitch_api_get(token = token, url = url)
    url = 'https://api.twitch.tv/helix/streams?type=live'
    i = 0
    for follow in res_get['data']:
        url = url + '&user_id=' + follow['broadcaster_id']
        if i == 99:
            break
        i += 1
    res_get = twitch_api_get(token = token, url = url)
    res_get = res_get['data']
    first = True
    for video in res_get:
        if first:
            print('Here are the current livestreams you follow:\n(The channel name you will need is in red)\n')
            first = False
        else:
            print('\n-------------------------------------------------------------------\n')
        print('\033[95mStreamer:\033[0m      ' + video['user_name'] + ' (\033[91m\033[1m' + video['user_login'] + '\033[0m)')
        print('\033[95mTitle:\033[0m         ' + video['title'])
        print('\033[95mGame/Category:\033[0m ' + video['game_name'])

##
# get_follows()
#
# Gets and prints followed channels
#
# @param token string auth token gathered from authenticating user
#
# @return nothing
##
def get_follows(token):
    with open(config.home_dir + '/qwitch/config.json', 'r', encoding='utf-8') as cache:
            cache_json = json.loads(cache.read())
            config.debug_log('get_livestreams(): Config read:', cache_json)
    url = 'https://api.twitch.tv/helix/channels/followed?user_id=' + cache_json[0]['user_id']
    res_get = twitch_api_get(token = token, url = url)
    res_get = res_get['data']
    first = True
    for video in res_get:
        if first:
            print('Here are the channels you follow:\n(The channel name you will need is in red)\n')
            first = False
        else:
            print('-------------------------------')
        print('\033[95mChannel Display Name:\033[0m        ' + video['broadcaster_name'])
        print('\033[95mChannel Name:\033[0m                ' + '\033[91m\033[1m' + video['broadcaster_login'] + '\033[0m')
        date = video['followed_at'].replace('T', ' ').replace('Z', '')
        print('\033[95mFollowed on:\033[0m                 ' + date)

##
# get_channel_id()
#
# Gets the twitch channel ID for the given channel name
#
# @param token string auth token gathered from authenticating user
# @param channel string channel name for which to get the channel ID
#
# @return integer the retrieved channel ID
#
# @remark this will raise a runtime error if the channel ID was not in the server's response
##
def get_channel_id(channel, token):
    url = 'https://api.twitch.tv/helix/users?login=' + channel
    res_get = twitch_api_get(token = token, url = url)
    try:
        channel_id = res_get['data'][0]['id']
        return channel_id
    except:
        raise RuntimeError

def get_vod(channel_id, token, keyword = ''):
    url = 'https://api.twitch.tv/helix/videos?user_id=' + channel_id + '&type=archive'
    res_get = twitch_api_get(token = token, url = url)
    if keyword == '':
        print('\033[95mSelected video:\033[0m ' + res_get['data'][0]['title'])
        resp = input('Play this video ? [y/N] ')
        if resp.lower() != 'y':
            exit()
        return res_get['data'][0]['url']
    i = 0
    while res_get['data'][i]:
        match = res_get['data'][i]['title'].lower().find(keyword.lower())
        if match != -1:
            print('\033[95mSelected video:\033[0m ' + res_get['data'][i]['title'])
            resp = input('Play this video ? [y/N] ')
            if resp.lower() != 'y':
                exit()
            return res_get['data'][i]['url']
        i += 1
    raise RuntimeError

##
# print_vod_list()
#
# Gets and prints the 20 latest VODs of the channel
#
# @param token string auth token gathered from authenticating user
# @param channel_id integer channel ID for which to get the VOD list
#
# @return string URL of the video that was chosen to be played
#         none otherwise
##
def print_vod_list(channel_id, token):
    url = 'https://api.twitch.tv/helix/videos?user_id=' + channel_id + '&type=archive'
    res_get = twitch_api_get(token = token, url = url)
    res_get = res_get['data']
    first = True
    for video in res_get:
        if first:
            print('Here are the latest videos (most recent first):\n')
            first = False
        else:
            print('-------------------------------')
        print('\033[95mTitle:\033[0m        ' + video['title'])
        date = video['published_at'].replace('T', ' ').replace('Z', '')
        print('\033[95mPublished on:\033[0m ' + date)
        print('\033[95mDuration:\033[0m     ' + video['duration'])
        print('\033[95mURL:\033[0m          ' + video['url'])
        print('\033[95mVideo ID:\033[0m     ' + video['id'])
        resp = input('\nPlay this video? [y/N] ')
        if str(resp).lower() == 'y':
            url = video['url'].replace('https://www.', '')
            return url
    return None

##
# exec_streamlink()
#
# Uses Streamlink to get the video stream link and launches Quicktime with that link
#
# @param url string url of the twitch video/livestream to play
# @param streamlink_config dict containing streamlink config properties (e.g. the auth-token)
# @param quality string video quality at which to play the video
#
# @return nothing
##
def exec_streamlink(url, streamlink_config, quality = None):
    session = Streamlink()
    options = Options()
    for key in streamlink_config:
        if key == 'default-stream':
            continue
        if re.match('^twitch-', key):
            option_key = key.replace('twitch-', '')
            try:
                option_value = [streamlink_config[key].split('=')]
            except:
                option_value = streamlink_config[key]
            options.set(option_key, option_value)
        else:
            session.set_option(key = key, value = streamlink_config[key])
    if 'default-stream' in streamlink_config and not quality:
        quality = streamlink_config['default-stream']
    elif not ('default-stream' in streamlink_config) and not quality:
        quality = 'best'
    try:
        streamurl = session.streams(url, options)[quality].url
        cmd_str = 'open -a "quicktime player" '+streamurl+';'
        subprocess.run(cmd_str, shell=True)
    except:
        print(
            'An error occured with Streamlink.\n',
            'You may not be subscribed to the twitch channel you are trying to access.',
            'Alternatively, check that you are still logged into your account on twitch.com','If not, get a new auth-token and update it by running:',
            '    qwitch -t',
            sep='\n'
        )
