"""Common configuration constants
"""

PROJECTNAME = 'av.rssnews'

ADD_PERMISSIONS = {
    'RSSNewsItem': 'av.rssnews: Add RSS News Item'
}

from zope.i18nmessageid import MessageFactory
RSSNewsMessageFactory = MessageFactory('av.rssnews')

RSS_MAXID = 5
