from sa_tools.base.sa_obj import SAObj
from sa_tools.base.descriptors import IntOrNone
from sa_tools.parsers.page_navi import PageNaviParser


class PageNavi(SAObj):
    page = IntOrNone()
    pages = IntOrNone(1)

    def __init__(self, *args, **properties):
        super(PageNavi, self).__init__(*args, **properties)
        self._from_parent()
        self.parser = PageNaviParser(self)

    def __repr__(self):
        if self.parent.unread:
            return "Navi: unread parent_obj"

        return "Page " + str(self.page) + " of " + str(self.pages)

    def _modify_parent(self):
        self.parent.page = self.page
        self.parent.pages = self.pages

    def _from_parent(self):
        self.page = self.parent.page
        self.pages = self.parent.pages

    def read(self, pg: int=1):
        super(PageNavi, self).read(pg)

        self.page = pg if pg <= self.pages else self.pages
        self.parser.parse()
        self._modify_parent()
        self._delete_extra()