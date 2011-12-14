""" News
"""
from zope.interface import implements
from Products.ATContentTypes.content.base import registerATCT
from av.rssnews.config import PROJECTNAME
from av.rssnews.interfaces import IRSSServer
from av.rssnews.content.core import SCHEMA
from Products.ATContentTypes.content.folder import ATFolder

class RSSServer(ATFolder):
    """ Add URL to ATFolder
    """
    implements(IRSSServer)
    schema = ATFolder.schema.copy() + SCHEMA.copy()
    meta_type = portal_type = archetype_name = 'RSSServer'

def register():
    """ Register custom content-type
    """
    registerATCT(RSSServer, PROJECTNAME)
