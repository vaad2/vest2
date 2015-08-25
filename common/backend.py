from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.encoding import smart_text
from django_jinja.backend import Jinja2, Template
from django.template.engine import Engine
from django.middleware.csrf import get_token
from django.utils.functional import SimpleLazyObject

# for django-rest support
import jinja2
import six
import sys


class ExTemplate(Template):
    def render(self, context=None, request=None):
        if context is None:
            context = {}

        if request is not None:
            def _get_val():
                token = get_token(request)
                if token is None:
                    return 'NOTPROVIDED'
                else:
                    return smart_text(token)

            context["request"] = request
            context["csrf_token"] = SimpleLazyObject(_get_val)

            # Support for django context processors
            for processor in self.backend.context_processors:
                context.update(processor(request))

        return self.template.render(context)

class ExJinja2(Jinja2):
    def __init__(self, params):
        ex_options = params.pop('EX_OPTIONS').copy()
        if 'DIRS' in ex_options:
            # FOR PYCHARM FIX
            params['DIRS'] = ex_options['DIRS']
            del ex_options['DIRS']

        self.app_dirname = True
        super(ExJinja2, self).__init__(params)
        # only for
        self.engine = Engine(self.dirs, False, **ex_options)

    def get_template(self, template_name):
        if not self.match_template(template_name):
            raise TemplateDoesNotExist("Template {} does not exists".format(template_name))

        try:
            return ExTemplate(self.env.get_template(template_name), self)
        except jinja2.TemplateNotFound as exc:
            six.reraise(TemplateDoesNotExist, TemplateDoesNotExist(exc.args), sys.exc_info()[2])
        except jinja2.TemplateSyntaxError as exc:
            six.reraise(TemplateSyntaxError, TemplateSyntaxError(exc.args), sys.exc_info()[2])
