from ckan.lib.helpers import lang

def harvester_dashboard_organization_title(value):
    """display the organization title"""
    return value.get(lang()) or value.get("de") or value.get("fr") or value.get("en") or value.get("it") or value