import sys, reddit, collections
        
def login(reddit, user, password = None):
    """
    Convenience function for *self.reddit.login()* that allows None to be
    passed in as the password signifying that the user should be prompted
    for it.
    
    """
    
    if not password:
        import getpass
        password = getpass.getpass("Password for /u/%s: " % user)
        
    # Will raise reddit.errors.InvalidUserPass if unsuccesful
    reddit.login(user, password)

class NewSubmissionsProxy:
    def __init__(self, reddit, subreddits, history_size = 100):
        self.reddit = reddit
        
        # Ensure that the list of subreddits is a list of some sort
        if isinstance(subreddits, basestring):
            self.subreddits = subreddits.split("+")
        else:
            self.subreddits = list(subreddits)
        
        # Will hold the ids of the recent submissions that have been processed
        self.processed = collections.deque()
    
    def get(self):
        for i in self.reddit.get_subreddit(self.subreddits).get_new_by_date(limit = None):
            # Stop if we've hit a submission that we've already processed
            if i.id in self.processed:
                raise StopIteration()
            
            # Note that we have processed this submission
            self.processed.insert(i.id)
            
            if len(self.processed) > history_size:
                self.processed.popleft()
                
            # Show it to the user
            yield i
            
    def get_state(self):
        import json
        
        state = {
            "subreddits": self.subreddits,
            "processed": self.processed
        }
        
        return json.dumps(state)
    
    def load_state(self, state):
        import json
        
        state = json.loads(state)
        
        self.subreddits = state["subreddits"]
        self.processed = state["processed"]
