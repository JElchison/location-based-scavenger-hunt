#!/usr/bin/python

import cgi
import cgitb
import os
import Cookie
import sys

# import user/login table
from game_config import *


#
# classes
#

# question object
class Question:
    def __init__(self):
        # string representing the question.  may contain HTML.
        self.question = None
        # boolean indicating whether the "answer" input field should be displayed (set to False for location-only questions)
        self.display_answer = True
        # tuple representing latitude/longitude for answer location (set to None for no location)
        self.answer_location = None
        # list of strings representing acceptable answers.  NOT case sensitive.  (set to None for no text-based answers)
        self.answer_texts = None
        # list of strings representing hints that users can purchase
        self.hints = None
        # string matching username of user who cannot answer this question.  instead, he/she must try to convince another user to input one the "bad answer" below for an added bonus.
        self.free_pass_user = None
        # string representing an obviously incorrect answer.  see self.free_pass_user.
        self.bad_answer = None


#
# functions
#

# kill the session without revealing any information
def kill_session():
    print "Content-Type: text/html"
    print
    # don't print HTML_HEADER since it reveals information about application
    print "No soup for you!"
    # error exit
    sys.exit(1)


# authenticate using GET parameter
def check_login(state, form):
    my_user = None
    my_set_cookie = Cookie.SimpleCookie()

    # login hash will come in on 'l' variable
    login_hash = form.getfirst("l")

    if login_hash:
        # cycle through all users
        for (try_user, try_login) in USERS:
            if login_hash == try_login:
                my_user = try_user
        if not my_user:
            # someone tried to login, but had an invalid hash.  possible attack.
            kill_session()

    return my_user, my_set_cookie


# authenticate
def get_user(state, form, cookie):
    # look for new login *only* (no cookie-based auth for reset)
    user, set_cookie = check_login(state, form)

    return user, set_cookie


def main():
    # Optional; for debugging only
    cgitb.enable()

    # load CGI environment
    form = cgi.FieldStorage()

    # load cookies
    cookie = Cookie.SimpleCookie()

    # get current user
    user, set_cookie = get_user(None, form, cookie)
    if not user:
        kill_session()

    # begin HTTP response
    print "Content-Type: text/html"
    print

    try:
        os.remove(DILL_FILE)
        print "Removed " + DILL_FILE
    except Exception as e:
        print e


if __name__ == "__main__":
    main()
