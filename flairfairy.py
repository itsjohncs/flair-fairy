## Parse Command Line Argument ##
import logging # Needed for the logging command line argument default
import reddit
import sys
import time
from optparse import OptionParser, make_option

from app.routines import *

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
                       "%default)")
]

option_list += RoutinesRunner.get_options()

parser = OptionParser(
    description = "Adds flair to posts linking to code snippets that "
                  "specify what language the snippet was written in.",
    option_list = option_list
)

# Run the parser
options = parser.parse_args()[0]

# Ensure all required options are present
if not (options.username and options.subreddit):
    parser.error("Username and subreddit required.")
    
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
r = reddit.Reddit(
    user_agent = "bot:flair-fairy target:/r/badcode owner:brownhead"
)

# Negative refresh_speed will cause a crash in time.sleep
if options.refresh_speed < 0:
    options.refresh_speed = 30

# Prompt the user for the password if one wasn't specified on the command line
if not options.password:
    import getpass
    options.password = getpass.getpass("Password for user %s: " % options.username)
    
# Will raise reddit.errors.InvalidUserPass if unsuccesful
try:
    r.login(options.username, options.password)
except reddit.errors.InvalidUserPass:
    print >> sys.stderr, "FATAL: Invalid user, password combination."
    
    sys.exit(1)
    
log.info("Succesfully logged in as user %s." % options.username)

## Do it ##
runner = RoutinesRunner(options)
while True:
    runner.run(r, options)
    time.sleep(options.refresh_speed)

log.info("Exiting...")
