import argparse
import requests
import os
import json
import time
import subprocess
import re
from urllib.parse import urlencode
import base64
import webbrowser

#curl -X POST 'https://id.twitch.tv/oauth2/token' -H 'Content-Type: application/x-www-form-urlencoded' -d 'client_id=s3e3q8l6ub08tf7ka9tg2myvetf5cf&client_secret=qfq4qiv8xuc852fc7q3gg15gikav4f&grant_type=client_credentials'

#curl -X GET 'https://api.twitch.tv/helix/videos?user_id=229729353&type=archive' -H 'Authorization: Bearer kt61fn9i7bvvvuj4we4evt9onpd4bz' -H 'Client-Id: s3e3q8l6ub08tf7ka9tg2myvetf5cf'

#curl -X GET 'https://id.twitch.tv/oauth2/validate' -H 'Authorization: OAuth kt61fn9i7bvvvuj4we4evt9onpd4bz'

#curl -X GET 'https://api.twitch.tv/helix/channels/followed?user_id=38864397' -H 'Authorization: Bearer kt61fn9i7bvvvuj4we4evt9onpd4bz' -H 'Client-Id: s3e3q8l6ub08tf7ka9tg2myvetf5cf'

#https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=s3e3q8l6ub08tf7ka9tg2myvetf5cf&redirect_uri=http://localhost:3000&scope=user%3Aread%3Afollows

CLIENT_ID = "s3e3q8l6ub08tf7ka9tg2myvetf5cf"
CLIENT_SECRET = "qfq4qiv8xuc852fc7q3gg15gikav4f"

home_dir = os.path.expanduser('~')
home_dir += '/Library/Application Support'
if not os.path.exists(home_dir + '/qwitch/cache'):
    os.makedirs(os.path.dirname(home_dir + '/qwitch/cache'), exist_ok=True)

def auth_api(client_id = CLIENT_ID, client_secret = CLIENT_SECRET):
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    res_post = requests.post(url = 'https://id.twitch.tv/oauth2/token', data = data, headers = headers)
    res_post = res_post.json()
    store_auth(res_post)
    return res_post['access_token']

def write_streamlink_config():
    if not os.path.exists(home_dir + '/streamlink/config.twitch'):
        os.makedirs(os.path.dirname(home_dir + '/streamlink/config.twitch'), exist_ok=True)
        token = input('Enter your auth-token cookie value: ')
        i=0
        while True:
            if i == 3:
                print('Too many failed attempts. Stopping for now.')
                exit()
            if not re.match('[a-z0-9]{30}', token):
                token = input('\nThis is does not look like an auth-token.\nEnter a valid token: ')
                i += 1
                continue
            break
        config = 'twitch-api-header=Authorization=OAuth ' + token + '\nplayer-args=--file-caching 3000 --network-caching 3000\nplayer-passthrough=hls'
        with open(home_dir + '/streamlink/config.twitch', 'w', encoding='utf-8') as file:
            file.write(config)

def check_streamlink_config():
    url = 'https://id.twitch.tv/oauth2/validate'
    old_token = ''
    with open(home_dir + '/streamlink/config.twitch', 'r', encoding='utf-8') as file:
        content = file.read()
    token = re.findall('twitch-api-header=Authorization=OAuth\s([a-z0-9]{30})', content)
    if not token:
        token = input('\nNo auth-token cookie value was found.\nEnter one now: ')
        i=0
        while True:
            if i == 2:
                exit('Too many failed attempts. Stopping for now.')
            if not re.match('[a-z0-9]{30}', token):
                token = input('\nThis is does not look like an auth-token.\nEnter a valid token: ')
                i += 1
                continue
            break
    if isinstance(token, list):
        token = token[0]
        old_token = token
    j = 0
    while True:
        if j == 2:
            exit('Too many failed attempts. Stopping for now.')
        header = {
            'Authorization': 'OAuth ' + token
        }
        res_get = requests.get(url = url, headers = header)
        if res_get.status_code == 401:
            token = input('\nThe token expired or is invalid.\nEnter a new one: ')
            i=0
            while True:
                if i == 2:
                    exit('Too many failed attempts. Stopping for now.')
                if not re.match('[a-z0-9]{30}', token):
                    token = input('\nThis is does not look like an auth-token.\nEnter a valid token: ')
                    i += 1
                    continue
                break
            j += 1
            continue
        break
    if not content:
        with open(home_dir + '/streamlink/config.twitch', 'w', encoding='utf-8') as file:
            file.write('twitch-api-header=Authorization=OAuth ' + token + '\nplayer-args=--file-caching 3000 --network-caching 3000\nplayer-passthrough=hls')
    elif old_token == '' and content:
        with open(home_dir + '/streamlink/config.twitch', 'a', encoding='utf-8') as file:
            file.write('twitch-api-header=Authorization=OAuth ' + token + '\n')
    elif token != old_token and old_token != '':
        content = content.replace(old_token, token)
        with open(home_dir + '/streamlink/config.twitch', 'w', encoding='utf-8') as file:
            file.write(content)
    print('A valid auth-token was found. Proceeding...')

def store_auth(data):
    now = int(time.time())
    data['requested_at'] = now - 1
    with open(home_dir + '/qwitch/cache', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def check_auth():
    try:
        with open(home_dir + '/qwitch/cache', 'r', encoding='utf-8') as cache:
            cache_json = cache.read().json()
        if cache_json:
            now = int(time.time())
            exp_date = cache_json['requested_at'] + cache_json['expires_in']
            if now >= exp_date:
                token = auth_api()
                if token:
                    return token
                return False
            return cache_json['access_token']
    except:
        token = auth_api()
        if token:
            return token
        return False

def twitch_api_get(token, url):
    headers = {
        'Client-Id': CLIENT_ID,
        'Authorization': 'Bearer ' + token
    }
    res_get = requests.get(url = url, headers = headers)
    return res_get.json()

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
        return res_get['data'][0]['url']
    i = 0
    while res_get['data'][i]:
        match = res_get['data'][i]['title'].lower().find(keyword.lower())
        if match != -1:
            print('Selected video: ' + res_get['data'][i]['title'])
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
            print('Here are the latest videos (most recent first):\n\n')
            first = False
        else:
            print('-------------------------------')
        print('Title: ' + video['title'])
        date = video['published_at'].replace('T', ' ').replace('Z', '')
        print('Published on: ' + date)
        print('Duration: ' + video['duration'])
        print('URL: ' + video['url'])

def exec_streamlink(url):
    cmd_str = 'open -a "quicktime player" $(streamlink ' + url + ' best --stream-url) ;'
    subprocess.run(cmd_str, shell=True)

if __name__ == "__main__":
    try:
        cli = argparse.ArgumentParser(
            prog = 'qwitch',
            description = 'Stream twitch in Quicktime'
        )
        group = cli.add_mutually_exclusive_group(required=True)

        cli.add_argument('channel')
        group.add_argument('-l', '--last', action = 'store_true')
        group.add_argument('-L', '--Live', action = 'store_true')
        group.add_argument('-V', '--Videos', action = 'store_true')
        group.add_argument('-v', '--vod', action = 'store', type=str)
        args = cli.parse_args()

        write_streamlink_config()

        if args.Live:
            try:
                check_streamlink_config()
                url = 'twitch.tv/' + args.channel
                print('Playing the livestream now...')
                exec_streamlink(url=url)
            except:
                cli.error('Could not get the livestream feed.')
            cli.exit()

        auth_token = check_auth()
        if not auth_token:
            cli.error('Could not authenticate in the Twitch API')

        try:
            channel_id = get_channel_id(channel = args.channel, token = auth_token)
            print(channel_id)
        except RuntimeError:
            cli.error('Could not get user id for the channel name provided.')
        except:
            cli.error('Something unknown went wrong.')

        if args.last:
            try:
                check_streamlink_config()
                url = get_vod(channel_id=channel_id, token=auth_token)
                url = url.replace('https://www.', '')
                print('Playing the video now...')
                exec_streamlink(url=url)
            except:
                cli.error('Could not find the last video.')

        if args.Videos:
            try:
                print_vod_list(channel_id=channel_id, token=auth_token)
            except:
                cli.error('Could not retrieve the video list')

        if args.vod:
            try:
                check_streamlink_config()
                url = get_vod(channel_id=channel_id, token=auth_token, keyword=args.vod)
                print(url)
                url = url.replace('https://www.', '')
                print('Playing the video now...')
                exec_streamlink(url=url)
            except:
                cli.error('Could not find a video that matched the keyword.')
    except KeyboardInterrupt:
        exit()