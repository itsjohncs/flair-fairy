## Parse Command Line Argument ##
import collections
import json
import logging # Needed for the logging command line argument default
import os
import praw
import re
import sys
import time
from optparse import OptionParser, make_option

import requests

import proxies
from settings import HISTORY_SIZE, code_sites, name_dict, flair_templates

option_list = [
    make_option("-u", "--username", dest = "username", type = str,
                help = "The username on reddit the bot will use to login."),
                
    make_option("-p", "--password", dest = "password", type = str,
                help = "The password on reddit the bot will use to login."),
                
    make_option("-r", "--reddit", dest = "subreddit", type = str,
                default = "badcode",
                help = "The name of the subreddit (eg: badcode) the bot "
                       "will work within."),
                       
    make_option("--refresh-speed", dest = "refresh_speed", type = float,
                default = 30.0,
                help = "The number of time in seconds the bot will wait "
                       "before performing more work."),
                       
    make_option("-q", "--quiet", dest = "quiet", default = False, 
                action = "store_true",
                help = "The bot will not explain all of its actions ad "
                       "nauseum."),
                       
    make_option("--map-file", dest = "map_file", default = "name_map.json",
                type = str,
                help = "The file containing the mapping from longname to "
                       "short for all the languages."),
                       
    make_option("--start-count", dest = "start_count", default = 100,
                type = int,
                help = "The maximum number of posts the fiary retrieves "
                       "out of the newest posts and processes."),
                       
    make_option("--debug", dest = "debug", default = False,
                action = "store_true",
                help = "The fairy will not make any changes, rather it "
                       "will only announce the changes it would make."),
                       
    make_option("-l", "--log-level", dest = "log_level", type = "int",
                default = logging.DEBUG, metavar = "LEVEL",
                help = "Only output log entries above LEVEL (default: "
                       "%default)"),
                       
    make_option("--config", dest = "config_path", type = "string",
                default = "config/", metavar = "PATH",
                help = "Search for config files in directory at PATH (default: "
                       "%default)"),

    make_option("--blow-away", dest = "blow_away", default = False,
                action = "store_true",
                help = "The fairy will not ignore posts that already have "
               "flair.")
]

parser = OptionParser(
    description = "Adds flair to posts linking to code snippets that "
                  "specify what language the snippet was written in.",
    option_list = option_list
)

log = logging.getLogger("flairfairy.languageflair")

# Run the parser
options = parser.parse_args()[0]

## Set up logging ##
if not options.quiet:
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(
        "[%(asctime)s] %(name)s.%(levelname)s: %(message)s"))
    topLog = logging.getLogger("flairfairy")
    topLog.setLevel(options.log_level)
    topLog.addHandler(sh)

log = logging.getLogger("flairfairy")

## Connect to reddit ##
r = praw.Reddit(
    user_agent = "bot:flair-fairy updates Flair for submissions after which" +
                 " programming language they contain. Owner by u/brownhead." +
                 " More info: github.com/brownhead/flair-fairy"
)

# Negative refresh_speed will cause a crash in time.sleep
if options.refresh_speed < 0:
    options.refresh_speed = 30

if not options.debug:
    try:
        r.login(options.username, options.password)
        subreddit = r.get_subreddit(options.subreddit)
        if r.user not in subreddit.get_moderators():
            print >> sys.stderr, "User not moderator of %s" % options.subreddit
            sys.exit(1)
    except reddit.errors.InvalidUserPass:
        print >> sys.stderr, "FATAL: Invalid user, password combination."
        sys.exit(1)
    
log.info("Succesfully logged in as user %s." % options.username)

def make_shortname(long_name):
    for regex, shortname in name_dict.iteritems():
        if re.match(regex, long_name, re.IGNORECASE) != None:
            return shortname
    return long_name

def find_template(language):
    for i in flair_templates:
        if i["name"] == language:
            return i
    return None

already_used = []

def undone_entries(subreddit):
    global already_used
    tmp_used = []
    for link in r.get_subreddit(subreddit).get_new_by_date(limit = None):
        if link.id in already_used:
            alread_used = tmp_used[-(HISTORY_SIZE-1):] + [alread_used[-1]]
            break
        tmp_used = tmp_used[-(HISTORY_SIZE-1):] + [link.id]
        yield link
    else:
        already_used = tmp_used

def run(options):
    log.debug("Started work cycle.")
    
    for i in undone_entries(options.subreddit):
        # Create a human readable id for the post to use in our log
        # messages
        post_id = "\"%s\" (%s)" % (i.title, i.id)
        
        log.debug("Processing post %s." % post_id)
        
        # Ignore all submissions that already have flair
        if i.link_flair_text and not options.blow_away:
            continue
          
        # Don't know how to parse code from this domain
        if not i.domain in code_sites.keys():
            continue
        page = requests.get(i.url)
        if not page.ok:
            log.debug("Got a %d error when opening %s" % (page.status_code,
                                                          i.url))
            continue
        language = re.search(code_sites[i.domain], page.content, 
                   re.DOTALL | re.IGNORECASE)
        if language is None:
            log.info("Language could not be determined for post %s."
                         % post_id)
            continue
        language = language.groups()[0].lower()
        shortname = make_shortname(language)
        
        log.debug("Determined language to be %s for post %s."
                     % (shortname, post_id))
        
        # Map the name to a flair template
        flair_template = find_template(shortname)
        if not flair_template:
            log.info("Determined language \"%s\" for post %s could not be "
                     "matched to any flair template."
                         % (shortname, post_id))
            continue
            
        # Set the flair if we're not in debug mode
        if not options.debug:
            i.set_flair(
                flair_text = flair_template["name"],
                flair_css_class = flair_template["css"]
            )
            
        log.info("Set language of post %s to %s" % (post_id, shortname))
        log.debug("Full flair: " + str(flair_template))
            
    log.debug("Work cycle finished.")

## Do it ##
while True:
    run(options)
    time.sleep(options.refresh_speed)

log.info("Exiting...")
