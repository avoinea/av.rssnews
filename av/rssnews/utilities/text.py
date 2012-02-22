""" Text utility
"""
import re
import difflib
from zope.interface import implements
from interfaces import IText
from keywords import NON_WORDS

ROMANIAN = {
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

class Text(object):
    """ Handle text
    """
    implements(IText)

    def translate(self, text, language=ROMANIAN.copy()):
        """ Translate text to ascii using language mapping
        """
        if not isinstance(text, unicode):
            text = text.decode('utf-8')
        return text.translate(language)

    def truncate_words(self, text, words=14, orphans=1, suffix='...'):
        """ Truncate text by number of words. Orphans is the number of trailing
        words not to cut, for example:

            >>> a = 'This is a nice method'
            >>> Text().truncate_words(a, 3, 2)
            'This is a nice method'

            >>> Text().truncate_words(a, 3, 1)
            'This is a...'

        """
        keywords = text.split()
        keywords = [word for word in keywords if word]
        if(len(keywords) <= (words + orphans)):
            return text
        return ' '.join(keywords[:words]) + suffix

    def truncate_length(self, text, length=60, orphans=5, suffix='...'):
        """ Truncate text by number of characters without cutting words at
        the end.
        Orphans is the number of trailing chars not to cut, for example:

            >>> a = 'This is a nice method'
            >>> Text().truncate_length(a, 19, 2)
            'This is a nice method'

            >>> Text().truncate_length(a, 19, 1)
            'This is a nice...'
        """
        text = ' '.join(word for word in text.split() if word)
        if len(text) <= length + orphans:
            return text
        return ' '.join(text[:length+1].split()[:-1]) + suffix

    def truncate(self, text, words=14, length=60, suffix='...'):
        """ Split text by given words and length
        """
        orphans = int(0.1 * length) # 10%
        trunk = self.truncate_length(text, length, orphans, '')

        orphans = int(0.1 * words) # 10%
        trunk = self.truncate_words(trunk, words, orphans, '')

        if trunk == text:
            return text

        return trunk + suffix

    def keywords(self, title, description, limit=10):
        """ Return keywords in text
        """
        safe = re.compile(r'[^A-Za-z\-\s]')

        title = self.translate(title)
        title = safe.sub('', title)
        title = set(x for x in title.split()
                    if x.lower() not in NON_WORDS)

        description = self.translate(description)
        description = safe.sub('', description)
        description = set(x for x in description.split()
                          if x.lower() not in NON_WORDS)

        keywords = set()
        for word in title:
            matches = difflib.get_close_matches(word, description)
            if matches:
                keywords.add(word)
                keywords.update(matches)

        return keywords
