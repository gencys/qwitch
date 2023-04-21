import requests
import json
import subprocess
import config

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
    with open(config.home_dir + '/qwitch/cache', 'r', encoding='utf-8') as cache:
            cache_json = json.loads(cache.read())
            config.debug_log('get_livestreams(): Config read:', cache_json)
    url = 'https://api.twitch.tv/helix/channels/followed?user_id=' + cache_json['user_id']
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
            print('Here are the current livestreams you follow:\n')
            first = False
        else:
            print('\n-------------------------------------------------------------------\n')
        print('Streamer:      ' + video['user_name'] + ' (' + video['user_login'] + ')')
        print('Title:         ' + video['title'])
        print('Game/Category: ' + video['game_name'])

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
        print('Selected video: ' + res_get['data'][0]['title'])
        resp = input('Play this video ? [y/N] ')
        if resp.lower() != 'y':
            exit()
        return res_get['data'][0]['url']
    i = 0
    while res_get['data'][i]:
        match = res_get['data'][i]['title'].lower().find(keyword.lower())
        if match != -1:
            print('Selected video: ' + res_get['data'][i]['title'])
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
        print('Title:        ' + video['title'])
        date = video['published_at'].replace('T', ' ').replace('Z', '')
        print('Published on: ' + date)
        print('Duration:     ' + video['duration'])
        print('URL:          ' + video['url'])
        resp = input('\nPlay this video? [y/N] ')
        if str(resp).lower() == 'y':
            url = video['url'].replace('https://www.', '')
            exec_streamlink(url = url)
            break

def exec_streamlink(url):
    cmd_str = 'open -a "quicktime player" $(streamlink ' + url + ' best --stream-url) ;'
    subprocess.run(cmd_str, shell=True)