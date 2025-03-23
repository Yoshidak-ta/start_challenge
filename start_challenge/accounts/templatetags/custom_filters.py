from django import template

register = template.Library()

@register.filter
def tens(value):
  try:
    return int(value) // 10
  except (ValueError, TypeError):
    return ''
  
@register.filter
def unique_answers(value):
  seen=set()
  return [x for x in value if not (x in seen or seen.add(x))]