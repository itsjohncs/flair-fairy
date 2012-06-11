import collections

class NewSubmissionsProxy:
    def __init__(self, subreddits, reddit = None, history_size = 100):
        self.reddit = reddit
        
        # Ensure that the list of subreddits is a list of some sort
        if isinstance(subreddits, basestring):
            self.subreddits = subreddits.split("+")
        else:
            self.subreddits = list(subreddits)
        
        # Will hold the ids of the recent submissions that have been processed
        self.processed = collections.deque()
        
        self.history_size = history_size
    
    def get(self, reddit = None):
        if not reddit:
            reddit = self.reddit
        
        for i in reddit.get_subreddit("+".join(self.subreddits)).get_new_by_date(limit = None):
            # Stop if we've hit a submission that we've already processed
            if i.id in self.processed:
                raise StopIteration()
            
            # Note that we have processed this submission
            self.processed.append(i.id)
            
            if len(self.processed) > self.history_size:
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
