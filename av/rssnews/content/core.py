""" Abstract RSS Content
"""
from zope.interface import implements
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.ATContentTypes.content.newsitem import ATNewsItem
from av.rssnews.config import RSSNewsMessageFactory as _
from av.rssnews.interfaces import IRSSContent
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

class RSSContent(ATNewsItem):
    """ RSS Content should subclass this
    """
    implements(IRSSContent)
    schema = ATNewsItem.schema.copy() + SCHEMA.copy()

    def generateNewId(self):
        """ Customize new id
        """
        oid = super(RSSContent, self).generateNewId()
        news_id = oid.split('-')
        if len(news_id) <= (RSS_MAXID + (0.20 * RSS_MAXID)): # 20%
            return oid
        return '-'.join(news_id[:RSS_MAXID])
