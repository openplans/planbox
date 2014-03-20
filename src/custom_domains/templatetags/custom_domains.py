from django.template.base import TemplateSyntaxError, Library, kwarg_re
from django.template.defaulttags import URLNode as BaseURLNode

register = Library()


class URLNode (BaseURLNode):
    def render(self, context):
        import pdb; pdb.set_trace()
        url = super(URLNode, self).render(context)
        if 'request' in context:
            request = context['request']
            if hasattr(request, 'domain_mapping'):
                url = request.domain_mapping.fix_url(url)
        return url


@register.tag
def url(parser, token):
    """
    This is essentially a verbatim copy of django.template.defaulttags.url in
    Django 1.6.2.
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    try:
        viewname = parser.compile_filter(bits[1])
    except TemplateSyntaxError as exc:
        exc.args = (exc.args[0] + ". "
                "The syntax of 'url' changed in Django 1.5, see the docs."),
        raise
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to url tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    return URLNode(viewname, args, kwargs, asvar)
