import sys, reddit, shelve

class BaseBot(object):
    def __init__(self, user_agent, shelve, **kwargs):
        self.reddit = reddit.Reddit(user_agent = user_agent)
        
        self.shelve = shelve
            
        super(RedditBot, self).__init__(self, **kwargs)
        
    def login(self, user, password = None):
        """
        Convenience function for *self.reddit.login()* that allows None to be
        passed in as the password signifying that the user should be prompted
        for it.
        
        """
        
        if not password:
            import getpass
            password = getpass.getpass("Password for /u/%s:" % user)
            
        # Will raise reddit.errors.InvalidUserPass if unsuccesful
        self.reddit.login(user, password)
        
        self.user = user
        
    # Each of the derived bots will call super()._run() at the end of their own
    # _run() functions, this makes sure none of them reach object and raise
    # a type-error
    def _run(self):
        assert not hasattr(super(RedditBot, self), "_run")
        
class WatcherBot(BaseBot):
    class _SubredditInfo:
        def __init__(self, reddit, subreddit_name):
            self.name = name
            self.subreddit = reddit.get_subreddit(name)
            
        def __eq__(self, other):
            return self.name == other.name
                
    def __init__(self, target_subreddits = [], retroactive = 20, **kwargs):
        # Save the subreddits were targeting
        self._monitored_subreddits = \
            [MonitorBot._SubredditInfo(i) for i in target_subreddits]
        
        # If no cached "last submission checked" is found, this many submissions
        # are pulled from each of the subreddits. None signifies ALL the
        # submissions in ALL the subreddits will be pulled in that case.
        self._retroactive = retroactive
        
        super().__init__(self, **kwargs)
        
    def monitor_subreddit(self, name):
        self._monitored_subreddits.append(_SubredditInfo(name))
        
    def ignore_subreddit(self, name):
        try:
            self._monitored_subreddits.remove(_SubredditInfo(name))
        except ValueError:
            pass
            
    def get_subreddits(self):
        return (i.name for i in _monitored_subreddits)

    def _get_new_submissions(self, subreddit, last_checked = None):
        """
        Returns a generator that retrieves new submissions from the given
        subreddit newer than the last_checked element.
        
        Takes into account the *retroactive* attribute if last_checked is not
        provided.
        
        """
        
        if last_checked:
            # TODO: Place holder may be included here... check
            return subreddit.get_new_by_date(
                limit = None,
                place_holder = last_checked
            )
        else:
            return subreddit.get_new_by_date(limit = self._retroactive)

    def _run(self):
        # Go through each of the subreddits...
        for i in self._subreddits:
            # and get each one's new submissions.
            for submission in _get_new_submissions(i.subreddit):
                super().on_new_submission(submission)
                
        super(WatcherBot, self)._run()

    def run(self):
        _run()
