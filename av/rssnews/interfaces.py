""" RSS News public interfaces
"""
from zope.interface import Interface
from Products.ATContentTypes.interfaces import IATNewsItem

class IRSSContent(IATNewsItem):
    """ Marker interface for all RSS Content-Types
    """

class IRSSNewsItem(IRSSContent):
    """ Marker interface for RSS News Item
    """

class IRSSNews(IRSSContent):
    """ Marker interface for RSS News
    """

class IRSSServer(IRSSContent):
    """ Marker interface for RSS News Server
    """

class IImport(Interface):
    """ Import content from XML
    """
