from .genHTML import html_jinja_env, HTML_TEMPLATE_DIR
from ecldoc.Utils import call_macro_by_name, joinpath
from ecldoc.parseDoc import construct_type

html_jinja_env.filters['macro'] = call_macro_by_name
tag_template = html_jinja_env.get_template(joinpath(HTML_TEMPLATE_DIR, 'taglets.tpl.html'))

def render_param(tag_param) :
    if len(tag_param.tuples['tuples']) == 0 : return ''
    html_tuples = []
    for t in tag_param.tuples['tuples'] :
        html_tuples.append((t[0], construct_type(t[2]), t[1]))

    render = tag_template.render(render_name='threetag', args=['Parameters', html_tuples])
    return render

def render_field(tag_field) :
    if len(tag_field.tuples['tuples']) == 0 : return ''
    html_tuples = []
    for t in tag_field.tuples['tuples'] :
        html_tuples.append((t[0], construct_type(t[2]), t[1]))

    return tag_template.render(render_name='threetag', args=['Fields', html_tuples])

def render_return(tag_return) :
    if len(tag_return.docstrings) == 0 and tag_return.return_type is None : return ''
    return_tuple = [(construct_type(tag_return.return_type), tag_return.return_desc)]
    return tag_template.render(render_name='twotag', args=['Returns', return_tuple])

def render_see(tag_see) :
    render = tag_template.render(render_name='onetag', args=['See', tag_see.tuples['tuples']])
    return render

def render_parent(tag_parent) :
    if len(tag_parent.tuples['tuples']) == 0 : return ''
    render = tag_template.render(render_name='parenttag', args=['Parents', tag_parent.tuples['tuples']])
    return render

def render_content(tag_content) :
    render = tag_template.render(render_name='contenttag', args=[tag_content.text])
    return render

def render_firstline(tag_firstline) :
    return tag_firstline.text

def render_generaltag(tag_generaltag) :
    render = tag_template.render(render_name='onetag', args=[tag_generaltag.tuples['name'], tag_generaltag.tuples['tuples']])
    return render

tag_renders = { 'param' : render_param,
                'field' : render_field,
                'return' : render_return,
                'see' : render_see,
                'parent' : render_parent,
                'content' : render_content,
                'firstline' : render_firstline,
                'generaltag' : render_generaltag
              }



