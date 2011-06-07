""" News
"""
from zope.interface import implements
from Products.ATContentTypes.content.base import registerATCT
from av.rssnews.config import PROJECTNAME
from av.rssnews.interfaces import IRSSNews
from av.rssnews.content.core import RSSContent

class RSSNews(RSSContent):
    """ Add URL to News Item
    """
    implements(IRSSNews)
    schema = RSSContent.schema.copy()
    meta_type = portal_type = archetype_name = 'RSSNews'

def register():
    """ Register custom content-type
    """
    registerATCT(RSSNews, PROJECTNAME)
