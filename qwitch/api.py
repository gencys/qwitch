import requests
import json
import subprocess
import re
import streamlink
from . import config

CLIENT_ID = 's3e3q8l6ub08tf7ka9tg2myvetf5cf'

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
        print('\033[95mVideo ID:\033[0m          ' + video['id'])
        resp = input('\nPlay this video? [y/N] ')
        if str(resp).lower() == 'y':
            url = video['url'].replace('https://www.', '')
            return url
    return None

def exec_streamlink(url, streamlink_config, quality = None):
    session = streamlink.Streamlink()
    for key in streamlink_config:
        if key == 'default-stream':
            continue
        if re.match('^twitch-', key):
            option_key = key.replace('twitch-', '')
            try:
                option_value = [streamlink_config[key].split('=')]
            except:
                option_value = streamlink_config[key]
            session.set_plugin_option('twitch', option_key, option_value)
        else:
            session.set_option(key = key, value = streamlink_config[key])
    if 'default-stream' in streamlink_config and not quality:
        quality = streamlink_config['default-stream']
    elif not ('default-stream' in streamlink_config) and not quality:
        quality = 'best'
    try:
        streamurl = session.streams(url)[quality].url
        cmd_str = 'open -a "quicktime player" '+streamurl+';'
        subprocess.run(cmd_str, shell=True)
    except:
        print('An error occured with Streamlink.')
