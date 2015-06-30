from django.core.urlresolvers import resolve
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import View
from django.conf import settings

from . import utils
from common.utils import ujson_response


class BaseMixin(View):
    breadcrumbs = []
    ajax_raw = False

    def permission_check(self, request, *args, **kwargs):
        return None

    def get_breadcrumbs(self):
        return self.breadcrumbs

    def render_to_response(self, context, **response_kwargs):
        context['breadcrumbs'] = self.get_breadcrumbs()

        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            **response_kwargs
        )

    def get_template_names(self):
        if hasattr(self, 'template_name') and self.template_name:
            tn = self.template_name
        else:
            namespace = resolve(self.request.path).namespace
            base = utils.camel_to_underline(self.__class__.__name__)

            tn = '%s/%s%s' % (namespace, base, getattr(settings, 'DEFAULT_TEMPLATE_EXT', '.html'))

        if self.request.is_ajax():
            tna = tn.split('.')
            tna[-2] = '%s_ajax' % tna[-2]
            return ['.'.join(tna)]

        return [tn]

    def _json_response(self, *args, **kwargs):
        return ujson_response(*args, **kwargs)

    def _pre_init(self, request, *args, **kwargs):
        pass

    def _post_init(self, request, *args, **kwargs):
        pass

    def dispatch(self, request, *args, **kwargs):
        result = self.permission_check(request, *args, **kwargs)

        self.paginator_data = {}

        if not result is None:
            return result

        if 'pk' in request.REQUESTS:
            kwargs['pk'] = request.REQUESTS

        if 'slug' in request.REQUESTS:
            kwargs['slug'] = request.REQUESTS['slug']

        self._pre_init(request, *args, **kwargs)

        if 'cmd' in request.REQUESTS:
            try:
                handler = getattr(self, 'cmd_%s' % request.REQUESTS['cmd'].lower())
                result = handler(request, *args, **kwargs)
            except Exception, e:
                if request.is_ajax():
                    return self._json_response({'success': False, 'data': None, 'errors': e})
                else:
                    raise Http404(e)

        else:
            result = super(BaseMixin, self).dispatch(request, *args, **kwargs)

        # for ajax response
        if request.is_ajax() or 'cmd' in request.REQUESTS:
            if isinstance(result, TemplateResponse):
                if not result.is_rendered:
                    result.render()
                success = True
                data = result.rendered_content
            elif isinstance(result, (list, tuple)):
                success, data = result
            else:
                success = result
                data = None

            errors = getattr(self, 'ajax_errors', {})

            if self.ajax_raw:
                return HttpResponse(data)

            return self._json_response({'success': success,
                                            'data': data,
                                            'meta': getattr(self, 'meta', {}),
                                            'errors': errors})

        return result


class AuthMixin(BaseMixin):
    no_access_url = '/'

    def _on_access_granted(self, request, *args, **kwargs):
        pass

    def permission_check(self, request, *args, **kwargs):
        # if not (request.user.is_authenticated() and request.user.is_active and request.user.is_approved):
        if not (request.user.is_authenticated() and request.user.is_active):
            return redirect(self.no_access_url)

        self._on_access_granted(request, *args, **kwargs)
