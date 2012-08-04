import logging 
import os
import re

import requests
from optparse import make_option

import proxies
from settings import code_sites, name_dict, flair_templates

log = logging.getLogger("flairfairy.languageflair")

class LanguageFlair:
    required_options = [
        make_option("--blow-away", dest = "blow_away", default = False,
            action = "store_true",
            help = "The fairy will not ignore posts that already have "
                   "flair.")
    ]
    
    def __init__(self, options, subreddits):
        self.flair_templates = flair_templates
        self.proxy = proxies.NewSubmissionsProxy(subreddits)
        self.name_dict = name_dict

    def shortname(self, long_name):
        for regex, shortname in self.name_dict.iteritems():
            if re.match(regex, long_name, re.IGNORECASE) != None:
                return shortname
        return long_name

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
            shortname = self.shortname(language)
            
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
