""" Custom content
"""
def initialize(context):
    """ Zope 2
    """
    from av.rssnews.content import news
    news.register()
