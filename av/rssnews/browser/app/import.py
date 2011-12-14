""" Import content from XML
"""
import logging
from zope.component import queryMultiAdapter
from av.rssnews.interfaces import IImport
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser import BrowserView
logger = logging.getLogger('av.rssnews')

class Import(BrowserView):
    """ Import content from XML
    """
    def __call__(self, **kwargs):
        if self.request:
            kwargs.update(self.request.form)
        xmlfile = kwargs.get('xmlfile', '')
        if not xmlfile:
            return self.index()

        xml = xmlfile.read()
        importer = queryMultiAdapter((self.context, self.request), IImport)
        if not importer:
            status = ('!!! Could not import XML as there is no '
                      'IImport adapter for this context !!!')
            IStatusMessage(self.request).addStatusMessage(status, type="error")
            return self.request.response.redirect(
                self.context.absolute_url() + '/@@import.xml')

        try:
            importer.body = xml
        except Exception, err:
            logger.exception(err)
            status = err
            stype = "error"
        else:
            status = 'XML succesfully imported.'
            stype = "info"

        IStatusMessage(self.request).addStatusMessage(status, type=stype)
        return self.request.response.redirect(
                self.context.absolute_url() + '/@@import.xml')
