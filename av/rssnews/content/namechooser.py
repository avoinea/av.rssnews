""" Choose name
"""
import re
from zope.interface import implements

from zope.app.container.interfaces import INameChooser
from zope.app.container.contained import NameChooser as ContainedNameChooser
from av.rssnews.config import RSS_MAXID

romanian = {
    194: 65,    # Sh
                #u'\u015E': u'S',
    259: 97,    # sh
                #u'\u015F': u's',
    258: 65,    # Tz
                #u'\u0162': u'T',
    354: 84,    # tz
                #u'\u0163': u't',
    226: 97,    # Ah
                #u'\u0102': u'A',
    238: 105,   # ah
                #u'\u0103': u'a',
    355: 116,   # A^
                #u'\u00C2': u'A',
    206: 73,    # a^
                #u'\u00E2': u'a',
    350: 83,    # I^
                #u'\u00CE': u'I',
    351: 115,   # i^
                #u'\u00EE': u'i',
}

class NameChooser(ContainedNameChooser):
    """A name chooser for newsitems.
    """
    implements(INameChooser)

    def __init__(self, context):
        self.context = context

    def checkName(self, name, object=None):
        """ Check
        """
        return True

    def chooseName(self, name, object=None):
        """ Choose
        """
        name = name or getattr(object, 'title', '')
        if not isinstance(name, unicode):
            name = name.decode('utf-8')
        name = name.strip().lower().translate(romanian)
        name = name.replace(' ', '-')
        name = name.strip('.')

        safe = re.compile(r'[^_A-Za-z0-9\.\-]')
        name = safe.sub('', name)
        new_name = name.split('-')
        if len(new_name) <= (RSS_MAXID + (0.20 * RSS_MAXID)): # 20%
            return name
        return '-'.join(new_name[:RSS_MAXID])
