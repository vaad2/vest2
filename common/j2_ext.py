from collections import OrderedDict
from jinja2 import nodes, TemplateSyntaxError
from jinja2.ext import Extension


# import collections
from . import thread_locals

from django.core.cache import get_cache


class VTScript(Extension):
    # a set of names that trigger the extension.
    tags = set(['vts'])

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        try:
            name = parser.stream.expect('name').value
        except TemplateSyntaxError:
            name = None

        body = parser.parse_statements(['name:endvts'], drop_needle=True)

        return nodes.CallBlock(self.call_method('_vt_script_cache', [nodes.Const(name)]),
                                                [], [], body).set_lineno(lineno)

    def _vt_script_cache(self, name, caller):
        rx_scripts = thread_locals.get_thread_var('_vt_scripts', OrderedDict())

        if not name:
            name = len(rx_scripts) + 10

        rx_scripts[name] = caller()

        thread_locals.set_thread_var('_vt_scripts', rx_scripts)

        return u''


