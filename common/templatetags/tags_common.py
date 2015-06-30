from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.safestring import mark_safe

from django_jinja import library
from common import thread_locals
from urlparse import urljoin


@library.global_function
def vt_static(path, **kwargs):
    return static(path, **kwargs)


@library.global_function
def vt_scripts():
    return mark_safe('\n'.join(thread_locals.get_thread_var('_vt_scripts', {}).values()))


@library.global_function
def vt_thumb_margin(image, geometry):
    from sorl.thumbnail.templatetags import thumbnail
    return thumbnail.margin(image, geometry)


@library.global_function
def vt_thumb(*args, **kwargs):
    from sorl.thumbnail import get_thumbnail
    return get_thumbnail(*args, **kwargs)

