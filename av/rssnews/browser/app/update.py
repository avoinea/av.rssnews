""" Update cron
"""

from Products.Five.browser import BrowserView

class Update(BrowserView):
    """ News updater """
    def __call__(self, **kwargs):
        print "====================="
        print "I was here"
        return "Me"
