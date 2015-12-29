#!/usr/bin/python

import cgi
import cgitb
import hashlib
import os
import Cookie
import datetime
import dill
import sys
import operator
import geopy.distance

# import user/login table, configuration, and questions
from game_config import *


#
# constants
#

# following must be a float; overwritten after questions are defined
GRINCH_MAX = 1000.0
# feet within which to consider a user within range (less than 100ft will give you problems)
FEET_WITHIN_RANGE = 100
# cache filename of this script
SELF_FILENAME = os.path.basename(__file__)
# HTML header to be used after successful login
HTML_HEADER = '''
<!DOCTYPE html>
<html lang="en">
<head>

  <!-- Basic Page Needs -->
  <meta charset="utf-8">
  <title>Location-Based Scavenger Hunt</title>

  <!-- Mobile Specific Metas -->
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <!-- FONT -->
  <link href="//fonts.googleapis.com/css?family=Raleway:400,300,600" rel="stylesheet" type="text/css">

  <!-- CSS -->
  <link rel="stylesheet" href="../css/normalize.css">
  <link rel="stylesheet" href="../css/skeleton.css">
  <link rel="stylesheet" href="../css/box.css">

</head>
<body>

  <!-- Primary Page Layout -->
  <div class="container">
    <div class="row">
      <div class="one-half column" style="margin-top: 5%">
        <b>Location-Based Scavenger Hunt</b>
'''

# HTML footer to be used after HTML_HEADER
HTML_FOOTER = '''
      </div>
    </div>
  </div>

<!-- End Document -->
</body>
</html>
'''


#
# classes
#

# game state object, to be persisted
class GameState:
    def __init__(self):
        # contains a dictionary of session IDs for logged in users
        self.session_id = {}
        # contains a dictionary of scores for all users
        self.score = {}
        # zero-based index
        self.current_question_number = 0
        # contains a list of disabled questions
        self.disabled_questions = []
        # number of hints revealed for current question
        self.hints_revealed_this_question = 0
        # banner message displayed atop every page, to notify other users about the most recent game event
        self.last_message = None
        # track when the first user logged in
        self.game_start_time = None
        # track the Grinch's score at game end, so that it doesn't keep increasing with time
        self.final_grinch_score = 0

        # start with scores of 0
        for user, login in USERS:
            if user not in ADMIN_USERS:
                self.score[user] = 0
        self.score[GRINCH_USERNAME] = 0


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

# read persistent state from file
def read_state():
    # default state
    state = GameState()

    dill_file = None
    try:
        # open for read
        dill_file = open(DILL_FILE, 'rb')
        # overwrite default state
        state = dill.load(dill_file)
    except IOError:
        # not necessarily a problem, this may be the beginning of the game (with no state saved yet)
        pass
    finally:
        if dill_file:
            dill_file.close()

    return state


# write persistent state to file
def write_state(state):
    dill_file = None
    try:
        # open for write
        dill_file = open(DILL_FILE, 'wb')
        # dump state
        dill.dump(state, dill_file)
    except IOError:
        # this can happen when to users submit a form at the same time.  instead of trying to merge states, just tell all subsequent users to try again.  pretty unlikely this will happen in games with small numbers of users.
        print '''<div class="alert-box warning"><span>Oh no! </span>Server was busy with another request. Please try again. :-/</div>'''
    finally:
        if dill_file:
            dill_file.close()


# kill the session without revealing any information
def kill_session():
    print "Content-Type: text/html"
    print
    # don't print HTML_HEADER since it reveals information about application
    print "No soup for you!"
    # error exit
    sys.exit(1)


# generate new session ID
def generate_sid():
    # 64 bits of entropy, per https://www.owasp.org/index.php/Session_Management_Cheat_Sheet#Session_ID_Entropy
    # SHA-384 per https://www.nsa.gov/ia/programs/suiteb_cryptography/
    return hashlib.sha384(os.urandom(8)).hexdigest()


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
        if not state.game_start_time:
            # the game just started (first person logged in).  record start time (in UTC).
            state.game_start_time = datetime.datetime.utcnow()

    if my_user:
        # authentication success.
        # generate new session ID.
        sid = generate_sid()
        # save new session ID in state (replace any previous sid)
        state.session_id[my_user] = sid
        # also save new session ID in user cookie
        my_set_cookie[SID_COOKIE_NAME] = sid
        # set cookie expiration
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)  # login expires in 1 day
        my_set_cookie[SID_COOKIE_NAME]['expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")

        # redirect to page without login param
        print "Location: " + SELF_FILENAME
        print my_set_cookie
        print

        # need to write the state before we redirect
        write_state(state)

        # non-error exit
        sys.exit(0)

    return my_user, my_set_cookie


# authenticate using cookie containing session ID
def check_cookie(state, cookie):
    # cycle through all users
    for (try_user, try_login) in USERS:
        try:
            # does session ID in cookie match current user's active session?
            if cookie[SID_COOKIE_NAME].value == str(state.session_id[try_user]):
                # authentication success
                return try_user
        except KeyError:
            pass
    # authentication failure
    return None


# authenticate
def get_user(state, form, cookie):
    # look for new login first
    user, set_cookie = check_login(state, form)
    if not user:
        # no GET parameter.  check for session cookie.
        user = check_cookie(state, cookie)

    return user, set_cookie


# ensure that QUERY_STRING contains location
def assert_location(form):
    lat = form.getfirst("lat")
    lon = form.getfirst("lon")

    if lat and lon:
        # success
        return

    # no location in QUERY_STRING.  must add it now.

    # get existing QUERY_STRING
    try:
        query_string = os.environ['QUERY_STRING']
    except KeyError:
        query_string = ""

    # get lat/lon, then prepend them to the query string
    print '''
<!DOCTYPE html>
<html lang="en">
<head>
<script>
navigator.geolocation.getCurrentPosition(showPosition);
function showPosition(position) {
    window.location = "''' + SELF_FILENAME + '''?lat=" + position.coords.latitude + "&lon=" + position.coords.longitude + "&''' + query_string + '''";
}
</script>
</head>
</html>
'''
    # state not changed, no need to write it.  okay to exit after redirect.
    # non-error exit.
    sys.exit(0)


def get_grinch_score(state):
    if state.final_grinch_score == 0:
        # game is still ongoing.

        # how long should the game go on?
        max_gameplay = int((GAME_END_TIME_UTC - state.game_start_time).total_seconds())
        # how much of the game has transpired?
        gameplay_so_far = max(min(int((datetime.datetime.utcnow() - state.game_start_time).total_seconds()), max_gameplay), 0)
        # in addition to standard score, add factor that increases with passing time
        return state.score[GRINCH_USERNAME] + int(GRINCH_MAX * gameplay_so_far / max_gameplay)
    else:
        # game has ended
        return state.final_grinch_score


def print_score_table(state, user):
    scores = {}

    is_admin = (user in ADMIN_USERS)

    print '<br><table>'

    # cycle through all users
    for my_user, my_login in USERS:
        # but omit admin users
        if my_user not in ADMIN_USERS:
            # store score in local dictionary
            scores[my_user] = state.score[my_user]
    # add grinch's score to local dictionary
    scores[GRINCH_USERNAME] = get_grinch_score(state)
    # sort scores, winner at top
    sorted_scores = sorted(scores.items(), key=operator.itemgetter(1))[::-1]

    # print one row per non-admin user
    for my_user, score in sorted_scores:
        # bold current user
        if my_user == user:
            bold_open = '<b>'
            bold_close = '</b>'
        else:
            bold_open = ''
            bold_close = ''

        # make grinch red
        if my_user == GRINCH_USERNAME:
            color = ' color: red;'
        else:
            color = ''

        # adjust padding to fit more vertically
        print '<tr>'
        print '<td style="' + color + '">' + bold_open + my_user + bold_close + '</td>'

        # right-justify score number
        if is_admin and my_user == GRINCH_USERNAME:
            print '<td style="text-align: right;' + color + '">' + str(state.score[GRINCH_USERNAME]) + ' --> ' + bold_open + str(score) + bold_close + '</td>'
        else:
            print '<td style="text-align: right;' + color + '">' + bold_open + str(score) + bold_close + '</td>'

        if is_admin:
            # for admins, include an extra input field that lets them manually adjust score
            print '<td><input name="set_score_' + my_user + '" size="5" /></td>'

        print '</tr>'

    print '</table>'


def get_winner(state):
    scores = {}

    # cycle through all users
    for my_user, my_login in USERS:
        # but omit admin users
        if my_user not in ADMIN_USERS:
            # store score in local dictionary
            scores[my_user] = state.score[my_user]
    # add grinch's score to local dictionary
    scores[GRINCH_USERNAME] = get_grinch_score(state)
    # sort scores, winner at top
    sorted_scores = sorted(scores.items(), key=operator.itemgetter(1))[::-1]

    # return user with highest score.
    # FTODO:  return multiple in case of tie.
    return sorted_scores[0][0]


def print_game_header(user):
    print HTML_HEADER
    print '<br>Welcome, ' + user
    print '<br><a href="' + SELF_FILENAME + '">Refresh scores/location</a>'
    print '<br>'


# ensure current question has not been disabled since state last set
def verify_state(state, questions):
    if state.current_question_number in state.disabled_questions:
        advance_question(state, questions)


# move to next question
def advance_question(state, questions):
    # this can intentionally overflow
    state.current_question_number += 1
    # reset question-specific state
    state.hints_revealed_this_question = 0
    # verify new state (this can recurse)
    verify_state(state, questions)


def handle_hint(state, form, user, questions):
    # ensure that the question hasn't advanced since this was submitted
    question_number_answered = int(form.getfirst("q"))
    if question_number_answered == state.current_question_number:

        # do we have any hints left to reveal?
        if questions[state.current_question_number].hints and state.hints_revealed_this_question < len(questions[state.current_question_number].hints):
            # yes.  reveal next hint.
            state.hints_revealed_this_question += 1
            # user must pay!
            state.score[user] -= POINTS_SUBTRACTED_FOR_PURCHASING_HINT
            # notify the other teammates about the new hint
            state.last_message = user + ' bought hint #' + str(state.hints_revealed_this_question) + ' for ' + str(POINTS_SUBTRACTED_FOR_PURCHASING_HINT) + ' points, and it is now listed below.'


def handle_donation(state, form, user):
    # wrap this in a try/except block as cheap user input validation
    try:
        # are we donating to the grinch?
        if form.getfirst("to") != GRINCH_USERNAME:
            # no, donating to a normal user

            # how many points to donate?
            # yes, this intentionally accepts negative numbers.
            points = int(form.getfirst("p").strip())

            if points < 0:
                # block attempts to steal from other users
                print '''<div class="alert-box warning"><span>Nice try! </span>I like the way you think, but no stealing, please.</div>'''
                # no actual donation
                points = 0
                # NOTE next line is 'elif' (but doesn't need to be).  only to prevent multiple messages.
            elif state.score[user] <= 0:
                # can only donate if have positive points
                print '''<div class="alert-box warning"><span>Nice try! </span>It's the thought that counts, right?</div>'''
                # no actual donation
                points = 0
                # NOTE next line is 'elif' (but doesn't need to be).  only to prevent multiple messages.
            elif points > state.score[user]:
                # can only donate what you have
                print '''<div class="alert-box warning"><span>Oops! </span>You can't donate more points than you have. How does an empty piggy bank sound?</div>'''
                # allow donation, but cut off at max
                points = state.score[user]

            # redundant if-check
            if points > 0:
                # subtract from source
                state.score[user] -= points
                # add to destination
                state.score[form.getfirst("to")] += points
                # let user know donation was successful
                print '''<div class="alert-box notice"><span>Smell that? </span>THAT's Christmas cheer. (Or maybe bean soup. Where's ''' + ADMIN_USERS[0] + '''?)</div>'''
        else:
            # yes, donating to the grinch

            # how many points to donate?
            # yes, this intentionally accepts negative numbers.
            points = int(form.getfirst("p").strip())

            if points < 0:
                # block attempts to steal from grinch
                print '''<div class="alert-box warning"><span>Nice try! </span>Stealing from ''' + GRINCH_USERNAME + '''? Now that's a bit too far. Do unto others...</div>'''
                # penalize user (adding a negative)
                state.score[user] += points
                # no actual donation
                points = 0
                # NOTE next line is 'elif' (but doesn't need to be).  only to prevent multiple messages.
            elif state.score[user] <= 0:
                # intentionally allow user to donate points to the grinch, even if they're already negative
                pass
                # NOTE next line is 'elif' (but doesn't need to be).  only to prevent multiple messages.
            elif points > state.score[user]:
                # intentionally allow user to donate more points to the grinch than they have
                pass

            # redundant if-check
            if points > 0:
                # subtract from source
                state.score[user] -= points
                # SUBTRACT a multiplier from grinch (this is how we guarantee that a non-grinch will eventually win)
                state.score[GRINCH_USERNAME] -= 10 * points
                # drop a hint
                print '<div class="alert-box warning"><span>Yuck! </span>' + GRINCH_USERNAME + ' HATES Christmas cheer. Stop it already.</div>'
    except Exception as e:
        # this is how we report errors parsing integers
        print '<div class="alert-box warning"><span>Exception: </span>' + str(e) + '</div>'


def calculate_distance_to(form, point):
    lat = form.getfirst("lat")
    lon = form.getfirst("lon")

    if lat and lon:
        current_location = (lat, lon)
        return geopy.distance.distance(current_location, point).miles * 5280
    else:
        return None


def is_within_range(form, point):
    return calculate_distance_to(form, point) <= FEET_WITHIN_RANGE


# where we handle normal answers (both text and location)
def handle_answer(state, form, user, questions):
    # initialize
    skip_last_message = False

    # initialize
    is_text_correct = False
    # perform lookup once
    answer_texts = questions[state.current_question_number].answer_texts

    # only proceed if there was a form submission, and there an answer was given
    if form.getfirst("s") == "Submit" and form.getfirst("a") and len(form.getfirst("a").strip()) > 0:
        # ensure that the question hasn't advanced since this was submitted
        question_number_answered = int(form.getfirst("q"))
        if question_number_answered == state.current_question_number:

            # first, look for a "bad answer"
            if questions[state.current_question_number].free_pass_user and questions[state.current_question_number].bad_answer:
                provided_answer = form.getfirst("a").lower().strip()
                if provided_answer == questions[state.current_question_number].bad_answer.lower().strip():
                    # ha!  someone fell for it.  bonus points for the free_pass_user.
                    state.score[questions[state.current_question_number].free_pass_user] += POINTS_ADDED_FOR_CONVINCING_A_GULLIBLE_TEAMMATE

            # second, parse normal text answers
            if answer_texts:
                provided_answer = form.getfirst("a").lower().strip()
                for answer_text in answer_texts:
                    if provided_answer == answer_text.lower().strip():
                        # correct!
                        is_text_correct = True
                        break

    # initialize
    is_location_correct = False
    # perform lookup once
    answer_location = questions[state.current_question_number].answer_location
    if answer_location:
        if is_within_range(form, answer_location):
            is_location_correct = True

    if (not answer_texts or is_text_correct) and (not answer_location or is_location_correct):
        # correct!

        if answer_texts:
            print '<div class="alert-box success"><span>Correct! </span>+' + str(POINTS_ADDED_FOR_CORRECT_ANSWER) + ' points for you.<br>Tell your teammates to click the "Refresh" link for the next question (not the browser button).</div>'
            state.last_message = user + ' answered question ' + str(state.current_question_number + 1) + ' correctly with the answer <b>' + form.getfirst("a").strip() + '</b>. The next question is listed below.'
        else:
            print '<div class="alert-box success"><span>You found it! </span>+' + str(POINTS_ADDED_FOR_CORRECT_ANSWER) + ' points for you.<br>Tell your teammates to click the "Refresh" link for the next question (not the browser button).</div>'
            state.last_message = user + ' found the location for question ' + str(state.current_question_number + 1) + '. The next question is listed below.'
        # answerer doesn't need to see their own message
        skip_last_message = True
        state.score[user] += POINTS_ADDED_FOR_CORRECT_ANSWER
        advance_question(state, questions)
    else:
        # not correct.  but not necessarily incorrect.

        # only proceed if there was a form submission, and there an answer was given
        if form.getfirst("s") == "Submit" and form.getfirst("a") and len(form.getfirst("a").strip()) > 0:
            # ensure that the question hasn't advanced since this was submitted
            question_number_answered = int(form.getfirst("q"))
            if question_number_answered == state.current_question_number:

                # only print an error message (and penalize points) if this question has a text answer
                if answer_texts:
                    print '<div class="alert-box error"><span>Incorrect. </span>-' + str(POINTS_GIVEN_TO_GRINCH_FOR_INCORRECT_ANSWER) + ' points for you, +' + str(POINTS_GIVEN_TO_GRINCH_FOR_INCORRECT_ANSWER) + ' for ' + GRINCH_USERNAME + '.</div>'
                    state.score[user] -= POINTS_GIVEN_TO_GRINCH_FOR_INCORRECT_ANSWER
                    state.score[GRINCH_USERNAME] += POINTS_GIVEN_TO_GRINCH_FOR_INCORRECT_ANSWER

        if answer_location:
            print '''<div class="alert-box notice"><span>Close, but... </span>You're still ''' + str(int(calculate_distance_to(form, answer_location))) + ''' feet away.</div>'''

    # pass this state back
    return skip_last_message


def print_hints(state, user, questions):
    # only print list if we have revealed hints
    if questions[state.current_question_number].hints and (state.hints_revealed_this_question > 0 or user in ADMIN_USERS):
        print '<ul>'
        # cycle all hints for this question
        for i in range(len(questions[state.current_question_number].hints)):
            # has this hint been revealed?
            if i < state.hints_revealed_this_question:
                # yes.  print hint.
                print '<li style="color: blue"><b>Hint #' + str(i + 1) + '</b>: ' + questions[state.current_question_number].hints[i] + '</li>'
            elif user in ADMIN_USERS:
                # no, but this is for an admin.  print hint in gray.
                print '<li style="color: gray"><b>Hint #' + str(i + 1) + '</b>: ' + questions[state.current_question_number].hints[i] + '</li>'
        print '</ul>'


def print_hints_remaining(state, user, questions):
    hints_remaining = 0
    if questions[state.current_question_number].hints:
        hints_remaining = len(questions[state.current_question_number].hints) - state.hints_revealed_this_question
    # sanity check
    if hints_remaining < 0:
        hints_remaining = 0

    # only show "Hint" button if we have hints remaining
    if hints_remaining > 0 and user not in ADMIN_USERS:
        print '''<button type="submit" name="s" value="Hint">Hint</button>&nbsp;&nbsp;&nbsp;'''

    # always print number of hints remaining
    print str(hints_remaining) + ' hints remaining'


# print controls to donate points to other users
def print_donate_points(user):
    print 'Be cheery. Donate some points to your losing teammates.'
    print '<form>'

    # cycle through all users
    for my_user, my_login in USERS:
        # but omit self + admin users
        if my_user != user and my_user not in ADMIN_USERS:
            # radio button for each
            print '<input type="radio" name="to" value="' + my_user + '"> ' + my_user + '<br>'
    # radio button for grinch
    print '<input type="radio" name="to" value="' + GRINCH_USERNAME + '"> ' + GRINCH_USERNAME + '<br>'

    print 'Points to donate: <input name="p" size="5" />'
    print '<br><input type="submit" value="Donate">'
    print '</form>'


def is_game_over(state, questions):
    return state.current_question_number >= len(questions)


# standard gameplay routine
def run_gameplay(state, form, user, questions):
    # ensure that QUERY_STRING contains location
    assert_location(form)

    # ensure current question has not been disabled since state last set
    verify_state(state, questions)

    print_game_header(user)

    # initialize
    skip_last_message = False

    if form.getfirst("s") == "Hint":
        handle_hint(state, form, user, questions)
    elif form.getfirst("p"):
        handle_donation(state, form, user)
    else:
        # only handle answer if game is not over
        if not is_game_over(state, questions):
            skip_last_message = handle_answer(state, form, user, questions)

    # print last message for all to see
    if state.last_message and not skip_last_message and not is_game_over(state, questions):
        print '<div class="alert-box notice">' + state.last_message + '</div>'

    print_score_table(state, user)

    if not is_game_over(state, questions):
        # game is not over

        print '<b>Question ' + str(state.current_question_number + 1) + '</b> of ' + str(len(questions)) + '<br>'
        print questions[state.current_question_number].question
        print '<br>'
        print '<br>'

        print_hints(state, user, questions)

        if user == questions[state.current_question_number].free_pass_user and questions[state.current_question_number].bad_answer:
            # current user gets secret pass
            print '<div class="alert-box warning"><span>Shhhhh! </span>You get a secret pass! Take a break while your teammates solve this one for you. +' + str(POINTS_ADDED_FOR_CONVINCING_A_GULLIBLE_TEAMMATE) + ' bonus points for you if you can convince one of them to enter <b>' + questions[state.current_question_number].bad_answer + '</b> as the answer!</div>'
        else:
            # no secret pass for current user
            print '<form id="mainform"><input type="hidden" name="q" value="' + str(state.current_question_number) + '">'

            # only print "answer" input field if we're supposed to
            if questions[state.current_question_number].answer_texts and questions[state.current_question_number].display_answer:
                print 'Enter your answer here:<br><input name="a" size="35" /><br><br><button type="submit" name="s" value="Submit">Submit</button>'

            print '<br>'
            print_hints_remaining(state, user, questions)
            print '</form>'

        print_donate_points(user)
    else:
        # game is over!

        print '<h3>Congratulations!</h3>'
        print '''<p>You've completed the challenge.</p>'''

        winner = get_winner(state)
        if winner == GRINCH_USERNAME:
            # grinch is winning.  give the humans a chance to fix that.

            print '<p><b>Now if you could only stop ' + GRINCH_USERNAME + '...</b></p>'
            # not-so-subtle hint...
            print_donate_points(user)
        else:
            # humans won!

            print '<p>And the winner is... <b>' + winner + '</b>!'
            if state.final_grinch_score == 0:
                # mark final grinch score, so it no longer climbs with passing time
                state.final_grinch_score = get_grinch_score(state)

    print HTML_FOOTER


# handle form inputs from admin panel
def handle_admin(state, form, user, questions):
    # better safe than sorry
    if user in ADMIN_USERS:

        mode = form.getfirst("s")

        if mode == "Score":
            # top form was submitted.  adjust scores.

            for my_user, my_login in USERS:
                if my_user not in ADMIN_USERS:
                    new_score = form.getfirst("set_score_" + my_user)
                    if new_score:
                        # wrap this in a try/except block as cheap user input validation
                        try:
                            state.score[my_user] = int(new_score.strip())
                        except Exception as e:
                            # this is how we report errors parsing integers
                            print '<div class="alert-box warning"><span>Exception: </span>' + str(e) + '</div>'
            # repeat once more for the Grinch
            my_user = GRINCH_USERNAME
            new_score = form.getfirst("set_score_" + my_user)
            if new_score:
                # wrap this in a try/except block as cheap user input validation
                try:
                    state.score[my_user] = int(new_score.strip())
                except Exception as e:
                    # this is how we report errors parsing integers
                    print '<div class="alert-box warning"><span>Exception: </span>' + str(e) + '</div>'

        elif mode == "State":
            # bottom form was submitted.  adjust game state.

            new_current_question_number = form.getfirst("set_current_question_number")
            if new_current_question_number:
                # wrap this in a try/except block as cheap user input validation
                try:
                    state.current_question_number = int(new_current_question_number)
                except Exception as e:
                    # this is how we report errors parsing integers
                    print '<div class="alert-box warning"><span>Exception: </span>' + str(e) + '</div>'
                # reset question-specific state
                state.hints_revealed_this_question = 0
                # verify new state (this can recurse)
                verify_state(state, questions)

            # start with an empty slate.  an absent param means unchecked.
            state.disabled_questions = []
            for i in range(len(questions)):
                new_disable_question = form.getfirst("set_disabled_question_" + str(i))
                if new_disable_question:
                    if new_disable_question == "on":
                        state.disabled_questions.append(i)


def display_admin_panel(state, form, user, questions):
    # better safe than sorry
    if user in ADMIN_USERS:

        print_game_header(user)

        # handle inputs from admin panel, if any
        handle_admin(state, form, user, questions)

        print '<form id="scoreform">'
        print_score_table(state, user)
        print '''<button type="submit" name="s" value="Score">Update Scores</button>'''
        print '</form>'

        # only print hints if game is ongoing
        if not is_game_over(state, questions):
            print_hints(state, user, questions)
            print_hints_remaining(state, user, questions)

        print '<form id="statusform">'
        print '<br><br><table>'
        print '<tr>'
        print '<th>Cur</th>'
        print '<th>Dis</th>'
        print '<th>Question</th>'
        print '</tr>'

        i = 0
        for question in questions:
            print '<tr>'
            print '<td><input type="radio" name="set_current_question_number" value="' + str(i) + '"'
            if i == state.current_question_number:
                print " checked"
            print '></td>'
            print '<td><input type="checkbox" name="set_disabled_question_' + str(i) + '"'
            if i in state.disabled_questions:
                print " checked"
            print '></td>'
            print '<td>' + question.question
            if question.answer_texts:
                # extra check to keep things displaying pretty on the admin panel
                if question.answer_texts[0] != '878d40e4ed4cc40abed5bc65589cf0837d38de549ccee2814a5d20c61530727c302e7500e77be9f88a90fa6ee9ebbab0':
                    print ' <i>' + str(question.answer_texts) + '</i>'
            if question.answer_location:
                print ' <i>' + str(question.answer_location) + '</i>'
            print '</td>'
            print '</tr>'
            i += 1

        print '</table>'
        print '''<button type="submit" name="s" value="State">Update State</button>'''
        print '</form>'

        # include link for admins to delete all game state
        admin_login = [my_login for my_user, my_login in USERS if my_user == user][0]
        print '<br><a href="' + RESET_FILENAME + '?l=' + admin_login + '">Delete game state</a>. <b>Danger!</b> This is the nuclear option. All game state will be permanently erased. Also, all logins will be invalidated. To restart, all gameplayers (including admins like you) must close all browser tabs and login again.'

        print HTML_FOOTER


def main():
    global GRINCH_MAX

    # Optional; for debugging only
    cgitb.enable()

    # read persistent state
    state = read_state()

    # load CGI environment
    form = cgi.FieldStorage()

    # load cookies
    cookie = Cookie.SimpleCookie()
    try:
        cookie.load(os.environ['HTTP_COOKIE'])
    except KeyError:
        pass

    # get current user
    user, set_cookie = get_user(state, form, cookie)
    if not user:
        kill_session()

    # begin HTTP response
    print "Content-Type: text/html"
    if set_cookie:
        print set_cookie
    print

    # import questions
    questions = setup_questions()
    # following must be a float, and cannot be set until after questions are defined
    GRINCH_MAX = 1.0 * POINTS_ADDED_FOR_CORRECT_ANSWER * len(questions)

    if user not in ADMIN_USERS:
        # non-admin user
        run_gameplay(state, form, user, questions)
    else:
        # admin user
        display_admin_panel(state, form, user, questions)

    # always write game state back to file
    write_state(state)


if __name__ == "__main__":
    main()
