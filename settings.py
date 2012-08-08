HISTORY_SIZE = 3
HISTORY_FILE = 'history.json'
LOG_FILE = 'flairlog.log'

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

languages_with_css_icons = ['js', 'vb', 'python', 'php', 'html', 'css', 'java',
                            'ruby', 'perl', 'sql', 'actionscript', 'lua',
                            'matlab', 'lisp']
