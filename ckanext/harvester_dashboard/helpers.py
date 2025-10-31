import json
import logging

from ckan.lib.helpers import lang
from ckan.lib.i18n import get_available_locales

log = logging.getLogger(__name__)


def get_localized_value_from_language_dict(value):
    """Display localized value of a language dict."""
    localized_value = value.get(lang())
    if localized_value:
        return localized_value

    for locale in get_available_locales():
        if value.get(locale.language):
            return value.get(locale.language)

    return value


def harvester_dashboard_organization_title(value):
    """Display organization title and consider the cases that it is a value, a language
    dict, or a language dict dumped to a json string.
    """
    if isinstance(value, dict):
        return get_localized_value_from_language_dict(value)
    try:
        value = json.loads(value)
        return get_localized_value_from_language_dict(value)
    except (AttributeError, ValueError):
        return value
