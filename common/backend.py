from django_jinja.backend import Jinja2, Template
from django.template.engine import Engine

class ExJinja2(Jinja2):
    def __init__(self, params):
        ex_options = params.pop('EX_OPTIONS').copy()
        self.app_dirname = True
        super(ExJinja2, self).__init__(params)
        # only for
        self.engine = Engine(self.dirs, False, **ex_options)

    def get_template(self, template_name):
        try:
            return super(ExJinja2, self).get_template(template_name)
        except Exception, e:
            return Template(self.engine.get_template(template_name))
