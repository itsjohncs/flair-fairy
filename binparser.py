"""
A module used for recognizing, accessing, and retrieving language data from
paste bins.

"""

import re, requests

class BaseParser:
    """
    Base class mainly for instructional purposes. Also in case we need it.
    All parsers should derive from BaseParser.
    
    """
    
    def __init__(self):
        self.page = None
        
        pass
    
    def check_match(self, url):
        raise NotImplemented()
        
    def load_page(self, url):
        request = requests.get(url)
        if request.status_code != requests.codes.ok:
            raise RuntimeError("Could not connect")
        
        self.page = request.text
        
    def retrieve_language(self):
        "Returns None if language could not be identified."
        
        raise NotImplemented()

class SimpleRegexParser(BaseParser):
    """
    Simple parser that checks a URL based on a regex and retrieves the language
    from a page based on a regex.
    
    """
    
    def __init__(self, url_regex, page_regex):
        """
        *url_regex* and *page_regex* should both be compiled RegexObjects, if
        they are strings they will be automatically compiled into RegexObjects
        with case sensitivity turned off.
        
        """

        if isinstance(url_regex, basestring):
            url_regex = re.compile(url_regex, re.IGNORECASE)
            
        if isinstance(page_regex, basestring):
            page_regex = re.compile(page_regex, re.IGNORECASE | re.DOTALL)
        
        self.url_regex = url_regex
        self.page_regex = page_regex
        
        BaseParser.__init__(self)
        
    def check_match(self, url):
        return self.url_regex.match(url) is not None
        
    def retrieve_language(self):
        if self.page is None:
            raise RuntimeError("load_page must be called before "
                               "retrieve_language.")
        
        match = self.page_regex.search(self.page)
        
        if match:
            return match.group("lang").strip()
        else:
            return None

###################################################
## Create new parsers above then add them below! ##
###################################################

parsers = (
    SimpleRegexParser(
        r"http://(www\.)?pastebin.com/",
        r"<head>.*<title>\[(?P<lang>.*?)\].*</title>.*</head>"
    ),
    SimpleRegexParser(
        r"http://(www\.)?codepad.org/",
        r"<head>.*<title>(?P<lang>.*?)code.*</title>.*</head>"
    ),
    SimpleRegexParser(
        r"https?://((www)|(gist)\.)?github.com/",
        r'<div class="data type-(?P<lang>[A-Za-z]*?)"'
    ),
    SimpleRegexParser(
        r"http://(www\.)?hatepaste.com/",
        r'<p class="lead lang"><a href=".*?">(?P<lang>.*?)</a>'
    )
)

def get_language(url):
    for i in parsers:
        if i.check_match(url):
            i.load_page(url)
            return i.retrieve_language()
            
    return None
