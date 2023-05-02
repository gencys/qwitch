# Qwitch

Qwitch is a CLI which allows you to watch streams and videos from Twitch directly in Quicktime on macOS.

Avoid using unoptimized websites and enjoy Twitch simply via a few commands and the fast and reliable Quicktime player.
This also allows you to AirPlay your favorite livestreams and videos on other devices.

## Requirements

To install Qwitch you will need to have installed Python >= 3.8 and the XCode Command Line Tools.

What's beautiful is that you can get these two requirement installed with only one command since XCode Command Line Tools will also install a compatible version of python3. All you need to do is run the following command
```
xcode-select --install
```
This will prompt you to install XCode Command Line Tools on your environment. Now you should be able to run python and pip commands.

## Installation

Qwitch is available via pip only. Simply run the following command to install it:
```
pip3 install --user qwitch
```

Once that's done, you'll be able to use Qwitch directly in the terminal. On the first use, the CLI will ask you two things:
* The value of Twitch's auth-token cookie
* For you to allow Qwitch to have access to a few things on your Twitch account

First, open your favorite web browser and log into your Twitch account. Then you'll need the value of the auth-token cookie. To grab it:
- Right-click anywhere on Twitch's webpage
- Click on "Inspect Element" or "Inspect"
- Navigate to the "Storage" or "Application" tab on the little window that opened
- Expand the "Cookies" folder
- Click on "twitch.tv"
- Search for the "auth-token" entry and copy its value (a 30-character string containing numbers and letters)

Alternatively, you can use a browser extension like cookies.txt for Firefox. This will generate a text file in which you'll need to search for the "auth-token" entry.

Well done! You'll need this to set up Qwitch.

Now you can use Qwitch in the terminal and it will ask you for this token in due time. It will also prompt you to give it access to a few information from your Twitch account. To do so it will automatically open your web browser, you'll need to accept, and then copy and paste the URL of the page back to Qwitch.

## How to use

Here are a few examples of how to achieve certain tasks with Qwitch:
### See which streamers you follow are live now

This is rather simple, simply enter the command below:
```
qwitch -s
```
The option `-s` is short for `--streams`. Qwitch will get the list of streamers you follow and display which ones are live now, with information about their stream.

### List the streamers you follow and their channel name

This is rather simple, simply enter the command below:
```
qwitch -f
```
The option `-f` is short for `--follows`. Qwitch will get the list of streamers you follow and display information about their channel. **Most important information is their channel name displayed in red, which Qwitch needs when you search for their videos or streams.**

### Watch this streamer's live

Say your favourite streamer is live and you want to watch their stream. Then all you'll need is the name of their channel. For example, if I want to watch Critical Role live, and I know the name of their channel is `criticalrole` then I use the following command to launch their livestream:
```
qwitch -s criticalrole
```
To know your streamer's channel name either use `qwitch -s`, if they are live then the channel name will be written in red. Otherwise, look at Twitch's link to their channel. In Critical Role's example it would be `https://twitch.tv/criticalrole` so their channel name is `criticalrole`.

Alternatively you can list the streamers you follow with `qwitch -f` and the channel names will be displayed in red.

### Watch this streamer's last video

You can watch a streamer's last video with the `-l` option (short for `--last`), like so:
```
qwitch -l channelname
```
and replacing `channelname` by the streamer's actual channel name.

### List a streamer's last 20 videos

You can list a streamer's last 20 videos with the `-V` (or `--Videos`) option, like so:
```
qwitch -V channelname
```
and replacing `channelname` by the streamer's actual channel name.

This will list the videos one by one, and ask you each time if you want to watch the video. Simply enter `y`, for yes, or `n`, for no, and hit <kbd>⏎ Enter</kbd>.

### Search and watch a streamer's video

To search and watch one of the streamer's last 20 videos, you can use the `-v` (short for `--vod`) either with a video ID or by using keywords from the video's title.

A video ID can be obtained from the video's `twitch.tv` link (e.g. `https://twitch.tv/videos/524717693` the video ID is `524717693`), or after using `qwitch -V channelname` to list channelname's last 20 videos. Once the video ID is obtained you can watch it with:
```
qwitch -v <VIDEO_ID>
```
where `<VIDEO_ID>` has to be replaced with the actual video ID (e.g. `524717693`).

To search for a video with a keyword(s), specify the keyword in quotation marks followed by the channel name. Like so:
```
qwitch -v "some keywords" channelname
```
This will search for a video with the title containing exactly `some keywords` in channelname's last 20 videos. The keywords you use have to be an exact match (up to letter case) because Twitch does not have any search engine to search for videos.

### Adjust the video quality

You can adjust a video's playback quality by telling Qwitch which video quality you want it to use. This is done by passing a video quality tag in the command (i.e. one of `160p`, `360p`, `480p`, `720p` or `1080p`) like so:
```
qwitch -s criticalrole 480p
```
This works with any qwitch command that can play a video.

By default qwitch will use the best available quality. However, you can override this by setting the `default-stream` option in Qwitch's config file.

## Qwitch's config file

Qwitch's config file is located at `~/Library/Application Support/qwitch` and is named `config.json`. This file contains two entries:
 - The first one contains information about you as a twitch user (this stays on your system, Qwitch doesn't collect any of your information), i.e. your tokens to log into twitch from the CLI
 - The second one contains all the [Streamlink](https://streamlink.github.io) options that are needed to power Qwitch

You can add Streamlink options to the second part of the config file in a JSON format. For example, you can add the `default-stream` Streamlink option to specify the default stream quality Qwitch should use. With this option, Qwitch's config file would look like
```json
[
    {
        "client_id": "qwer9tyuiopasdf0ghjkllzxcv4bnm",
        "login": "username",
        "scopes": [
            "user:read:follows",
            "user_read",
            "user_subscriptions"
        ],
        "user_id": "12345678",
        "expires_in": 4932814,
        "access_token": "zxc6vbnm7asdfg3hjklqwert8yuiop",
        "requested_at": 1682178117
    },
    {
        "twitch-api-header": "Authorization=OAuth asdfghjkl4qwertyui9nbvc2qwerty",
        "default-stream": "720p"
    }
]
```
More options for Streamlink can be found on their website. Options that are boolean, need to be added in JSON format, i.e. you will need to specify `True` or `False` as value for the key.

## Something wrong?

If you find something's not right or you have some trouble setting things up, don't hesitate to create an issue on Qwitch's GitHub repository and I'll do my best to help you.
