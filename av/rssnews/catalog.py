""" Catalog indexes
"""
from zope.interface import Interface
from plone.indexer.decorator import indexer
from av.rssnews.interfaces import IRSSNewsItem, IRSSServer
from Products.CMFPlone.utils import parent

@indexer(IRSSNewsItem)
def sourceTitle(obj, **kwargs):
    """ Get source for catalog index """
    if not IRSSNewsItem.providedBy(obj):
        raise AttributeError

    found = False
    myparent = parent(obj)
    for back in range(0, 5):
        if IRSSServer.providedBy(myparent):
            found = True
            break
        myparent = parent(myparent)

    if not found:
        raise AttributeError

    return myparent.title_or_id()

@indexer(IRSSNewsItem)
def sourcePath(obj, **kwargs):
    """ Get source path for catalog index """
    if not IRSSNewsItem.providedBy(obj):
        raise AttributeError

    found = False
    myparent = parent(obj)
    for back in range(0, 5):
        if IRSSServer.providedBy(myparent):
            found = True
            break
        myparent = parent(myparent)

    if not found:
        raise AttributeError

    return myparent.getPhysicalPath()
