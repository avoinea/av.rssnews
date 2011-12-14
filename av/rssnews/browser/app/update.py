""" Update cron
"""
#import time
import re
import logging
import urllib2
import feedparser
from datetime import datetime
from zope.app.container.interfaces import INameChooser
from zope.datetime import parseDatetimetz
from av.rssnews.config import bucharest
from BeautifulSoup import BeautifulSoup
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('av.rssnews')

class Update(BrowserView):
    """ News updater """

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
            enc_id = enc_href.split('/')[-1]
            try:
                conn = urllib2.urlopen(enc_href)
                data = conn.read()
            except Exception, err:
                logger.exception(err)
                continue
            if data:
                logger.info('Add image %s in %s',
                             enc_id, container.absolute_url(1))

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
        image_path = image_link.split('/')
        image_id = image_path[-1] or image_path[-2]

        # Adds
        if image_link.startswith('http://core.ad20.net'):
            return None

        # Sport.ro
        if image_link.endswith('thumb_size3.jpg'):
            image_link = image_link.replace(
                'thumb_size3.jpg', 'thumb_size1.jpg')
        if image_link.endswith('size3.jpg'):
            image_link = image_link.replace('size3.jpg', 'size1.jpg')
        try:
            conn = urllib2.urlopen(image_link)
        except urllib2.HTTPError, err:
            logger.exception('Image url: %s; Error: %s', image_link, err)
            return None
        data = conn.read()
        if data:
            logger.info('Add image %s in %s',
                         image_id, container.absolute_url(1))
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
                               if isinstance(e,unicode)]).strip()

        # Descopera.ro
        index = description.find('Citeste tot articolul')
        if index != -1:
            description = description[:index]

        if not (title and description):
            return None

        url = entry.get('link', '#').strip()

        # News item already added, skip it
        name = INameChooser(self.context).chooseName(title)
        if name in self.context.objectIds():
            return self.context._getOb(name)

        # Add new item
        name = self.context.invokeFactory('RSSNewsItem', name)
        logger.info('Adding newsitem %s in %s',
                    name, self.context.absolute_url(1))

        updated = entry.get('updated', None)
        if not updated:
            updated = self.context.updated or datetime.now(bucharest)
        else:
            updated = parseDatetimetz(updated)

        print "======="
        print name
        print updated

        # Update news properties
        newsitem = self.context._getOb(name)
        newsitem.getField('title').getMutator(newsitem)(title)
        newsitem.getField('description').getMutator(newsitem)(description)
        newsitem.getField('url').getMutator(newsitem)(url)
        #newsitem.getField('effective').getMutator(newsitem)(updated)
        newsitem.getField('subject').getMutator(newsitem)([
            self.context.getId(),
        ])

        self.add_image(newsitem, entry)

        # Publish
        wftool = getToolByName(self.context, 'portal_workflow')
        state = wftool.getInfoFor(newsitem, 'review_state', '(Unknown)')
        if state != 'published':
            try:
                wftool.doActionFor(newsitem, 'publish', comment='')
            except Exception, err:
                logger.exception(err)

        # Reindex
        newsitem.reindexObject()
        return newsitem

    def __call__(self, **kwargs):
        """ Run updater
        """
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
            return "No changes made until last update"

        etag = data.get('etag', None)
        if etag and efield:
            efield.getMutator(self.context)(etag)

        #last_updated = data.get('modified', None)
        #if isinstance(last_updated,
                      #time.struct_time) and len(last_updated) >= 6:
            #args = last_updated[:6] + (0, utc)
            #self.context.updated = datetime(*args)
        #else:
            #self.context.updated = datetime.now(bucharest)

        for entry in data.get('entries', ()):
            self.add_newsitem(entry)

        return '%s\t%s\tUPDATED' % (
            datetime.now(bucharest).strftime('%d-%m-%Y %H:%M'),
            self.context.absolute_url(1)
        )
