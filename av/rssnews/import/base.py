""" XML Import adapter for BaseContent
"""
import base64
import logging
from zope.interface import implements
from zope.component import queryMultiAdapter
from av.rssnews.interfaces import IImport
from xml.etree.ElementTree import ElementTree, XMLTreeBuilder
from Products.CMFCore.utils import getToolByName
logger = logging.getLogger('av.rssnews')

class Import(object):
    """ Import BaseContent
    """
    implements(IImport)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def body(self):
        """ Getter
        """
        raise AttributeError('body')

    @body.setter
    def body(self, xml):
        """ Body importer
        """
        if isinstance(xml, (str, unicode)):
            parser = XMLTreeBuilder()
            parser.feed(xml)
            tree = parser.close()
            tree = ElementTree(tree)
            elem = tree.getroot()
        else:
            elem = xml

        if elem.tag != 'object':
            raise AttributeError('Invalid xml root element %s' % elem.tag)

        name = elem.get('name')
        if not name:
            raise AttributeError('No name provided for object')

        if hasattr(self.context, '__name__') and (
            name != self.context.__name__):
            raise AttributeError(('XML root object name %s '
                                  'should match context name %s') % (
                                      name, self.context.__name__))

        for child in elem.getchildren():
            if child.tag == 'property':
                self.attribute = child
            elif child.tag == 'object':
                self.child = child

        wftool = getToolByName(self.context, 'portal_workflow')
        state = wftool.getInfoFor(self.context, 'review_state', '(Unknown)')
        if state != 'published':
            try:
                wftool.doActionFor(self.context, 'publish',
                                   comment='Initial import')
            except Exception, err:
                logger.exception(err)
        self.context.reindexObject()

    @property
    def attribute(self):
        """ Attribute
        """
        raise AttributeError('attribute')

    @attribute.setter
    def attribute(self, element):
        """ Attribute importer
        """
        name = element.get('name')
        if not name:
            raise AttributeError('Missing name attribute for tag <property>')

        field = self.context.getField(name)
        if not field:
            return

        elements = element.getchildren()
        if elements:
            value = [item.text for item in elements]
        else:
            value = element.text

        if not value:
            return

        logger.debug('Set attribute %s: %s', name, value)
        field.getMutator(self.context)(value)

    @property
    def child(self):
        """ Child
        """
        raise AttributeError('child')

    @child.setter
    def child(self, element):
        """ Child importer
        """
        name = element.get('name')
        if not name:
            raise AttributeError('No name provided for object')

        if name not in self.context:
            factory = element.get('factory')
            if not factory:
                raise AttributeError('No factory provided for object %s' % name)

            logger.debug('Adding type %s: %s', factory, name)
            name = self.context.invokeFactory(factory, name)

        child = self.context[name]

        importer = queryMultiAdapter((child, self.request), IImport)
        if importer:
            importer.body = element

class ImportImage(Import):
    """ Image import
    """
    @property
    def attribute(self):
        """ Attribute
        """
        raise AttributeError('attribute')

    @attribute.setter
    def attribute(self, element):
        """ Attribute setter
        """
        if not element.text:
            return

        field = self.context.getField('image')
        if not field:
            return

        name = element.get('name')
        if name == 'data':
            text = element.text
            text = text.replace('<![CDATA[', '', 1)
            text.strip(']]>')
            text = base64.decodestring(text)
            field.getMutator(self.context)(text)
