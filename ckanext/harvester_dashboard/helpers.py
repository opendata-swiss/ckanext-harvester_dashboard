# encoding: utf-8

import json
import logging

import ckan.plugins.toolkit as tk
from ckan.lib.helpers import lang

log = logging.getLogger(__name__)


def get_localized_value_from_language_dict(value):
    """display localized value of a language dict"""
    user_language = lang()
    try:
        localized_value = value.get(user_language)
        if localized_value:
            return localized_value
        locales = tk.config.get("ckan.locales_offered", None)
        if locales:
            for locale in locales.split(" "):
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
