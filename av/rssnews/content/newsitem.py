""" News item
"""
from zope.interface import implements
from Products.ATContentTypes.content.base import registerATCT

from av.rssnews.config import PROJECTNAME
from av.rssnews.content.core import RSSContent
from av.rssnews.interfaces import IRSSNewsItem

class RSSNewsItem(RSSContent):
    """ Add URL to News Item
    """
    implements(IRSSNewsItem)
    schema = RSSContent.schema.copy()
    meta_type = portal_type = archetype_name = 'RSSNewsItem'

def register():
    """ Register custom content-type
    """
    registerATCT(RSSNewsItem, PROJECTNAME)
