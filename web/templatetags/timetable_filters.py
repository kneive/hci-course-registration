from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary"""
    if dictionary is None:
        return {'courses': [], 'spans': {}}
    result = dictionary.get(key, {'courses': [], 'spans': {}})
    # Handle old format (list) for backward compatibility
    if isinstance(result, list):
        return {'courses': result, 'spans': {}}
    return result

@register.filter
def get_span(spans_dict, course_id):
    """Get the span value for a course"""
    if not spans_dict or not isinstance(spans_dict, dict):
        return 1
    return spans_dict.get(course_id, 1)