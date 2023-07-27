import urllib.parse

def escape(text:str) -> str:
    '''Escapes text to use for searching'''
    return urllib.parse.quote(text, safe='')