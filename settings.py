code_sites = {
    'pastebin.com' : r"<head>.*?<title>\[(.*?)\].*?</title>.*?</head>",
    'codepad.org' : r"<head>.*?<title>(.*?) .*?</title>.*?</head>",
    'gist.github.com': r'<div class="data type-([A-Za-z]*?)"',
    'hatepase.com': r'<div class="data type-([A-Za-z]*?)"'
    }

name_dict = { 
	"c(\\+\\+)?$" : "c/c++",
	"(visual)?basic$" : "vb",
	"j(ava)? ?script$" : "js"
}

flair_templates = [{"name": "js", "css": "js icon"},
                   {"name": "c/c++", "css": "cpp icon"},
                   {"name": "vb", "css": "vb icon"},
                   {"name": "python", "css": "python icon"},
                   {"name": "php", "css": "php icon"},
                   {"name": "html", "css": "html icon"},
                   {"name": "css", "css": "css icon"},
                   {"name": "java", "css": "java icon"},
                   {"name": "c#", "css": "csharp icon"},
                   {"name": "asp/asp.net", "css": "asp icon"},
                   {"name": "ruby", "css": "ruby icon"},
                   {"name": "perl", "css": "perl icon"},
                   {"name": "sql", "css": "sql icon"},
                   {"name": "actionscript", "css": "actionscript icon"},
                   {"name": "objective c", "css": "objectivec icon"},
                   {"name": "lua", "css": "lua icon"},
                   {"name": "matlab", "css": "matlab icon"},
                   {"name": "lisp", "css": "lisp icon"}]
