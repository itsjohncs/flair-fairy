## Parse Command Line Argument ##
from optparse import OptionParser, make_option
import logging # Needed for the logging command line argument default

option_list = [
    make_option("-u", "--username", dest = "username", type = str,
                help = "The username on reddit the bot will use to login."),
                
    make_option("-p", "--password", dest = "password", type = str,
                help = "The password on reddit the bot will use to login."),
                
    make_option("-r", "--reddit", dest = "subreddit", type = str,
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
                       
    make_option("--blow-away", dest = "blow_away", default = False,
                action = "store_true",
                help = "The fairy will not ignore posts tha already have "
                       "flair."),
                       
    make_option("-l", "--log-level", dest = "logLevel", type = "int",
                default = logging.DEBUG, metavar = "LEVEL",
                help = "Only output log entries above LEVEL (default: "
                       "%default)")
]

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
    topLog.setLevel(options.logLevel)
    topLog.addHandler(sh)

log = logging.getLogger("flairfairy")

## Connect to reddit ##
import reddit, sys

r = reddit.Reddit(
    user_agent = "bot:flair-fairy target:/r/badcode owner:brownhead"
)

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

log.info("Exiting...")

# Set it up so if SIGINT is encountered we exit gracefully. Logic for this is
# that if a SIGINT occurs in the middle of the bot doing something important
# a redditors day might be ruined. Downside is if the bot goes haywire it's
# harder to stop. Upside is if your like the rest of the world you run something
# akin to screen and can kill it forcibly easily.
#exiting = False
#def _setExit(a, b):
#    global exiting
#    
#    print "Exiting soon..."
#    exiting = True
    
#signal.signal(signal.SIGINT, _setExit)

#def wait(seconds):
    #"""
    #Waits a given amount of seconds (floating numbers OK) and then returns True.
    #If exiting is True when the function begins or a SIGINT is encountered
    #during waiting, False is returned.
    
    #"""
    
    ## Sleep if were not exiting yet
    #if not exiting:
        #time.sleep(seconds)
        
    ## Return True iff were not exiting
    #return not exiting

### Prepwork Done. Let's Reddit! ##
#import reddit, requests, re, shortnames, binparser, socket

#options = None

## Begin work cycle.... Now!
#def run(subreddit):
    ## Prepare the language mapper
    #name_mapper = shortnames.ShortNameMapper(open(options.map_file))
    
    #log("Beginning work cycle...")
    
    #try:
        ## Grab the posts we will scan through
        #if not run.last_checked:
            ## 100 new posts should account for small amounts of bot downtime
            #submissions = list(subreddit.get_new_by_date(limit = 100))
        #else:
            #submissions = list(subreddit.get_new_by_date(
                #limit = None, 
                #place_holder = run.last_checked
            #))[1:] # Skip the place_holder
    #except socket.timeout:
        #log("Could not retrieve a list of submissions!")
    
    ## Mark the first submission as our last checked as it is the most recent.
    ## That way when we grab more submissions in the next cycle we'll grab
    ## everything more recent that it.
    #if submissions:
        #run.last_checked = submissions[0].id

    #for i in submissions:
        ## If flair has already been added skip this submission
        #if i.link_flair_text and not options.blow_away:
            #continue
        
        #try:
            #language = binparser.get_language(i.url)
        #except RuntimeError:
            ## Broken link
            #continue
        
        #if language is None:
            #continue
        
        #shortname = name_mapper.map_name(language).lower()
        
        #if options.debug:
            #print "Would set post '%s' to be language '%s'." \
                      #% (i.title, shortname)
        #else:
            #log("Setting post '%s' to language '%s'" % (i.title, shortname))
            
            #i.set_flair(shortname)
            
            ## Sleep for a bit so that we don't make reddit mad at us
            #time.sleep(4)
            
    #log("Ending work cycle.")
    
#run.last_checked = None
