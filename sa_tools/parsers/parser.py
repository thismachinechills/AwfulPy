from sa_tools.base.sa_obj import SAObj
from sa_tools.parsers.tools.parser_dispatch import ParserDispatch
from sa_tools.parsers.tools.bs_wrapper import BSWrapper


class Parser(SAObj, ParserDispatch):
    def __init__(self, parent, wrapper=BSWrapper, parser_map=None, *args, **kwargs):
        super(Parser, self).__init__(parent, *args, parser_map=parser_map, **kwargs)
        self.id = self.parent.id
        self.wrapper = None
        self.set_wrapper(wrapper)
        self.results = dict()

        self._delete_extra()

    def set_wrapper(self, wrapper=BSWrapper):
        self.wrapper = wrapper(self.parent)

        if self.parent._content:
            self.wrapper.wrap_parent_content()

    def parse(self, content=None, *args, **kwargs):
        self.read()
        self.wrapper.wrap_parent_content()

        if content:
            return self.wrapper.wrap_content(content)


    @property
    def content(self):
        return self.wrapper.content

    @content.setter
    def content(self, new_val):
        self.wrapper.content = new_val