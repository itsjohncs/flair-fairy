## Handle Command Line Arguments ##
from optparse import OptionParser, make_option

option_list = [
    make_option("-u", "--username", dest = "username", type = str,
                help = "The username on reddit the bot will use to login."),
    make_option("-p", "--password", dest = "password", type = str,
                help = "The password on reddit the bot will use to login."),
    make_option("-r", "--reddit", dest = "subreddit", type = str,
                help = "The name of the subreddit (eg: badcode) the bot will "
                       "work within."),
    make_option("--refresh-speed", dest = "refresh_speed", type = float,
                default = 30.0,
                help = "The number of time in seconds the bot will wait before "
                       "performing more work."),
    make_option("-q", "--quiet", dest = "quiet", default = False, 
                action = "store_true",
                help = "The bot will not explain all of its actions ad "
                       "nauseum.")
]

parser = OptionParser(
    description = "Ensures the language flair on /r/badcode is updated.",
    option_list = option_list
)

options = parser.parse_args()[0]

# Ensure all required options are present
if not (options.username and options.password and options.subreddit):
    parser.error("Username, password, and subreddit required.")

## Boring Prep Work ##
import time, signal, sys

# Logging is a pain without one of these
def log(message):
    "Logs a message if quiet mode is not enabled."
    
    if not options.quiet:
        print message

# Set it up so if SIGINT is encountered we exit gracefully
exiting = False
def _setExit(a, b):
    global exiting
    
    print >> sys.stderr, "Exiting soon..."
    exiting = True
signal.signal(signal.SIGINT, _setExit)

def wait(seconds):
    """
    Waits a given amount of seconds (floating numbers OK) and then returns True.
    If exiting is True when the function begins or a SIGINT is encountered
    during waiting, False is returned.
    
    """
    
    # Sleep if were not exiting yet
    if not exiting:
        time.sleep(seconds)
        
    # Return True iff were not exiting
    return not exiting
    
# Used to map language names to more better ones
name_map = (
    (r"c\+\+", "cpp"),
    (r"visual ?basic", "vb"),
    (r".*basic.*", "basic")
)

def map_name(name):
    for key, item in name_map:
        if re.match(key, name):
            return item
            
    return name

## Prepwork Done. Let's Reddit! ##
import reddit, requests, re

# Connect to reddit
r = reddit.Reddit(user_agent = "reddit-flair-fairy:/r/badcode owner:brownhead")
log("Connected to reddit.")

# Send login info
r.login(options.username, options.password)
log("Logged in.")

# Connect to the desired subreddit
subreddit = r.get_subreddit(options.subreddit)

# Begin work cycle.... Now!
last_checked = None
while wait(options.refresh_speed):
    log("Beginning work cycle...")
    
    # Grab the posts we will scan through
    if not last_checked:
        # 100 new posts should account for small amounts of bot downtime
        submissions = list(subreddit.get_new_by_date(limit = 100))
    else:
        submissions = list(subreddit.get_new_by_date(
            limit = None, 
            place_holder = last_checked
        ))

    # Mark the first submission as our last checked as it is the most recent.
    # That way when we grab more submissions in the next cycle we'll grab
    # everything more recent that it.
    if submissions:
        last_checked = submissions[0].id

    for i in submissions:
        # If flair has already been added skip this submission
        if i.link_flair_text:
            continue
            
        # Figure out what site were dealing with
        if re.match("http://(www.)?pastebin.com/", i.url):
            site = "pastebin"
        elif re.match("http://(www.)?codepad.org/", i.url):
            site = "codepad"
        else:
            # We can't figure it out... Move along.
            continue
        
        # Get the page
        page = requests.get(i.url)
        if page.status_code != requests.codes.ok:
            log("Could not access %s for post %s" % (i.url, i.title))
            continue
            
        # This could probably be nicer
        language = None
        if site == "pastebin":
            match = re.search(r"<head>.*?<title>\[(.*?)\].*?</title>.*?</head>",
                              page.content, re.DOTALL | re.IGNORECASE)
            
            if match:
                language = match.group(1)
        elif site == "codepad":
            match = re.search(r"<head>.*?<title>(.*?) .*?</title>.*?</head>",
                              page.content, re.DOTALL | re.IGNORECASE)
    
            if match:
                language = match.group(1)
        if not language:
            continue
        
        i.set_flair(map_name(language.lower()))
            
    log("Ending work cycle.")
