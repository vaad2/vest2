import re

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.apps import apps


from django.utils.safestring import mark_safe
from django_jinja import library


from common import thread_locals

import jinja2

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


@jinja2.contextfunction
@library.global_function
def vt_tree(context, *args, **kwargs):
    request = context['request']

    url = re.sub(r'/+', '/', '/%s/' % request.path_info.strip('/'), re.IGNORECASE)
    query = kwargs.get('query', {})
    model = apps.get_model(kwargs['model'])

    queryset = model.objects.filter(**query)

    item = None

    max_level = kwargs.get('max_level', 1000)
    min_level = kwargs.get('min_level', 0)

    cats = {}

    if kwargs.get('pk'):
        item = queryset.get(pk=args[0])
    elif kwargs.get('slug'):
        item = queryset.get(slug=args[0])

    items = list(item.descendants_get()) if item else list(queryset)

    if len(items):
        active_item = None
        prev_item = None
        item_map = {}

        for item in items:
            if item.level > max_level:
                continue
            if prev_item and prev_item.level < item.level:
                prev_item.open = True

            if prev_item and prev_item.level > item.level:
                prev_item.close = prev_item.level - item.level
            else:
                item.close = 0

            prev_item = item
            item_map[str(item.pk)] = item

            if cmp(url, item):
                cats[args[0]] = item
                active_item = item
                item.active = True
                item.current = True

        item.close = item.level - items[0].level
        if active_item:
            for item_pk in active_item.path.split(','):
                if item_pk in item_map:
                    item_map[item_pk].active = True

    #
    # if len(args):
    #     try:
    #         item = cls.objects.get(pk=args[0])
    #     except BaseException, e:
    #         item = cls.objects.get(name=args[0])
    #
    #     items = list(item.descendants_get(**qkwargs))
    # else:
    #     items = list(cls.objects.filter(**qkwargs))
    #








    # # qkwargs = kwargs.get('qkwargs', {})
    # df = {'level__lte': max_level, 'level__gte': min_level}
    # df.update(qkwargs)
    #
    # cls = kwargs['cls']
    # # cats = get_thread_var(VEST_CURRENT_TREE, {})
    # cats = {}
    # if isinstance(cls, basestring):
    #     cls = model_class_get(cls)
    #
    # try:
    #     if len(args):
    #         try:
    #             item = cls.objects.get(pk=args[0])
    #         except BaseException, e:
    #             item = cls.objects.get(name=args[0])
    #
    #         items = list(item.descendants_get(**qkwargs))
    #     else:
    #         items = list(cls.objects.filter(**qkwargs))
    # except cls.DoesNotExist:
    #     return ''
    #
    # if 'cmp' in kwargs:
    #     cmp = kwargs['cmp']
    # else:
    #     def cmp(op1, item):
    #         if hasattr(item, 'url_get'):
    #             return op1 == item.url_get() or op1 == '%s/' % item.url_get()
    #         return op1 == item.url or op1 == '%s/' % item.url
    #
    # if len(items):
    #     active_item = None
    #     prev_item = None
    #     item_map = {}
    #     for item in items:
    #         if item.level > max_level:
    #             continue
    #         if prev_item and prev_item.level < item.level:
    #             prev_item.open = True
    #
    #         if prev_item and prev_item.level > item.level:
    #             prev_item.close = prev_item.level - item.level
    #         else:
    #             item.close = 0
    #
    #         prev_item = item
    #         item_map[str(item.pk)] = item
    #
    #         if cmp(url, item):
    #             cats[args[0]] = item
    #             active_item = item
    #             item.active = True
    #             item.current = True
    #
    #     item.close = item.level - items[0].level
    #     if active_item:
    #         for item_pk in active_item.path.split(','):
    #             if item_pk in item_map:
    #                 item_map[item_pk].active = True
    #
    # # set_thread_var(VEST_CURRENT_TREE, cats)
    #
    # return render_to_string(template_name, {
    #     'items': items,
    #     'curr_url': url,
    #     'request': request,
    #     'args': args,
    #     'kwargs': kwargs
    # })
    #


@library.filter
@library.global_function
def vt_iif(expr, result_true, result_false=''):
    return result_true if expr else result_false

@library.filter
def vt_verbose_name(object, is_plural=False):
    model = type(object)
    return model._meta.verbose_name_plural.title() if is_plural else model._meta.verbose_name.title()