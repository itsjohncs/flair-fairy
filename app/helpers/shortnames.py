"""
A module used to map longer programming language names to simpler, more
recognizable/reddit-friendly ones.

"""

import re

class ShortNameMapper:
    class _NameMapping:
        def __init__(self, shortname, regexs, ignorecase):
            self.regexs = [re.compile(i, re.IGNORECASE if ignorecase else 0)
                              for i in regexs]
                              
            self.shortname = shortname
            
        def check_match(self, longname):
            for i in self.regexs:
                if i.search(longname):
                    return True
                    
            return False
    
    def __init__(self, file = None, ignorecase = True):
        """
        Will automatically call import_map if *file* is specified.
        
        If *ignorecase* is True all regular expressions will disregard case when
        matching.
        
        """
        
        # Do not modify after initialization! Will not have desired effect.
        self.__ignorecase = ignorecase
        
        self._name_maps = []
        
        if file:
            self.import_map(file)

    def import_map(self, file):
        """
        Imports a JSON file containing mapping info in the format:
        
            [
                ["visual ?basic", "vbasic", "vb"],
                ["c\\+\\+", "cpp"],
                ...
                ...
            ]
            
        The last element of each array is the shortname for the language and all
        other entries are regular expressions that match the longversion of the
        name.
        
        Note the expressions will be checked IN ORDER.
        
        """
        
        import json
        
        # Load the JSON file
        raw = json.load(file)
        
        for i in raw:
            if len(i) <= 1:
                raise RuntimeError("Badly formed mapping info.")
            
            # Grab the shortname from the end of the list
            shortname = i.pop()
            
            # Create a new name mapping and add it to the list
            self._name_maps.append(
                self._NameMapping(shortname, i, self.__ignorecase)
            )
            
    def check_match(self, longname):
        """
        Returns true iff a shortname is associated with that longname.
        
        Use map_name() to get the actual name
        
        """
        
        for i in self._name_maps:
            if i.check_match(longname):
                return True
                
        return False
    
    def map_name(self, longname):
        """
        Returns *longname* mapped to its corresponding shortname, or returns
        *longname* if no shortname was found.
        
        """
    
        for i in self._name_maps:
            if i.check_match(longname):
                return i.shortname
                
        return longname
