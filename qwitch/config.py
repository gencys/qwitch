import os
import re
import time
import json
import webbrowser
import time
import requests

DEBUG = False
VER = '2.4.2'

home_dir = os.path.expanduser('~')
home_dir += '/Library/Application Support'
if not os.path.exists(home_dir + '/qwitch/config.json'):
    os.makedirs(os.path.dirname(home_dir + '/qwitch/config.json'), exist_ok=True)

##
# debug_log()
#
# Print given args when debugging is enabled
##
def debug_log(*args):
    if DEBUG:
        print('\n')
        for arg in args:
            print(arg)
        print('\n')

##
# ask_for_token()
#
# Asks the user for their auth-token, regex it to confirm it's a token-like string
# it can also validate the token
#
# @param tries integer number of maximum retries
# @param validate boolean tells the function to validate the token or not
#
# @return string the token that was parsed
##
def ask_for_token(tries = 3, validate = False):
    i=0
    token = input('Enter your auth-token cookie value: ')
    debug_log('Got token from input:', token)
    while True:
        if i == tries - 1:
            exit('Too many failed attempts. Stopping for now.')
        if not re.match('[a-z0-9]{30}', token):
            token = input('\nThis is does not look like an auth-token.\nEnter a valid token: ')
            debug_log('Got token from input:', token)
            i += 1
            continue
        if validate:
            res_get = validate_token(token = token)
            if res_get.status_code == 401:
                token = input('\nThe token expired or is invalid.\nEnter a new one: ')
                debug_log('Got token from input:', token)
                i += 1
                continue
        break
    return token

##
# auth_api()
#
# Opens the twitch auth page to get user token. Parses token from URL and stores it in the config file
#
# @return string the token that was parsed
##
def auth_api():
    print('A browser page will open. Connect with your account to authorize the app.\nOnce done, copy the full URL and paste it below.')
    time.sleep(5)
    webbrowser.open('https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=s3e3q8l6ub08tf7ka9tg2myvetf5cf&redirect_uri=http://localhost:3000&scope=user_read+user_subscriptions+user%3Aread%3Afollows', new=1, autoraise=True)
    auth_url = input('Enter the full URL here: ')
    token = re.findall('access_token=([a-z0-9]{30})\&scope', auth_url)
    debug_log('Parsed token: ', token)
    auth_data = validate_token(token=token[0])
    if auth_data.status_code == 401:
        print('The URL you entered may be invalid. Try again.')
        exit()
    auth_data = auth_data.json()
    auth_data['access_token'] = token[0]
    store_auth(data = auth_data)
    print('You can close the page that was opened.')
    return token[0]

##
# validate_token()
#
# Sends a request to the twitch API to validate the token string
#
# @param token string sent to the API that needs to be validated
#
# @return request object of the get request ran
##
def validate_token(token: str):
    url = 'https://id.twitch.tv/oauth2/validate'
    header = {
        'Authorization': 'OAuth ' + token
    }
    res_get = requests.get(url = url, headers = header)
    debug_log('Validation response:', res_get.json())
    return res_get

##
# write_streamlink_config()
#
# Writes the auth-token config to the config file after asking for the token
#
# @return config dict if the config file exists, false otherwise
##
def write_streamlink_config():
    if os.path.exists(home_dir + '/qwitch/config.json'):
        token = ask_for_token(validate = True)
        with open(home_dir + '/qwitch/config.json', 'r', encoding='utf-8') as file:
            cache_json = json.loads(file.read())
        if len(cache_json) >= 2:
            cache_json[1].update({'twitch-api-header': 'Authorization=OAuth ' + token})
        else:
            config = {
                'twitch-api-header': 'Authorization=OAuth ' + token
            }
            cache_json.append(config)
        config = cache_json[1]
        with open(home_dir + '/qwitch/config.json', 'w', encoding='utf-8') as file:
            json.dump(cache_json, file, ensure_ascii=False, indent=4)
        return config
    return False

##
# check_streamlink_config()
#
# Reads the auth-token config in the config file after verifying that the config is valid
# updates/creates the config if necessary
#
# @return the config dict for the auth-token
##
def check_streamlink_config():
    old_token = ''
    with open(home_dir + '/qwitch/config.json', 'r', encoding='utf-8') as file:
        content = json.loads(file.read())
        debug_log('Content of config:', content)
    if len(content) >= 2:
        if 'twitch-api-header' in content[1]:
            token = re.findall('Authorization=OAuth\s([a-z0-9]{30})', content[1]['twitch-api-header'])
        else:
            config = write_streamlink_config()
            return config
    else:
        config = write_streamlink_config()
        return config
    debug_log('Token from config:', token)
    token = token[0]
    old_token = token
    j = 0
    while True:
        if j == 2:
            exit('Too many failed attempts. Stopping for now.')
        res_get = validate_token(token = token)
        if res_get.status_code == 401:
            print('\nThe token expired or is invalid.')
            token = ask_for_token()
            j += 1
            continue
        break
    if old_token != token:
        content[1]['twitch-api-header'] = 'Authorization=OAuth ' + token
        with open(home_dir + '/qwitch/config.json', 'w', encoding='utf-8') as file:
            json.dump(content, file, ensure_ascii=False, indent=4)
    debug_log('A valid auth-token was found. Proceeding...')
    return content[1]

##
# store_auth()
#
# Writes the twitch token config to the config file
#
# @param data dict of the validation request for the twitch API token
##
def store_auth(data):
    now = int(time.time())
    data['requested_at'] = now - 1
    if os.path.exists(home_dir + '/qwitch/config.json'):
        with open(home_dir + '/qwitch/config.json', 'r', encoding='utf-8') as file:
            cache_json = json.loads(file.read())
            cache_json[0] = data
        with open(home_dir + '/qwitch/config.json', 'w', encoding='utf-8') as file:
            json.dump(cache_json, file, ensure_ascii=False, indent=4)
    else:
        with open(home_dir + '/qwitch/config.json', 'w', encoding='utf-8') as file:
            data = [data]
            json.dump(data, file, ensure_ascii=False, indent=4)

##
# check_auth()
#
# Reads and validates the config for the twitch API token
#
# @return string token which was parsed
##
def check_auth():
    try:
        with open(home_dir + '/qwitch/config.json', 'r', encoding='utf-8') as cache:
            cache_json = json.loads(cache.read())
            debug_log('check_auth(): Config read:', cache_json)
        if cache_json:
            now = int(time.time())
            exp_date = cache_json[0]['requested_at'] + cache_json[0]['expires_in']
            if now >= exp_date:
                token = auth_api()
                debug_log('Token returned by auth_api():', token)
                if token:
                    return token
                return False
            return cache_json[0]['access_token']
    except:
        token = auth_api()
        debug_log('Token returned by auth_api() after error:', token)
        if token:
            return token
        return False

##
# check_auth()
#
# Get Qwitch's latest version from pypi.org's API, compares it to current version and advises if new version is available
#
# @return boolean True if newer version is available, False otherwise
##
def get_package_ver_and_compare():
    with open(home_dir + '/qwitch/config.json', 'r', encoding='utf-8') as cache:
        cache_json = json.loads(cache.read())
    now = int(time.time())
    if len(cache_json) >= 3:
        if 'last_update_check' in cache_json[2]:
            time_to_check = cache_json[2]['last_update_check'] + 86400
            if  now < time_to_check:
                return False
        cache_json[2].update({'last_update_check': now})
    else:
        cache_json.append({'last_update_check': now})
    with open(home_dir + '/qwitch/config.json', 'w', encoding='utf-8') as file:
        json.dump(cache_json, file, ensure_ascii=False, indent=4)
    res_get = requests.get(url = 'https://pypi.org/pypi/qwitch/json').json()
    remote_ver = res_get['info']['version']
    if remote_ver != VER:
        print('A new version of Qwitch is available!\nPlease update Qwitch by running:\n    \033[91m\033[1mpip install qwitch --upgrade\033[0m')
        return True
    return False