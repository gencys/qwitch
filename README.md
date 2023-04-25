# Qwitch

Qwitch is a CLI which allows you to watch streams and videos from Twitch directly in Quicktime on macOS.

Avoid using unoptimized websites and enjoy Twitch simply via a few commands and the fast and reliable Quicktime player.
This also allows you to AirPlay your favorite livestreams and videos on other devices.

## Installation

Qwitch is available via pip only. Simply run the following command to install it:
```
pip install qwitch
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

## Something wrong?

If you find something's not right or you have some trouble setting things up, don't hesitate to create an issue on this repository and I'll do my best to help you.
