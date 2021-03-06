from time import strptime

from datetime import datetime

from sa_tools.parsers.parser import Parser
from sa_tools.parsers.tools.parser_dispatch import ParserDispatch
from sa_tools.parsers.tools.wrapper import BS4Adapter


class PMParser(Parser, ParserDispatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_parser_map(self, parser_map: dict=None):
        if not parser_map:
            parser_map = {'status': parse_status,
                          'icon': parse_icon,
                          'title': parse_title,
                          'sender': parse_sender,
                          'date': parse_date,
                          'check': parse_check}

        super().set_parser_map(parser_map=parser_map)

    def parse(self, content: BS4Adapter) -> iter:
        content = self.wrap(content)

        info_gen = gen_info(content, self.dispatch)

        return info_gen


def gen_info(content: BS4Adapter, dispatch) -> iter(((str, object),)):
    tds = content.find_all('td')

    for td in tds:
        key = td['class'][0]
        key, val = dispatch(key, td)

        if key == 'title':
            yield from gen_info_from_title(key, val)

        yield key, val


def gen_info_from_title(key: str, val) -> iter(((str, str),)):
        title, url = val

        yield 'url', url
        yield 'name', title
        yield parse_id(key, url)


def parse_status(key: str, content: BS4Adapter) -> (str, bool):
    new = "http://fi.somethingawful.com/images/newpm.gif"
    indicator = content.img['src']
    key = 'unread'

    return key, indicator == new


def parse_icon(key: str, content: BS4Adapter) -> (str, str or None):
    status = (content.img['src'] if content.img else None)
    return key, (content.img['src'] if content.img else None)


def parse_title(key: str, content: BS4Adapter) -> (str, (str, str)):
    title = content.text.strip()
    url = "http://fi.somethingawful.com/" + content.a['href']

    return key, (title, url)


def parse_sender(key: str, content: BS4Adapter) -> (str, str):
    return key, content.text.strip()


def parse_date(key: str, content: BS4Adapter) -> (str, datetime):
    date_str = content.text.strip()

    return key, strptime(date_str, '%b %d, %Y at %H:%M')


def parse_check(key: str, content: BS4Adapter) -> (str, BS4Adapter):
    return key, content


def parse_id(key: str, url: str) -> (str, int):
    id = url.split('privatemessageid=')[-1]

    return 'id', id