""" News item
"""
from zope.interface import implements
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.ATContentTypes.content.base import registerATCT

from av.rssnews.config import RSSNewsMessageFactory as _
from av.rssnews.config import PROJECTNAME
from av.rssnews.interfaces import IRSSNewsItem
from av.rssnews.config import RSS_MAXID

SCHEMA = Schema((
    StringField(
        'url',
        schemata='default',
        widget=StringWidget(
            description="",
            label=_(u'label_news_url', default=u'URL')
        )
    ),
))

class RSSNewsItem(ATNewsItem):
    """ Add URL to News Item
    """
    implements(IRSSNewsItem)

    schema = ATNewsItem.schema.copy() + SCHEMA
    meta_type = portal_type = archetype_name = 'RSSNewsItem'

    def generateNewId(self):
        """ Customize new id
        """
        oid = super(RSSNewsItem, self).generateNewId()
        news_id = oid.split('-')
        if len(news_id) <= (RSS_MAXID + (0.20 * RSS_MAXID)): # 20%
            return oid
        return '-'.join(news_id[:RSS_MAXID])

def register():
    """ Register custom content-type
    """
    registerATCT(RSSNewsItem, PROJECTNAME)
