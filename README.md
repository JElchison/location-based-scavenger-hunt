# location-based-scavenger-hunt
A Python/CGI framework for creating your own customizable location-based collaborative scavenger hunts.

For Christmas 2015, I decided I'd like to gift my family an *experience* instead of material gifts.  There are a few services out there that provide location-based scavenger hunts, but none (that I could find) are free or open-source.  So, I created my own.  And now, this is my gift to you.

Sample questions included are for a Christmas-based hunt in Cincinnati, but can easily be repurposed for your own uses (for any occasion, in any city).

Features:
* Multi-user, collaborative game.  Everyone competes collaboratively, but against each other for the final prize.
* Define your own questions (in order)
* Answers may be text-based, location-based, or both
* Admin panel to modify score, current question, disabled questions
* Several Easter eggs / plot-twists
* "Gullible challenges" between users (one user must convince another of an obviously incorrect answer)

Techy stuff:
* On client side, browser-based gameplay.  Works on any mobile device with a modern browser (Chrome recommended).  No app installation required.
* Server side runs a Python script in CGI environment (TLS recommended)


## Screenshots

<p>
Sample question:
<br><img src="https://raw.githubusercontent.com/JElchison/location-based-scavenger-hunt/master/screenshots/Question.png" width="300">
</p>

<p>
A correct answer:
<br><img src="https://raw.githubusercontent.com/JElchison/location-based-scavenger-hunt/master/screenshots/Correct.png" width="300">
</p>

<p>
An incorrect answer:
<br><img src="https://raw.githubusercontent.com/JElchison/location-based-scavenger-hunt/master/screenshots/Incorrect.png" width="300">
</p>

<p>
A question linking to a geocache:
<br><img src="https://raw.githubusercontent.com/JElchison/location-based-scavenger-hunt/master/screenshots/Geocache.png" width="300">
</p>

<p>
A location-based question:
<br><img src="https://raw.githubusercontent.com/JElchison/location-based-scavenger-hunt/master/screenshots/Location.png" width="300">
</p>

<p>
A sample hint:
<br><img src="https://raw.githubusercontent.com/JElchison/location-based-scavenger-hunt/master/screenshots/Hint.png" width="300">
</p>

<p>
Embedded HTML, in this case a YouTube video:
<br><img src="https://raw.githubusercontent.com/JElchison/location-based-scavenger-hunt/master/screenshots/Video.png" width="300">
</p>

<p>
Admin panel:
<br><img src="https://raw.githubusercontent.com/JElchison/location-based-scavenger-hunt/master/screenshots/Admin.png" width="300">
</p>


## Setup

### Server Setup

To run a scavenger hunt, you will need a web server under your control.

Following is one recommended configuration:
* [Amazon EC2](https://aws.amazon.com/ec2/) instance
* Latest [Ubuntu LTS](https://wiki.ubuntu.com/LTS)
    * [Automatic Security Updates](https://help.ubuntu.com/community/AutomaticSecurityUpdates)
        * `sudo apt-get install unattended-upgrades`
        * `sudo dpkg-reconfigure --priority=low unattended-upgrades`
* Firewall
    * All ports closed, except game server port (e.g. 55864) and possibly SSH
* Web server configuration
    * Disable HTTP on port 80
    * Run latest version of TLS on obscure high port number (e.g. 55864)
    * [Strong Ciphers for Apache, nginx and Lighttpd](https://cipherli.st/)
* [lighttpd](https://www.lighttpd.net/)
    * `sudo apt-get install lighttpd`
    * [Setting up a simple SSL configuration](https://redmine.lighttpd.net/projects/1/wiki/HowToSimpleSSL)
    * [Strong SSL Security on lighttpd](https://raymii.org/s/tutorials/Strong_SSL_Security_On_lighttpd.html)
    * [Installing Lighttpd with Python CGI support](https://mike632t.wordpress.com/2013/09/21/installing-lighttpd-with-python-cgi-support/)
* [pip](http://www.pip-installer.org/) for Python package management
    * `sudo apt-get install python-pip`
* [dill](https://github.com/uqfoundation/dill) as alternative for Python's pickle
    * `sudo pip install dill`
* [geopy](https://pypi.python.org/pypi/geopy) for geolocation in Python
    * `sudo pip install geopy`
    

### Game Setup

Following should be set up per-game:
* Fill out `game_config.py` with your game parameters
    * `USERS` table (in a list of "(username, login hash)" tuples)
    * `ADMIN_USERS` list
    * Name of game arch-nemesis (e.g. "The Grinch")
    * UTC time that game is expected to end
    * Define questions.  Refer to the [Question class](https://github.com/JElchison/location-based-scavenger-hunt/blob/master/cgi-bin/game.py#L103) for more info. Sample questions included are for a Christmas-based hunt in Cincinnati, but can easily be repurposed for your own uses (for any occasion, in any city).
* If using the (included) Simon question, be sure to update required end score and URL on [line 114 of `simon_says.js`](https://github.com/JElchison/location-based-scavenger-hunt/blob/master/simon/inc/simon_says.js#L114).  The `q=14` *must* match the question number in `game_config.py`.
* Set up a login method.  Login URL = `https://your-server-url.here:55864/cgi-bin/game.py?l=hash` where the hash comes from the `USERS` list in `game_config.py`. Methods:
    * Email a personalized login link to every user (no sharing login links).  This is the preferred method (see Client Setup below).
    * Print a QR code for each user using the personalized login link

For ideas on devising creative questions:
* Use the included Simon game
* Hide a clue inside a real [geocache](https://www.geocaching.com/), and then link to the geocache as part of a question
* Use [Google Voice](https://www.google.com/voice) for a custom voicemail greeting revealing a required clue
* Use [Twilio](https://www.twilio.com/) to do neat things with text messages
* Use [IFTTT](https://ifttt.com/) for some neat conditional clues
    

### Client Setup

If you're using QR codes for login, iPhone users may need to download a barcode reader, such as [QR Reader](https://itunes.apple.com/us/app/qr-reader-for-iphone/id368494609).  Further, you may not be able to control what browser opens after having scanned a QR code.  Safari on iPhone has been observed to be wonky.

Chrome is the recommended mobile browser, both on iPhone and Android.  For that reason, perhaps emailing a personalized login link to every user is the preferred method.

When a client logs in the first time, he/she will have to grant two privileges:
* Accept the self-signed certificate (unless you have a CA-signed one).  Usually, it's <b>Advanced</b> --> <b>Proceed</b>.
* Allow Chrome to detect/use your location

If you don't accept/allow both of these, then you'll have a sad time.  A nerd should supervise the process of initial logins.

Ensure that everyone reads the instructions (on Question 1) before anyone attempts to answer Question 1.


## Gameplay

Questions are served, one at a time, in order, beginning with question #1 (which also provides some basic instructions).  All users playing the game always see the same question.  When one user answers a question correctly, all users see the next question.  Automatic refreshes are intentionally omitted to keep from frustrating users while mid-input.  There is a refresh link that can/should be used frequently to see the latest game updates.  All users will be able to see the current scoreboard.

Some questions require a correct text answer.  Others require a user to be in the "right" location.  Other questions have both constraints.

When the last question is correctly answered, the game is over ... maybe.


### Spoiler

Below contains an actual game spoiler.

The game is rigged to always have the Grinch win.  He will gain points steadily with passing time (that's why the game needs to know the estimated UTC time when the game will be over).  Also, he gains points with all incorrect answers.  Even if a single user answers all questions correctly, he/she will still have less points than the Grinch at the estimated game-end time.

For a human to win, someone must play the martyr and donate points to the Grinch.  Doing so will actually remove points from the Grinch, causing the next human in line to win.


## Admin Interface

Each game can have any number of administrators, who do not participate but ensure that the game continues without any problems and on schedule.  From the [admin panel](https://raw.githubusercontent.com/JElchison/location-based-scavenger-hunt/master/screenshots/Admin.png), an admin has the ability to:
* Manually edit current scores (form at the top)
* Set the current question (radio buttons in the `Cur` column)
* Disable (future) questions (to expedite a long game) (checkboxes in the `Dis` column)
* Reset the game (see below section)

An admin could use a browser on a phone, tablet, or even computer.  No need for location services.


## Resetting a Game

To start a brand new game, or in case of catastrophic failure, admins have the ability to delete all persistent game state.  This can be done via the admin panel, or by accessing the following URL directly:
* `https://your-server-url.here:55864/cgi-bin/reset.py?l=hash` where the hash comes from an admin in the `USERS` list in `game_config.py`.

Non-admins cannot reset games.

After a game reset, all players (including admins) must close all tabs and re-login.


## Sample lighttpd config

```
server.modules = (
        "mod_access",
        "mod_alias",
        "mod_compress",
        "mod_redirect",
#       "mod_rewrite",
        "mod_cgi",
)

server.document-root        = "/var/www"
server.upload-dirs          = ( "/var/cache/lighttpd/uploads" )
server.errorlog             = "/var/log/lighttpd/error.log"
server.pid-file             = "/var/run/lighttpd.pid"
server.username             = "www-data"
server.groupname            = "www-data"
server.port                 = 80


index-file.names            = ( "index.php", "index.html", "index.lighttpd.html" )
url.access-deny             = ( "~", ".inc" )
static-file.exclude-extensions = ( ".php", ".pl", ".fcgi" )

compress.cache-dir          = "/var/cache/lighttpd/compress/"
compress.filetype           = ( "application/javascript", "text/css", "text/html", "text/plain" )

# default listening port for IPv6 falls back to the IPv4 port
## Use ipv6 if available
#include_shell "/usr/share/lighttpd/use-ipv6.pl " + server.port
include_shell "/usr/share/lighttpd/create-mime.assign.pl"
include_shell "/usr/share/lighttpd/include-conf-enabled.pl"

$HTTP["url"] =~ "^/cgi-bin/" {
    cgi.assign = (".py" => "/usr/bin/python")
}

$SERVER["socket"] == ":55864" {
  ssl.engine = "enable" 
  ssl.pemfile = "/etc/lighttpd/certs/lighttpd.pem" 
}

ssl.honor-cipher-order = "enable"
ssl.cipher-list = "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH"
ssl.use-compression = "disable"
setenv.add-response-header = (
    "Strict-Transport-Security" => "max-age=63072000; includeSubdomains; preload",
    "X-Frame-Options" => "DENY",
    "X-Content-Type-Options" => "nosniff"
)
ssl.use-sslv2 = "disable"
ssl.use-sslv3 = "disable"
```


## Licenses

Included software:
* [HTML5-Simon-Says](https://github.com/dbchristopher/HTML5-Simon-Says) -- [GNU v3 license](https://github.com/dbchristopher/HTML5-Simon-Says/blob/master/LICENSE.txt)
    * [MIDI.js](https://github.com/mudcube/MIDI.js) -- [MIT license](https://github.com/mudcube/MIDI.js/blob/master/LICENSE.txt)
* [Skeleton](https://github.com/dhg/Skeleton) CSS -- [MIT license](https://github.com/dhg/Skeleton/blob/master/LICENSE.md)
* [CSS Notification Boxes](http://www.cssportal.com/blog/css-notification-boxes/) -- Unknown license. Consult author/[website](http://www.cssportal.com/blog/css-notification-boxes/).

