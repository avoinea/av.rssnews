""" Custom content
"""
def initialize(context):
    """ Zope 2
    """
    from av.rssnews.content import newsitem
    newsitem.register()

    from av.rssnews.content import news
    news.register()

    from av.rssnews.content import server
    server.register()
