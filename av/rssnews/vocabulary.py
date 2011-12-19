""" Vocabularies
"""
import operator
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

class ServersVocabulary(object):
    """ Servers vocabulary
    """
    implements(IVocabularyFactory)

    def __call__(self, context=None):
        ctool = getToolByName(context, 'portal_catalog')
        brains = ctool(object_provides='av.rssnews.interfaces.IRSSServer')
        items = ((brain.getURL(1), brain.Title) for brain in brains)
        items = sorted(items, key=operator.itemgetter(1))
        return SimpleVocabulary([
            SimpleTerm(item[0], item[0], item[1]) for item in items])
