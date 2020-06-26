import re
from django import template

register = template.Library()


@register.tag(name="render_block")
def render_block(parser, token):
    '''
    Assign contents of the block to a variable.
    
    Why? Because normal blocks allow only one usage per page,
    it's impossible to use the same block in few places on the page.
    
    USAGE:

    {% render_block as primary_bg_color %}
      #ffee77
    {% end_render_block %}
    
    <p>
      Main color is: {{ primary_bg_color }}
    </p>
    
    <styles>
    body {
      background-color: {{ primary_bg_color }};
    }
    a {
      color: {{ primary_bg_color }};
    }
    </styles>
    '''
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires arguments" % token.contents.split()[0]
        )
    match = re.search(r'as (\w+)', args)
    if not match:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    var_name = match.group(1)

    nodelist = parser.parse(('end_render_block',))
    parser.delete_first_token()
    return RenderBlockAsVarNode(nodelist, var_name)


class RenderBlockAsVarNode(template.Node):
    def __init__(self, nodelist, var_name):
        self.nodelist = nodelist
        self.var_name = var_name

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.var_name] = output
        return ''
