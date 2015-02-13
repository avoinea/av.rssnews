""" Abstract RSS Content
"""
from zope.interface import implements
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.ATContentTypes.content.newsitem import ATNewsItem
from av.rssnews.config import RSSNewsMessageFactory as _
from av.rssnews.interfaces import IRSSContent
from zope.container.interfaces import INameChooser

from Products.CMFPlone import PloneMessageFactory as _
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ImageWidget
from Products.ATContentTypes.configuration import zconf
from Products.validation import V_REQUIRED

from plone.app.blob.field import BlobField
from plone.app.blob.mixins import ImageFieldMixin
from plone.app.blob.interfaces import IBlobImageField

class ExtensionBlobField(BlobField, ImageFieldMixin):
    """ Image Field """
    implements(IBlobImageField)

SCHEMA = Schema((
    ExtensionBlobField('image',
        required = False,
        accessor = 'getImage',
        mutator = 'setImage',
        sizes = None,
        languageIndependent = True,
        storage = AnnotationStorage(migrate=True),
        swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
        pil_quality = zconf.pil_config.quality,
        pil_resize_algo = zconf.pil_config.resize_algo,
        original_size = None,
        max_size = zconf.ATImage.max_image_dimension,
        default_content_type = 'image/png',
        allowable_content_types = ('image/gif', 'image/jpeg', 'image/png'),
        validators = (('isNonEmptyFile', V_REQUIRED),
                      ('checkImageMaxSize', V_REQUIRED)),
        widget = ImageWidget(label = _(u'label_image', default=u'Image'),
                             description=_(u''),
                             show_content_type = False,
                             )
        ),
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
        title = self.Title()
        return INameChooser(self).chooseName(title)
