"""Common configuration constants
"""

PROJECTNAME = 'av.rssnews'

ADD_PERMISSIONS = {
    'RSSNewsItem': 'av.rssnews: Add RSS News Item',
    'RSSNews': 'av.rssnews: Add RSS News',
    'RSSServer': 'av.rssnews: Add RSS Server',
}

from zope.i18nmessageid import MessageFactory
RSSNewsMessageFactory = MessageFactory('av.rssnews')

RSS_MAXID = 5

from pytz import timezone
from pytz import UTC as utc
bucharest = timezone('Europe/Bucharest')
