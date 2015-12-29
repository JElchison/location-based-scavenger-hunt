#!/usr/bin/python

import datetime

# import Question class from primary file
from game import Question


#
# common configuration information
#

# list of all users, along with a hash to be used for login.
# recommend creating hash with `head -c 8 /dev/random | sha384sum` for 64 bits of entropy.
# 64 bits of entropy, per https://www.owasp.org/index.php/Session_Management_Cheat_Sheet#Session_ID_Entropy
# SHA-384 per https://www.nsa.gov/ia/programs/suiteb_cryptography/
# login URL = /cgi-bin/game.py?l=hash
USERS = [('Alice',   '42da60b18ced0332025d829a90942d78d3e742c5179baa796d1ecd81d69e093b468943cf3a1907e99f5753c6f3aeab6d'),
         ('Bob',     'f89584a7cceb3cf983048ad2fcc934195b4e5469f3bf1b75af8f68da44a8ec2ef66d7a95b6306cbb7e63059d9cc7e6b9'),
         ('Charlie', 'd797f23a8c5f6bc23376b51fd50b025051810058a3a73f7380c147b5f9ce6807fb3c1862006cb686d8f87ac824ab61b8'),
         ('Dan',     '46ae66d11bcbb5b17537402d788a56269dc67589414e2e3d471ec77209a278333dfe804313a870c1ebb43971f6392b92'),
         ('Erin',    'b950beaea33205e7b366c51969344220c3e7352f3079704002af2c5032074f8d934aa857766230452176711e6514bcdf')]
# list of admin users, to be presented with admin interface (instead of normal gameplay).  admin users must also be in USERS list.
ADMIN_USERS = ['Erin']
# name of arch-nemesis
GRINCH_USERNAME = 'The Grinch'
# UTC time that game is expected to end (used to ensure Grinch accrues points quick enough to "win" at the end)
GAME_END_TIME_UTC = datetime.datetime(2015, 12, 24, 22, 00)


#
# obscure configuration information
#

# points constants
POINTS_ADDED_FOR_CORRECT_ANSWER = 50
POINTS_GIVEN_TO_GRINCH_FOR_INCORRECT_ANSWER = 10
POINTS_SUBTRACTED_FOR_PURCHASING_HINT = 30
POINTS_ADDED_FOR_CONVINCING_A_GULLIBLE_TEAMMATE = 2 * POINTS_ADDED_FOR_CORRECT_ANSWER
# location of state file on server
DILL_FILE = '/var/oca/state.dill'
# name of session ID cookie.  recommend something benign like 'id'.
SID_COOKIE_NAME = 'id'
# filename of reset script
RESET_FILENAME = 'reset.py'


# define questions
def setup_questions():
    questions = []

    # question 0
    new_question = Question()
    new_question.question = '''<p>Welcome! This is a Cincinnati-focused location-based Christmas scavenger hunt. This game server will guide you throughout the day, and throughout the city.</p>
<img width=300 src="https://img1.etsystatic.com/034/0/5979785/il_570xN.530057843_jq80.jpg">
<br><br>Your goals:
<ol>
    <li>Don't let the Grinch win. (And no, ''' + ADMIN_USERS[0] + ''' is not the Grinch.) Rest assured, it truly is possible to beat the Grinch. But you may have to think about it...</li>
    <li>Beat your teammates. The winner of this game wins a real, tangible prize (or two). The prize is [TBD].</li>
    <li>Enjoy the time with each other, and some of the best of what Cincinnati has to offer.</li>
</ol>
You will need:
<ul>
    <li>Your charging cable for your phone (and an external battery, if you have one). You'll be using your phone a lot today.</li>
    <li>One of the questions will require a geocaching app. If you don't have one, try these links for <a href="https://itunes.apple.com/us/app/geocaching-intro/id329541503">iPhone</a> and <a href="https://play.google.com/store/apps/details?id=cgeo.geocaching">Android</a>. Go ahead and install it now.</li>
</ul>
Tips:
<ul>
    <li>During this game, please avoid using the page refresh feature in your phone browser. Doing so will repeat your last action, which may not be what you want. Instead, you may click the "Refresh" link at any time, without consequence.</li>
    <li>Just in case you accidentally get logged out, bring your QR code (or login link) with you on the adventure.</li>
</ul>
Alright, that's it for the pep-talk.  Without further ado ... here's an easy question to get you started:
<br><br><b>Have ALL game players read and understood the tips listed in this welcome message?</b> (Please don't leave anyone behind.)
'''
    new_question.answer_texts = []
    new_question.answer_texts.append("Yes")
    new_question.answer_texts.append("Yeah")
    new_question.answer_texts.append("Yep")
    new_question.answer_texts.append("Yup")
    new_question.answer_texts.append("Ya")
    new_question.hints = []
    new_question.hints.append("Type 'Yes' once everyone has read and understood the tips listed in this welcome message.")
    questions.append(new_question)

    # question 1
    new_question = Question()
    # from http://www.essentialwonders.com/coffee-fact-and-trivia/
    new_question.question = "Okay, good. Hopefully that wasn't too hard. Next question... <br>What starts out as a yellow berry, changes into a red berry, and then is picked by hand to harvest?"
    new_question.answer_texts = []
    new_question.answer_texts.append("Coffee")
    new_question.answer_texts.append("Coffee bean")
    new_question.answer_texts.append("Coffee beans")
    new_question.hints = []
    # from https://en.wikipedia.org/wiki/Caffeine
    new_question.hints.append("Primary source of the world's most widely consumed psychoactive drug.")
    new_question.hints.append("Go-go juice.")
    new_question.hints.append("Joe.")
    questions.append(new_question)

    # question 2
    new_question = Question()
    new_question.question = "Great! Let's go get some coffee. Your carriage awaits! <br>Next question for when everyone's in the car (please don't answer until then)... <br>Who is the 8th reindeer?"
    new_question.answer_texts = []
    new_question.answer_texts.append("Blitzen")
    new_question.answer_texts.append("Blixem")
    new_question.answer_texts.append("Blixen")
    new_question.hints = []
    new_question.hints.append("The thing the defensive line does.")
    new_question.free_pass_user = "Alice"
    new_question.bad_answer = "Rudolph"
    questions.append(new_question)

    # question 3
    new_question = Question()
    new_question.question = "Who is the 10th reindeer?"
    new_question.answer_texts = []
    new_question.answer_texts.append("Olive")
    new_question.hints = []
    new_question.hints.append("...used to laugh and call him names...")
    new_question.hints.append("_____ the other reindeer...")
    new_question.hints.append("Turn the words into a name.")
    questions.append(new_question)

    # question 4
    new_question = Question()
    # from http://www.xmasfun.com/Trivia.aspx?Trivia_Quiz_ID=22
    new_question.question = '''Name the Christmas song title with this overly verbose name:  "My parent's mother was involved in an unexpected trampling incident with an antlered creature of the genus Rangifer."'''
    new_question.answer_texts = []
    new_question.answer_texts.append("Grandma Got Run Over By A Reindeer")
    new_question.answer_texts.append("Grandma Got Ran Over By A Reindeer")
    new_question.hints = []
    new_question.hints.append('''<iframe width="420" height="315" src="https://www.youtube.com/embed/cI8aByUXPL0?rel=0&amp;showinfo=0" frameborder="0" allowfullscreen></iframe>''')
    questions.append(new_question)

    # question 5
    new_question = Question()
    # from http://www.xmasfun.com/Trivia.aspx?Trivia_Quiz_ID=22
    new_question.question = '''Name the Christmas song title with this overly verbose name:  "Apply ornamental decorative items to the house's connective passage ways."'''
    new_question.answer_texts = []
    new_question.answer_texts.append("Deck The Halls")
    new_question.hints = []
    new_question.hints.append('''<iframe width="420" height="315" src="https://www.youtube.com/embed/miBKPwVtxFU?rel=0&amp;showinfo=0" frameborder="0" allowfullscreen></iframe>''')
    questions.append(new_question)

    # question 6
    new_question = Question()
    new_question.question = '''Alright, see you at <a href="http://www.yelp.com/biz/deeper-roots-coffee-cincinnati-3">Deeper Roots</a>! Be sure to get your coffee TO GO.'''
    new_question.answer_location = (39.152160, -84.431909)
    questions.append(new_question)

    # question 7
    new_question = Question()
    new_question.question = "Wouldn't it be nice to read something while sipping on this go-go juice?"
    new_question.answer_texts = []
    new_question.answer_texts.append("Yes")
    new_question.answer_texts.append("Yeah")
    new_question.answer_texts.append("Yep")
    new_question.answer_texts.append("Yup")
    new_question.answer_texts.append("Ya")
    new_question.hints = []
    new_question.hints.append('''Not "no". (Yes, that's a double negative.)''')
    questions.append(new_question)

    # question 8
    new_question = Question()
    new_question.question = "Good thinking. Head next door and poke around a bit. <br>When you're done, here's the next question for when everyone's in the car (please don't answer until then)... <br>What else goes great with coffee?"
    new_question.answer_texts = []
    new_question.answer_texts.append("donuts")
    new_question.answer_texts.append("donut")
    new_question.answer_texts.append("doughnuts")
    new_question.answer_texts.append("doughnut")
    new_question.hints = []
    new_question.hints.append('''<br><img width=300 src="http://sherman-ave.com/wp-content/uploads/2014/08/homer-excited.png">''')
    new_question.hints.append("What does Homer like to eat?")
    new_question.hints.append("Dunkin' (but where we're goin' is *way* better)")
    questions.append(new_question)

    # question 9
    new_question = Question()
    # from http://www.xmasfun.com/Trivia.aspx?Trivia_Quiz_ID=8
    new_question.question = "Great! Let's go get some donuts. Next question... <br>While stealing a Christmas tree, the Grinch was caught in the act by a small Who. What was her name?"
    new_question.answer_texts = []
    new_question.answer_texts.append("Cindy-Lou Who")
    new_question.answer_texts.append("Cindy Lou Who")
    new_question.answer_texts.append("Cindy-Lew Who")
    new_question.answer_texts.append("Cindy Lew Who")
    new_question.answer_texts.append("Cindy-Lou")
    new_question.answer_texts.append("Cindy Lou")
    new_question.answer_texts.append("Cindy-Lew")
    new_question.answer_texts.append("Cindy Lew")
    new_question.hints = []
    new_question.hints.append('''<iframe width="420" height="315" src="https://www.youtube.com/embed/AslwI4x4eVU?rel=0&amp;showinfo=0" frameborder="0" allowfullscreen></iframe>''')
    new_question.free_pass_user = "Charlie"
    new_question.bad_answer = "Yahoo"
    questions.append(new_question)

    # question 10
    new_question = Question()
    new_question.question = '''See you at <a href="http://www.yelp.com/biz/holtmans-donut-shop-cincinnati">Holtman's</a>!'''
    new_question.answer_location = (39.110510, -84.515246)
    questions.append(new_question)

    # question 11
    new_question = Question()
    new_question.question = '''Feel free to poke around OTR a bit. When you're ready, go check out <a href="http://www.yelp.com/biz/washington-park-cincinnati">Washington Park</a>.'''
    new_question.answer_location = (39.108833, -84.517413)
    questions.append(new_question)

    # question 12
    new_question = Question()
    new_question.question = "There were 4 presidents from Cincinnati. Who was the most recent?"
    new_question.answer_texts = []
    new_question.answer_texts.append("William Howard Taft")
    new_question.answer_texts.append("William Taft")
    new_question.answer_texts.append("Taft")
    new_question.answer_texts.append("W H Taft")
    new_question.answer_texts.append("W. H. Taft")
    new_question.free_pass_user = "Dan"
    new_question.bad_answer = "Obama"
    questions.append(new_question)

    # question 13
    new_question = Question()
    new_question.question = '''Nice work! When you're hungry, let's head to <a href="http://www.yelp.com/biz/tafts-ale-house-cincinnati">Taft's Ale House</a> for a bite. The games shall resume when you get there!'''
    new_question.answer_texts = []
    new_question.answer_location = (39.111307, -84.517507)
    questions.append(new_question)

    # question 14
    # NOTE: keep in sync with question number embedded in simon_says.js winning URL
    new_question = Question()
    new_question.question = '''Go ahead and order. While you're waiting for your food (and not before), <a href="/simon/">let's play a game</a>.'''
    new_question.display_answer = False
    new_question.answer_texts = []
    new_question.answer_texts.append("878d40e4ed4cc40abed5bc65589cf0837d38de549ccee2814a5d20c61530727c302e7500e77be9f88a90fa6ee9ebbab0")
    new_question.hints = []
    new_question.hints.append("You'll need at least 20")
    new_question.hints.append("A little desperate are we? Just for that, you'll need at least 25. Anyone dare to ask for another hint?")
    new_question.hints.append("You've ruined it for the whole class.")
    new_question.hints.append("One bad apple...")
    questions.append(new_question)

    # question 15
    new_question = Question()
    new_question.question = "Now that that torture is over, what is a building in which objects of historical, scientific, artistic, or cultural interest are stored and exhibited?"
    new_question.answer_texts = []
    new_question.answer_texts.append("museum")
    questions.append(new_question)

    # question 16
    new_question = Question()
    new_question.question = '''When you're done eating, let's go <a href="http://www.yelp.com/biz/cincinnati-art-museum-cincinnati">check one out</a>!'''
    new_question.answer_location = (39.113951, -84.496922)
    questions.append(new_question)

    # question 17
    new_question = Question()
    new_question.question = '''Stay a while. When you're ready to move on, take me to the *original* site of Cincinnati Observatory.'''
    new_question.answer_location = (39.107887, -84.498752)
    new_question.hints = []
    new_question.hints.append("It's not far from the museum.")
    new_question.hints.append("It's atop one of Cincinnati's 7 hills.")
    questions.append(new_question)

    # question 18
    new_question = Question()
    # http://www.xmasfun.com/Trivia.aspx?Trivia_Quiz_ID=21
    new_question.question = '''This round is all about [Alice]. For this question, she can choose her own adventure: Head to Kentucky for an afternoon drink, or head to <a href="http://www.junglejims.com/">Jungle Jim's</a> to pick out a ~$15 bottle of wine for dinner. Once she decides (and not before), here's the next question... <br>Who said "Bah Humbug"?'''
    new_question.answer_texts = []
    new_question.answer_texts.append("Scrooge")
    new_question.answer_texts.append("Ebenezer Scrooge")
    new_question.answer_texts.append("Ebeneezer Scrooge")
    new_question.hints = []
    new_question.hints.append("1843")
    new_question.hints.append("Dickens")
    new_question.hints.append("A Christmas Carol")
    new_question.free_pass_user = "Bob"
    new_question.bad_answer = "Frosty the Snowman"
    questions.append(new_question)

    # question 19
    new_question = Question()
    # http://www.xmasfun.com/Trivia.aspx?Trivia_Quiz_ID=18
    new_question.question = '''In "A Charlie Brown Christmas", how much does Lucy charge for psychiatric help?'''
    new_question.answer_texts = []
    new_question.answer_texts.append("5 cents")
    new_question.answer_texts.append("5 cent")
    new_question.answer_texts.append("Five cents")
    new_question.answer_texts.append("Five cent")
    new_question.answer_texts.append("$0.05")
    new_question.answer_texts.append("0.05")
    new_question.answer_texts.append("$.05")
    new_question.answer_texts.append(".05")
    new_question.answer_texts.append("A nickel")
    new_question.answer_texts.append("Nickel")
    new_question.hints = []
    new_question.hints.append("A single coin")
    new_question.free_pass_user = "Alice"
    new_question.bad_answer = "A new car"
    questions.append(new_question)

    # question 20
    new_question = Question()
    # http://www.xmasfun.com/Trivia.aspx?Trivia_Quiz_ID=18
    new_question.question = '''What traditional Christmas carol does the entire Peanuts gang hum, and then eventually sing at the end of the show?'''
    new_question.answer_texts = []
    new_question.answer_texts.append("Hark The Herald Angels Sing")
    new_question.answer_texts.append("Hark! The Herald Angels Sing")
    new_question.answer_texts.append("Hark, The Herald Angels Sing")
    new_question.hints = []
    new_question.hints.append("Listen, ...")
    new_question.hints.append('''<iframe width="420" height="315" src="https://www.youtube.com/embed/ZP37k831y9U?rel=0&amp;showinfo=0" frameborder="0" allowfullscreen></iframe>''')
    new_question.free_pass_user = "Charlie"
    new_question.bad_answer = "All I Want For Christmas Is You"
    questions.append(new_question)

    # question 21
    new_question = Question()
    # http://www.xmasfun.com/Trivia.aspx?Trivia_Quiz_ID=11
    new_question.question = '''What Christmas movie contains the following quote? "Bless this highly nutritious microwavable macaroni and cheese dinner and the people who sold it on sale. Amen."'''
    new_question.answer_texts = []
    new_question.answer_texts.append("Home Alone")
    new_question.hints = []
    new_question.hints.append('''<br><img width=300 src="http://cdn.hark.com/images/000/487/802/487802/original.jpg">''')
    new_question.free_pass_user = "Bob"
    new_question.bad_answer = "Miracle On 34th Street"
    questions.append(new_question)

    # question 22
    new_question = Question()
    new_question.question = '''Switching gears... Who is this famous actor? <br><img width=300 src="https://s3.amazonaws.com/media.tmz.com/2014/11/19/1119-macauley-main-300x250.jpg">'''
    new_question.answer_texts = []
    new_question.answer_texts.append("Macaulay Culkin")
    new_question.hints = []
    new_question.hints.append('''<br><img width=300 src="http://images-cdn.moviepilot.com/image/upload/c_fill,h_1463,w_2197/t_mp_quality/macaulay-culkin-i-bet-you-can-t-guess-what-macaulay-culkin-s-been-up-to-recently-jpeg-223591.jpg">''')
    new_question.hints.append('''<br><img width=300 src="http://a4.files.biography.com/image/upload/c_fill,cs_srgb,dpr_1.0,g_face,h_300,q_80,w_300/MTE5NDg0MDU0NzQyNjY0NzE5.jpg">''')
    new_question.hints.append('''<br><img width=300 src="http://images-cdn.moviepilot.com/images/c_fill,h_809,w_666/t_mp_quality/jdrlitljl0789ggree1z/the-story-of-what-really-happened-to-macaulay-culkin-when-his-star-started-to-fade-448101.jpg">''')
    new_question.free_pass_user = "Dan"
    new_question.bad_answer = "Will Smith"
    questions.append(new_question)

    # question 23
    new_question = Question()
    new_question.question = '''Go <a href="https://www.geocaching.com/geocache/GC395V8_a-grate-place-to-play-ball">find this</a>. (Use your geocaching app.)'''
    new_question.answer_location = (39.41481666666667, -84.35875)
    new_question.answer_texts = []
    # http://img14.deviantart.net/24f3/i/2010/361/b/4/santa_jaws_by_starkelstar-d35sqwt.jpg
    new_question.answer_texts.append("Santa Jaws")
    new_question.hints = []
    new_question.hints.append('''The title of the cache is intentionally spelled.''')
    new_question.hints.append('''Of the two grates, pay attention to the west one.''')
    new_question.hints.append('''It's on the end of the string.''')
    new_question.hints.append('''Enter what you find on the paper as the answer to this question.''')
    questions.append(new_question)

    return questions
