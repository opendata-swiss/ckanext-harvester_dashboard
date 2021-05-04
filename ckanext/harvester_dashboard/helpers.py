from ckan.lib.helpers import lang
import ckan.plugins.toolkit as tk

def harvester_dashboard_organization_title(value):
    """display the organization title"""
    try:
        localized_value = value.get(lang())
        if localized_value:
            return localized_value
        locales = tk.config.get('ckan.locales_offered')
        if locales:
            for locale in locales:
                return value.get(locale)
    except Exception:
        return value
