from bs4 import BeautifulSoup


class SAObj(object):
    """
    The gloves are off. It's a fucking free for all.
    """

    def __init__(self, parent, id=None, content=None, name=None, url=None, **properties):
        super(SAObj, self).__init__()

        self.parent = parent
        self.session = self.parent.session

        self.id = id
        self._content = content
        self.name = name
        self.url = url
        self._properties = properties

        self.unread = True
        self.base_url = None

        self._dynamic_attr()

    def __repr__(self):
        if self.name:
            return self.name
        else:
            return super(SAObj, self).__repr__()

    def __str__(self):
        return self.__repr__()

    def __getattr__(self, attr):
        """
        Monkey patch of the year, 2014.

        See _delete_extra() for why this exists.

        I'm on the fence about this one. Getting rid of extraneous null
        attrs makes for a clean namespace, but is a huge fuck you to sane
        software design.

        This is somewhere in between keeping a dozen null attrs attached to
        an sa_obj or having lean objects, gets/sets, passing a dozen kwargs
        to a constructor and using hasattr() before attr lookup.

        If I'm not being paid I'm going to have fun.
        """
        if attr not in self.__dict__:
            return None

    def _delete_extra(self):
        """
        Second runner up.

        If unread, call this at the end of your overridden read()
        """
        significant_false_vals = False, 0
        delete_these = [attr for attr, val in self.__dict__.items()
                        if not val and val not in significant_false_vals]

        for attr in delete_these:
            delattr(self, attr)

    def _dynamic_attr(self):
        """
        Consolation prize.

        If unread, call this at the end of your overridden read()
        """
        for name, attr in self._properties.items():
            setattr(self, name, attr)

        del self._properties

    def _fetch(self, url=None):
        if not url:
            url = self.url

        response = self.session.get(url)

        if not response.ok:
            raise Exception(("There was an error with your request ",
                             url, response.status_code, response.reason))

        self._content = BeautifulSoup(response.content)

    def read(self, pg=1, setup_callback=None, **kwargs):
        """
        You need to call _dynamic_attr() and _delete_extra() for full
        sa_obj interop.

        If unread, call them at the end of your overridden read()
        """
        if self.unread:
            self.unread = False

        if setup_callback:
            setup_callback(**kwargs)
            self._delete_extra()


class SAListObj(SAObj):
    def __init__(self, *args, collection=None, **properties):
        self.page = None
        self.pages = None
        self.navi = None

        self._collection = collection
        self.children = self._collection
        self._page_keyword = 'pagenumber'

        super(SAListObj, self).__init__(*args, **properties)

    def _setup_navi(self, pg=1):
        if not self.navi:
            navi = self._content.find('div', 'pages')
            self.navi = SAPageNavi(self, content=navi)

        self.navi.read(pg)

    def read(self, pg=1):
        super(SAListObj, self).read(pg)

        url = self.url + '&' + self._page_keyword + '=' + str(pg)
        self._fetch(url)
        self._setup_navi(pg)


class SAPageNavi(SAObj):
    def __init__(self, *args, **properties):
        super(SAPageNavi, self).__init__(*args, **properties)

        self.page = 1
        self.pages = 1

    def read(self, pg=1):
        super(SAPageNavi, self).read(pg)

        self.page = pg
        self._parse_page_selector()
        self._modify_parent()
        self._delete_extra()

    def _modify_parent(self):
        self.parent.page = self.page
        self.parent.pages = self.pages

    def _parse_page_selector(self):
        page_selector = self._content.find_all('option')

        if len(page_selector):
            self.pages = page_selector[-1].text
        else:
            self.pages = 1
