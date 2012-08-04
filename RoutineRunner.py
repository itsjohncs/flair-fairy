import languageflair

class RoutinesRunner:
    routines_classes = [languageflair.LanguageFlair]
    
    def __init__(self, options):
        self.routines = [
            languageflair.LanguageFlair(options, options.subreddit)
        ]
        
    def run(self, reddit, options):
        for i in self.routines:
            i.run(reddit, options)
