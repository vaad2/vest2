from collections import OrderedDict
import hashlib
import os
import urllib2
import urlparse
import sys
import re
import codecs
from transliterate import translit

from datetime import datetime
from uuid import uuid4
from copy import deepcopy
from importlib import import_module

import ujson

from django.contrib import auth
from django.core.files.base import ContentFile
from django.apps import apps
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from django.template.loader import get_template
from django.utils.datastructures import SortedDict
from django.utils.deconstruct import deconstructible
from django.utils.translation import get_language
from django.conf import settings

def file_put_contents(filename, data, utf=False):
    f = codecs.open(filename, "w", "utf-8-sig") if utf else open(filename, 'w')
    f.write(data)
    f.close()


def file_get_contents(url):
    if os.path.exists(url):
        return open(url, 'r').read()

    opener = urllib2.build_opener()
    content = opener.open(url).read()
    return content


def image_from_url_get(url):
    url_data = urlparse.urlparse(url)

    ext = os.path.splitext(url_data.path)[1]
    return ContentFile(urllib2.urlopen(url).read())


def image_from_url_get_2(url, name_gen=True):
    file = image_from_url_get(url)
    ext = os.path.splitext(urlparse.urlparse(url).path)[1]
    if name_gen:
        md5 = hashlib.md5()
        md5.update('%s-%s' % (url, datetime.now()))
        if not ext:
            ext = '.jpg'

        file.name = '%s%s' % (md5.hexdigest(), ext.lower())
    else:
        file.name = os.path.basename(url)

    return file


def md5_for_file(f, block_size=2 ** 20):
    f = open(f)
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)

    f.close()
    return md5


def model_class_get(path):
    return apps.get_model(*path.split('.'))


def model_object_get(path, pk):
    return model_class_get(path).objects.get(pk=pk)


def class_get(path):
    arr = path.split('.')
    return getattr(import_module('.'.join(arr[0:-1])), arr[-1])


def qset_to_dict(qset, key='id'):
    res = OrderedDict()
    for item in qset:
        res[getattr(item, key)] = item
    return res


def shop_login(request, username, password):
    if auth.SESSION_KEY in request.session:
        del request.session[auth.SESSION_KEY]
        request.session.modified = True

    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
    return user


def exception_details():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    return file_name, exc_type, exc_obj, exc_tb


def dict_sort(dic_or_list, key):
    if isinstance(dic_or_list, list):
        sorted_x = sorted(dic_or_list, key=lambda x: x[key])
    else:
        sorted_x = sorted(dic_or_list.iteritems(), key=lambda x: x[1][key])
    return sorted_x


def handle_uploaded_file(f, path):
    destination = open(path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()


def file_exists(path):
    try:
        with open(path) as f:
            return True
    except IOError as e:
        return None


# def template_to_source():
# loader = Loader()
#
#     apps_root = os.path.realpath('%s/../' % settings.PROJECT_ROOT)
#
#     for st in SiteTemplate.active_objects.all():
#         for filepath in loader.get_template_sources(st.name):
#             try:
#                 if file_exists(filepath) and filepath.startswith(apps_root):
#                     with codecs.open(filepath, 'w', 'utf8') as f:
#                         f.write(st.content)
#                         print st.name, filepath, '-ok'
#             except IOError as e:
#                 print e


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def camel_to_underline(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()

'''

 <?xml version="1.0" encoding="UTF-8"?>
 <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
 {% for item in items %}
 {% if item.url|first == '/' %}
<url>
<loc>{{ item.url }}</loc>
<changefreq>weekly</changefreq>
<priority>1</priority>
</url>
{% endif %}
{% endfor %}
</urlset>

'''
class SiteMapGenerator(object):
    def __init__(self):
        self.file = None

    def _write_header(self):
        self.file.write('''<?xml version="1.0" encoding="UTF-8"?>''')

    def _open_urlset(self):

        self.file.write('''<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">''')

    def _close_urlset(self):
        self.file.write('</urlset>')

    def _write_urls(self, urls):
        for url in urls:
            self.file.write('<url>')
            self.file.write('<loc>%(loc)s</loc>' % url)
            self.file.write('<changefreq>%(changefreq)s</changefreq>' % url)
            self.file.write('<priority>%(priority)s</priority>' % url)
            self.file.write('</url>')

    def generate(self, path, **kwargs):
        try:
            self.file = open(path, 'w+')
            self._write_header()
            self._open_urlset()
            self._write_urls(kwargs['urls'])
            self._close_urlset()

        except BaseException, e:
            from common.std import exception_details

            import logging

            log = logging.getLogger('file_logger')
            ed = unicode(exception_details())
            log.log(logging.DEBUG, ed)

            return {'success': False, 'error': ed}
        finally:
            self.file.close()
        return {'success': True}


def dict_merge(target, *args):
    # Merge multiple dicts
    if len(args) > 1:
        for obj in args:
            dict_merge(target, obj)
        return target

    # Recursively merge dicts and set non-dict values
    obj = args[0]
    if not isinstance(obj, dict):
        return obj
    for k, v in obj.iteritems():
        if k in target and isinstance(target[k], dict):
            dict_merge(target[k], v)
        else:
            target[k] = deepcopy(v)
    return target

# request.FILES['file']
# path = 'users/1' for example
from django.core.files.storage import default_storage


def form_file_save(file, path):
    name, ext = os.path.splitext(file.name)
    name = '%s%s' % (str(uuid4()), ext)
    file_path = '%s/%s' % (path, name)

    full_path = default_storage.save(file_path, ContentFile(file.read()))
    return file_path, full_path


@deconstructible
class UploadPath(object):
    def __init__(self, *args, **kwargs):
        self.base_path = kwargs['base_path']
        self.field_name = kwargs.get('field_name')
        self.name_gen = kwargs.get('name_gen')

    def __call__(self, instance, file_name):
        name = file_name

        if self.name_gen:
            name, ext = os.path.splitext(file_name)
            name = '%s%s' % (str(uuid4()), ext)


        if self.field_name:
            field = getattr(instance, self.field_name)
            path = os.path.join(self.base_path, field.slug if hasattr(field, 'slug') else unicode(field.pk))
        else:
            path = self.base_path


        if not os.path.exists(path):
            os.makedirs(path)

        path = os.path.join(path, name)

        return path
        # return path.format(instance.user.username, self.sub_path, filename)


def lang_get():
    return get_language().split('-')[0]


def slugify_ru(in_str):
    try:
        return slugify(translit(in_str, reversed=True))
    except Exception, e:
        return slugify(unicode(in_str), reversed=True)


def ujson_response(x):
    return HttpResponse(ujson.dumps(x), content_type='application/json; charset=UTF-8')



def ex_find_template(name, exclude=[], dirs=None):
    using = None
    if len(exclude):
        using = []
        for loader_name in settings.TEMPLATE_LOADERS:
            if loader_name in exclude:
                continue
            using.append(loader_name)

    return get_template(name)


# language prefix
vt_lang_prefix = lambda url: r'^([A-Za-z]{2}/)?%s' % url
