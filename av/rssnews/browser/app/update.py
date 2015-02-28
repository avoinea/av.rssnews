""" Update cron
"""
#import time
import re
import logging
import urllib2
import feedparser
import time
from datetime import datetime
from datetime import timedelta
import transaction
from DateTime import DateTime
from StringIO import StringIO
from PIL import Image as PILImage
from zope.interface import alsoProvides
from zope.component import queryMultiAdapter, getUtility
from zope.container.interfaces import INameChooser
from zope.datetime import parseDatetimetz
from BeautifulSoup import BeautifulSoup
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.breadcrumbs import IHideFromBreadcrumbs
from Products.CMFPlone.utils import parent
from av.rssnews.config import bucharest
from av.rssnews.utilities.interfaces import IText


logger = logging.getLogger('av.rssnews')

class Update(BrowserView):
    """ News updater """
    def __init__(self, context, request):
        super(Update, self).__init__(context, request)
        self.exists = set()

    def get_aspect_ratio(self, img, width=400, height=300):
        """ Return proportional dimensions within desired size """
        sw = float(width) / img.size[0]
        sh = float(height) / img.size[1]
        if sw <= sh:
            height = int(sw * img.size[1] + 0.5)
        else:
            width = int(sh * img.size[0] + 0.5)
        return width, height

    def resize(self, img):
        """ Resize image
        """
        width, height = self.get_aspect_ratio(img)
        try:
            img = img.resize((width, height), PILImage.ANTIALIAS)
        except AttributeError:
            img = img.resize((width, height))
        except Exception, err:
            logger.exception(err)
            return None
        return img

    def add_image_from_enclosures(self, container, enclosures):
        """ Add image from enclosures
        """
        for enclosure in enclosures:
            enc_type = enclosure.get('type', '')
            if 'image' not in enc_type:
                continue
            enc_href = enclosure.get('href', '')
            if not enc_href:
                continue

            enc_href = enc_href.split('?')[0]
            #enc_id = enc_href.split('/')[-1]
            try:
                conn = urllib2.urlopen(enc_href)
                data = conn.read()
            except Exception, err:
                logger.exception(err)
                continue
            if data:
                img = PILImage.open(StringIO(data))
                # Skip low resolution images
                try:
                    if (img.size[0] < 350 or img.size[1] < 250):
                        return None
                except Exception, err:
                    logger.exception(err)

                fmt = img.format
                img = self.resize(img)
                if img:
                    newimg = StringIO()
                    img.save(newimg, fmt, quality=85)
                    newimg.seek(0)
                    data = newimg.read()
                container.getField('image').getMutator(container)(data)
            return container
        return None

    def add_image_from_summary(self, container, summary):
        """ Add image from summary
        """
        summary = summary.replace('\n', ' ')
        pattern = re.compile(r'\<img.*src=\"(?P<imagelink>.+?)\"')
        found = pattern.search(summary)
        if not found:
            return None
        image_link = found.group('imagelink')
        image_link = image_link.split('?')[0]
        #image_path = image_link.split('/')
        #image_id = image_path[-1] or image_path[-2]

        # Adds
        if image_link.startswith('http://core.ad20.net'):
            return None

        # Sport.ro
        if image_link.endswith('thumb_size3.jpg'):
            image_link = image_link.replace(
                'thumb_size3.jpg', 'thumb_size1.jpg')
        if image_link.endswith('size3.jpg'):
            image_link = image_link.replace('size3.jpg', 'size1.jpg')

        # doctorulzilei
        if image_link.endswith('-170x100.jpg'):
            image_link = image_link.replace('-170x100.jpg', '.jpg')

        try:
            conn = urllib2.urlopen(image_link)
        except urllib2.HTTPError, err:
            logger.exception('Image url: %s; Error: %s', image_link, err)
            return None
        data = conn.read()
        if data:
            img = PILImage.open(StringIO(data))

            # Skip low resolution images
            try:
                if (img.size[0] < 350 or img.size[1] < 250):
                    return None
            except Exception, err:
                logger.exception(err)

            fmt = img.format
            img = self.resize(img)
            if img:
                newimg = StringIO()
                img.save(newimg, fmt, quality=85)
                newimg.seek(0)
                data = newimg.read()
            container.getField('image').getMutator(container)(data)
            return container
        return None

    def add_image(self, container, entry):
        """ Try to add image in container
        """
        # Get image from enclosure
        enclosures = entry.get('enclosures', [])
        image = self.add_image_from_enclosures(container, enclosures)
        if image:
            return image

        # Get image from description
        summary = entry.get('summary', '')
        image = self.add_image_from_summary(container, summary)
        if image:
            return image

        return None

    def add_newsitem(self, entry):
        """ Add news item
        """
        title = entry.get('title', '')
        title = title.replace('&nbsp;', ' ').strip()

        description = BeautifulSoup(entry.get('summary', ''))
        description = ''.join([e for e in description.recursiveChildGenerator()
                        if isinstance(e, unicode)]).strip()

        ptool = getToolByName(self.context, 'portal_properties')
        sanitize = getattr(ptool, 'sanitize', None)
        if sanitize:
            title_sanitize = sanitize.getProperty('subject', [])
            for expr in title_sanitize:
                title = title.replace(expr, '')
            desc_sanitize = sanitize.getProperty('body', [])
            for expr in desc_sanitize:
                description = description.replace(expr, '')

        body = description

        utils = getUtility(IText)
        description = utils.truncate(description, 20, 200)

        if not (title and description):
            return None

        url = entry.get('link', '#').strip()

        updated = entry.get('updated', None)
        if not updated:
            updated = datetime.now(bucharest)
        else:
            try:
                updated = parseDatetimetz(updated)
            except SyntaxError:
                updated = parseDatetimetz(updated.replace(' ', 'T', 1))
            except:
                updated = datetime.now(bucharest)

            # Skip news older than 30 days
            plone_ro = 'plone.ro' in url
            if not plone_ro:
                try:
                    if updated < (datetime.now() - timedelta(10)):
                        return None
                except TypeError:
                    if updated < (datetime.now(bucharest) - timedelta(10)):
                        return None
                except Exception, err:
                    logger.exception(err)

        # Add archive
        archive = updated.strftime('%Y-%m-%d')
        archive = self.add(self.context, 'Folder', archive)
        alsoProvides(archive, IHideFromBreadcrumbs)
        if not IHideFromBreadcrumbs.providedBy(self.context):
            alsoProvides(self.context, IHideFromBreadcrumbs)
        self.publish(archive)

        # News item already added, skip it
        name = INameChooser(self.context).chooseName(title)

        # Skip duplicate
        if name in self.exists:
            return None

        self.exists.add(name)
        if name in archive.objectIds():
            return archive._getOb(name)

        # Add new item
        newsitem = self.add(archive, 'RSSNewsItem', name)

        # Update news properties
        newsitem.getField('title').getMutator(newsitem)(title)
        newsitem.getField('description').getMutator(newsitem)(description)
        newsitem.getField('text').getMutator(newsitem)(body)
        newsitem.getField('url').getMutator(newsitem)(url)
        newsitem.getField('effectiveDate').getMutator(newsitem)(updated)
        subject = [self.context.title_or_id()]
        try:
            if u'black friday' in title.lower() or u'black friday' in description.lower():
                subject.append('Black Friday')
        except Exception, err:
            logger.exception(err)
        newsitem.getField('subject').getMutator(newsitem)(subject)

        self.add_image(newsitem, entry)

        # Publish
        self.publish(newsitem)

        # Reindex
        newsitem.reindexObject()
        return newsitem

    def add(self, context, factory, name):
        """ Invoke factory
        """
        if not name in context.objectIds():
            logger.info('Adding %s: %s/%s', factory,
                        context.absolute_url(1), name)
            name = context.invokeFactory(factory, name)
        return context._getOb(name)

    def publish(self, doc):
        """ Publish doc
        """
        wftool = getToolByName(self.context, 'portal_workflow')
        state = wftool.getInfoFor(doc, 'review_state', '(Unknown)')
        if state != 'published':
            try:
                wftool.doActionFor(doc, 'publish', comment='')
            except Exception, err:
                logger.debug(err)

    def __call__(self, **kwargs):
        """ Run updater
        """
        self.exists = kwargs.get('exists', set())
        ufield = self.context.getField('url')
        if not ufield:
            return
        url = ufield.getAccessor(self.context)()

        etag = None
        efield = self.context.getField('etag')
        if efield:
            etag = efield.getAccessor(self.context)()

        data = feedparser.parse(url, etag=etag)

        # No change
        if data.get('status', None) == 304:
            return "No changes made since last update"

        etag = data.get('etag', None)
        if etag and efield:
            efield.getMutator(self.context)(etag)

        for entry in data.get('entries', ()):
            self.add_newsitem(entry)

        return '%s - UPDATED' % self.context.absolute_url(1)

class PortalUpdate(BrowserView):
    """ Call all updaters
    """
    def __init__(self, context, request):
        super(PortalUpdate, self).__init__(context, request)
        self.exists = set()

    def __call__(self, **kwargs):
        ctool = getToolByName(self.context, 'portal_catalog')
        brains = ctool(object_provides='av.rssnews.interfaces.IRSSNews')

        start = time.time()
        logger.info('Updating %s news sources...', len(brains))
        for brain in brains:
            doc = brain.getObject()
            updater = queryMultiAdapter((doc, self.request), name=u'update')
            if not updater:
                continue

            try:
                res = updater(exists=self.exists)
            except Exception, err:
                logger.exception(err)
                continue
            else:
                logger.info(res)
                transaction.savepoint(optimistic=True)

        logger.info('Update complete in %s seconds !', time.time() - start)

class PortalCleanup(BrowserView):
    """ Cleanup old news
    """
    def __call__(self, **kwargs):
        if getattr(self.request, 'form', {}):
            kwargs.update(self.request.form)

        days = kwargs.get('days', 10)
        try:
            days = int(days)
        except Exception, err:
            logger.exception(err)
            days = 10
        days = max(days, 10)

        ctool = getToolByName(self.context, 'portal_catalog')
        brains = ctool(
            effective={'query': DateTime() - days, 'range': 'max'},
            object_provides='av.rssnews.interfaces.IRSSNewsItem')

        index = 0
        total = len(brains)
        logger.info('Deleting old news: 0/%s', total)
        for index, brain in enumerate(brains):
            try:
                obj = brain.getObject()
                obj_parent = parent(obj)
                obj_parent.manage_delObjects([brain.getId])
            except Exception, err:
                logger.exception(err)
                continue
            else:
                if (index+1) % 500 == 0:
                    logger.info('Deleting old news: %s/%s', index+1, total)
                    transaction.commit()

        logger.info('Deleting old news: %s/%s', total, total)
        transaction.commit()

        brains = ctool(portal_type='Folder')
        total = len(brains)
        logger.info('Deleting empty folders: 0/%s', total)
        for index, brain in enumerate(brains):
            try:
                name = brain.getId
                obj = brain.getObject()
                if obj.objectIds():
                    continue
                # 2013-01-01 - Avoid deletion of empty faceted folders
                elif not name.startswith('201'):
                    continue
                obj_parent = parent(obj)
                obj_parent.manage_delObjects([name])
            except Exception, err:
                logger.exception(err)
                continue
            else:
                if (index+1) % 500 == 0:
                    logger.info('Deleting empty folders %s/%s', index+1, total)
                    transaction.commit()
        logger.info('Deleting empty folders: %s/%s', index, total)

        return 'Deleted old news and empty folders'
