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

    @staticmethod
    def get_options():
        options_list = []
        for i in RoutinesRunner.routines_classes:
            if hasattr(i, "required_options"):
                options_list += i.required_options
                
        return options_list
