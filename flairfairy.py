'''Sets links flair depending on the used programming language in the link
'''

import argparse
import json
import logging # Needed for the logging command line argument default
import os
import re
import sys
from time import sleep

import praw
import requests

from settings import (HISTORY_SIZE, HISTORY_FILE, LOG_FILE,
                      code_sites, name_dict, languages_with_css_icons)

def parse_commandline_arguments():
    '''Parse and return arguments after sanity checks'''
    parser = argparse.ArgumentParser('Sets links flair depending on the used '+
                                     'programming language in the link')
    parser.add_argument('-u', '--username', 
                    help = "The username on reddit the bot will use to login."),
    parser.add_argument('-p', '--password', 
                    help = "The password on reddit the bot will use to login."),
    parser.add_argument("-r", "--subreddit", default = "badcode",
                    help = "The name of the subreddit (eg: badcode) the bot "
                           "will work within."),
    parser.add_argument("--refresh-speed", type = float, default = 30.0,
                    help = "The number of time in seconds the bot will wait "
                           "before performing more work."),
    parser.add_argument("-q", "--quiet", action = "store_true",
                    help = "The bot will not explain all of its actions ad "
                           "nauseum."),
    parser.add_argument("--debug", action = "store_true",
                    help = "The fairy will not make any changes, rather it "
                           "will only announce the changes it would make."),
    parser.add_argument("-l", "--log-level", default = 'DEBUG',
                    help = "Only log events at higher than this value."),
    parser.add_argument("--blow-away", action = "store_true",
                    help = "Robot will not ignore posts with flair.")
    args = parser.parse_args()
    # Negative refresh_speed will cause a crash in time.sleep
    if args.refresh_speed < 0:
        args.refresh_speed = 3
    # Turn a log level like DEBUG into their int representation
    try:
        args.log_level = getattr(logging, args.log_level.upper())
    except AttributeError:
        print >> sys.stderr, "FATAL: Invalid log level. See help."
        sys.exit(1)
    return args

def setup_logger():
    '''Setup logging to the file specified in settings.py'''
    log = logging.getLogger("flairfairy")

    if not options.quiet:
        fh = logging.FileHandler(LOG_FILE)
        fh.setFormatter(logging.Formatter(
            "[%(asctime)s] %(name)s.%(levelname)s: %(message)s"))
        topLog = logging.getLogger("flairfairy")
        topLog.setLevel(options.log_level)
        topLog.addHandler(fh)

    return logging.getLogger("flairfairy")

def connect_to_reddit():
    return praw.Reddit(
        user_agent = "bot:flair-fairy updates Flair for submissions after which" +
                     " programming language they contain. Owner by u/brownhead." +
                     " More info: github.com/brownhead/flair-fairy")

def login_to_reddit():
    try:
        r.login(options.username, options.password)
        subreddit = r.get_subreddit(options.subreddit)
        if r.user not in subreddit.get_moderators():
            print >> sys.stderr, "User not moderator of %s" % options.subreddit
            sys.exit(1)
    except praw.errors.InvalidUserPass:
        print >> sys.stderr, "FATAL: Invalid user, password combination."
        sys.exit(1)

def make_shortname(long_name):
    '''Turn a long version of a language like javascript into the short js'''
    for regex, shortname in name_dict.iteritems():
        if re.match(regex, long_name, re.IGNORECASE) != None:
            return shortname
    return long_name

def find_flair_icon(language):
    '''Return the name of the icon matching the language'''
    if language == 'vb.net':
        return 'vb icon'
    elif language == 'c/c++':
        return 'cpp icon'
    elif language == 'c#':
        return 'csharp icon'
    elif language == 'asp/asp.net':
        return 'asp icon'
    elif language == 'objective c':
        return 'objectivec icon'
    elif language in languages_with_css_icons:
        return language + " icon"
    return None

def load_history():
    '''Load the history of which entires we've already processed'''
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as history_file:
            content = history_file.read()
            if content != '':
                return json.loads(content)
    return []

def store_history(new_history):
    '''Store the history in the history file'''
    with open(HISTORY_FILE, 'w') as history_file:
        history_file.write(json.dumps(new_history, indent = 2))

def undone_entries(subreddit):
    '''Yield newest entries to `subreddit` until entry with id in history_file'''
    first_used = []
    already_used = load_history()
    for link in r.get_subreddit(subreddit).get_new_by_date(limit = None):
        if link.id in already_used:
            already_used = (first_used + 
                            already_used[:HISTORY_SIZE - len(first_used)])
            break
        if len(first_used) < HISTORY_SIZE:
            first_used.append(link.id)
        yield link
    else:
        already_used = first_used
    store_history(already_used)

def work_cycle(options):
    '''Set flair for every entry we haven't seen before'''
    log.debug("Started work cycle.")
    
    for entry in undone_entries(options.subreddit):
        # Create a human readable id for the post to use in our log
        # messages
        post_id = "\"%s\" (%s)" % (entry.title, entry.id)
        
        log.debug("Processing post %s." % post_id)
        
        # Ignore all submissions that already have flair
        if entry.link_flair_text and not options.blow_away:
            continue
          
        # Don't know how to parse code from this domain
        if not entry.domain in code_sites.keys():
            continue
        try:
            page = requests.get(entry.url)
        except requests.exceptions.RequestException, e:
            log.info("ERROR: Got an %s for %s. Skipping" % (type(e).__name__,
                                                            entry.title))
            continue
        if not page.ok:
            log.debug("Got a %d error when opening %s" % (page.status_code,
                                                          entry.url))
            continue
        language = re.search(code_sites[entry.domain], page.content, 
                   re.DOTALL | re.IGNORECASE)
        if language is None:
            log.info("Language could not be determined for post %s." % post_id)
            continue
        language = language.groups()[0].lower()
        shortname = make_shortname(language)
        log.debug("Determined language to be %s for post %s."
                    % (shortname, post_id))
        
        # Map the name to a flair template
        flair_icon = find_flair_icon(shortname)
        if not flair_icon:
            log.info("Determined language \"%s\" for post %s could not be "
                     "matched to any flair icon."
                         % (shortname, post_id))
            continue
            
        if not options.debug:
            i.set_flair(
                flair_text = shortname,
                flair_css_class = flair_icon
            )
            
        log.info("Set language of post %s to %s" % (post_id, shortname))
        log.debug("Full flair: Text=%s Icon=%s" % (shortname, flair_icon))
            
    log.debug("Work cycle finished.")

if __name__ == '__main__':
    options = parse_commandline_arguments()
    log = setup_logger()
    r = connect_to_reddit()
    if not options.debug:
        login_to_reddit()
        log.info("Succesfully logged in as user %s." % options.username)
    while True:
        work_cycle(options)
        sleep(options.refresh_speed)
    log.info("Exiting...")
