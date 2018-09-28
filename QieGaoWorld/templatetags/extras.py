from django import template

register = template.Library()

@register.filter
def select(value,args):
    return '<select class="uk-select animal_options" >%s</select>' % option(value,args)
    
@register.filter
def option(value,args):
    option=""
    for v in value:
        if v.id == None:
            v.id=v.value
        if v.id == args :
            selected="selected"
        else:
            selected=""
        option +='<option value="%s"%s>%s</option>' % (str(v.id),select,str(v.value))
    
    return option