import markdown
from markupsafe import Markup

def markdown_filter(text):
    if not text:
        return ''
    html = markdown.markdown(text, extensions=['extra', 'codehilite'])
    return Markup(html)