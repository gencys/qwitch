import argparse
import re
from . import config
from . import api

def main():
    try:
        cli = argparse.ArgumentParser(
            prog = 'qwitch',
            description = 'Stream twitch in Quicktime'
        )
        group = cli.add_mutually_exclusive_group(required=True)

        cli.add_argument('channel', nargs='?', default = False, help= 'channel name given in red with -s/--streams. Needed to launch livestream or videos.')
        cli.add_argument('quality', nargs='?', default = False, help= 'video quality name, e.g. 720p, 1080p, best, worst, etc... (defaults to best). You can defined a default quality in the config file (see the README)')
        cli.add_argument('-d', '--debug', action = 'store_true', help= 'enable debugging.')
        cli.add_argument('--version', action='version', version='%(prog)s 2.2.1')

        group.add_argument('-l', '--last', action = 'store_true', help= 'play the most recent video of the channel.')
        group.add_argument('-V', '--Videos', action = 'store_true', help= 'list the last 20 videos of the channel.')
        group.add_argument('-s', '--streams', action = 'store_true', help= 'list the streamers you follow which are currently currently live.')
        group.add_argument('-f', '--follows', action = 'store_true', help= 'list the streamers you follow.')
        group.add_argument('-v', '--vod', action = 'store', type = str, help= 'search for a video by keyword(s) or ID. The keyword needs to be in quotation marks and an exact match (this is not a search engine)')
        args = cli.parse_args()

        auth_token = config.check_auth()
        streamlink_config = config.check_streamlink_config()
        if not auth_token:
            cli.error('Could not authenticate in the Twitch API')

        if args.debug:
            config.DEBUG = True

        if args.follows:
            try:
                api.get_follows(token = auth_token)
            except:
                cli.error('Could not get the list of followed streamers.')
        elif args.channel:
            try:
                channel_id = api.get_channel_id(channel = args.channel, token = auth_token)
            except RuntimeError:
                cli.error('Could not get user id for the channel name provided.\nCheck that the channel name you provided is correct.')
            except:
                cli.error('Something unknown went wrong.')

            if args.last:
                url = api.get_vod(channel_id=channel_id, token=auth_token)
                url = url.replace('https://www.', '')
                config.debug_log('Playing the video now...')
                api.exec_streamlink(url = url, streamlink_config = streamlink_config, quality = args.quality)
            elif args.Videos:
                try:
                    url = api.print_vod_list(channel_id=channel_id, token=auth_token)
                    if url:
                        api.exec_streamlink(url = url, streamlink_config = streamlink_config, quality = args.quality)
                except KeyboardInterrupt:
                    exit()
                except:
                    cli.error('Could not retrieve the video list')
            elif args.vod:
                try:
                    url = api.get_vod(channel_id=channel_id, token=auth_token, keyword=args.vod)
                    url = url.replace('https://www.', '')
                    config.debug_log('Playing the video now...')
                    api.exec_streamlink(url = url, streamlink_config = streamlink_config, quality = args.quality)
                except:
                    cli.error('Could not find a video that matched the keyword.')
            else:
                try:
                    url = 'twitch.tv/' + args.channel
                    config.debug_log('Playing the livestream now...')
                    api.exec_streamlink(url = url, streamlink_config = streamlink_config, quality = args.quality)
                except:
                    cli.error('Could not get the livestream feed.')
        elif args.vod:
            if re.match('^[0-9]{9,10}$', args.vod):
                url = 'twitch.tv/videos/' + args.vod
                api.exec_streamlink(url = url, streamlink_config = streamlink_config, quality = args.quality)
        elif args.streams:
            try:
                api.get_livestreams(token = auth_token)
            except:
                cli.error('Could not get the livestream list.')
    except KeyboardInterrupt:
        exit()

if __name__ == "__main__":
    main()