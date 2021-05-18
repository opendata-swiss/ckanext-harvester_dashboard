# encoding: utf-8

import logging
import json
from ckan.lib.helpers import lang
import ckan.plugins.toolkit as tk

log = logging.getLogger(__name__)


def get_localized_value_from_language_dict(value):
    """display localized value of a language dict"""
    user_language = lang()
    try:
        localized_value = value.get(user_language)
        if localized_value:
            return localized_value
        locales = tk.config.get('ckan.locales_offered')
        if locales:
            for locale in locales.split(' '):
                if value.get(locale):
                    return value.get(locale)
    except Exception:
        return value


def harvester_dashboard_organization_title(value):
    """display organization title and consider the cases that it is a value,
    a language dict or a language dict warpped as json string"""
    if isinstance(value, dict):
        return get_localized_value_from_language_dict(value)
    try:
        value = json.loads(value)
        return get_localized_value_from_language_dict(value)
    except ValueError:
        return value
