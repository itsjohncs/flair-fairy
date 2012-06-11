import logging, json, os
from app.helpers import *
from optparse import make_option

log = logging.getLogger("flairfairy.languageflair")

class LanguageFlair:
    required_options = [
        make_option("--blow-away", dest = "blow_away", default = False,
            action = "store_true",
            help = "The fairy will not ignore posts tha already have "
                   "flair.")
    ]
    
    def __init__(self, options, subreddits):
        try:
            self.name_mapper = shortnames.ShortNameMapper(
                open(os.path.join(options.config_path, "name_map.json"))
            )
        except IOError:
            log.warn("Could not open name_map.json.")
            
            self.name_mapper = None
            
        try:
            self.flair_templates = \
                json.load(open(os.path.join(options.config_path, "flair_templates.json")))
        except IOError:
            log.crtitical("Could not open flair_templates.json.")
            
            raise
        
        self.proxy = proxies.NewSubmissionsProxy(subreddits)
    
    def find_template(self, language):
        for i in self.flair_templates:
            if i["name"] == language:
                return i
                
        return None
    
    def run(self, reddit, options):
        log.debug("Started work cycle.")
        
        for i in self.proxy.get(reddit):
            # Create a human readable id for the post to use in our log
            # messages
            post_id = "\"%s\" (%s)" % (i.title, i.id)
            
            log.debug("Processing post %s." % post_id)
            
            # Ignore all submissions that already have flair
            if i.link_flair_text and not options.blow_away:
                continue
                
            try:
                language = binparser.get_language(i.url)
            except ConnectionFailure:
                log.info("Possible broken link detected for post %s." % post_id)
                
                # Broken link or website, just skip it
                continue
                
            if language is None:
                log.info("Language could not be determined for post %s."
                             % post_id)
                             
                continue
            
            # The language should always be lowercase
            language = language.lower()
            
            # Determine the short name for this language if possible
            if self.name_mapper:
                shortname = self.name_mapper.map_name(language)
            else:
                shortname = language
            
            log.debug("Determined language to be %s for post %s."
                         % (shortname, post_id))
            
            # Map the name to a flair template
            flair_template = self.find_template(shortname)
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
