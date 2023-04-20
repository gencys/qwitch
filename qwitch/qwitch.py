import argparse
import re
import config
import api


if __name__ == "__main__":
    try:
        cli = argparse.ArgumentParser(
            prog = 'qwitch',
            description = 'Stream twitch in Quicktime'
        )
        group = cli.add_mutually_exclusive_group(required=True)

        cli.add_argument('channel', nargs='?', default = False)
        cli.add_argument('-d', '--debug', action = 'store_true', help= 'enable debugging.')

        group.add_argument('-l', '--last', action = 'store_true', help= 'play the most recent video of the channel.')
        group.add_argument('-V', '--Videos', action = 'store_true', help= 'list the last 20 videos of the channel.')
        group.add_argument('-s', '--streams', action = 'store_true', help= 'list the streamers you follow currently live.')
        group.add_argument('-v', '--vod', action = 'store', type = str, help= 'search for a video by keyword(s) or ID.')
        args = cli.parse_args()

        config.write_streamlink_config()
        auth_token = config.check_auth()
        if not auth_token:
            cli.error('Could not authenticate in the Twitch API')

        if args.debug:
            config.DEBUG = True

        if args.channel:
            try:
                channel_id = api.get_channel_id(channel = args.channel, token = auth_token)
            except RuntimeError:
                cli.error('Could not get user id for the channel name provided.')
            except:
                cli.error('Something unknown went wrong.')

            if args.last:
                config.check_streamlink_config()
                url = api.get_vod(channel_id=channel_id, token=auth_token)
                url = url.replace('https://www.', '')
                config.debug_log('Playing the video now...')
                api.exec_streamlink(url=url)
            elif args.Videos:
                try:
                    api.print_vod_list(channel_id=channel_id, token=auth_token)
                except:
                    cli.error('Could not retrieve the video list')
            elif args.vod:
                try:
                    config.check_streamlink_config()
                    url = api.get_vod(channel_id=channel_id, token=auth_token, keyword=args.vod)
                    url = url.replace('https://www.', '')
                    config.debug_log('Playing the video now...')
                    api.exec_streamlink(url=url)
                except:
                    cli.error('Could not find a video that matched the keyword.')
            else:
                try:
                    config.check_streamlink_config()
                    url = 'twitch.tv/' + args.channel
                    config.debug_log('Playing the livestream now...')
                    api.exec_streamlink(url=url)
                except:
                    cli.error('Could not get the livestream feed.')
        elif args.vod:
            if re.match('^[0-9]{9}$', args.vod):
                url = 'twitch.tv/videos/' + args.vod
                api.exec_streamlink(url=url)
                cli.exit()
        elif args.streams:
            auth_token = config.check_auth()
            if not auth_token:
                cli.error('Could not authenticate in the Twitch API')
            try:
                api.get_livestreams(token = auth_token)
            except:
                cli.error('Could not get the livestream list.')
    except KeyboardInterrupt:
        exit()