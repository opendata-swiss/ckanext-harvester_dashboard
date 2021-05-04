# coding=UTF-8

import ckan.plugins as plugins
from ckan.lib.plugins import DefaultTranslation
import ckan.plugins.toolkit as toolkit
from ckanext.harvester_dashboard import logic as harvester_dashboard_logic
from ckanext.harvester_dashboard.helpers import harvester_dashboard_organization_title
import logging
log = logging.getLogger(__name__)


class HarvesterDashboardPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IRoutes, inherit=True)

    # ITranslation

    def i18n_domain(self):
        return 'ckanext-harvester_dashboard'

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')

    def get_actions(self):
        """
        Expose new API methods
        """
        return {
            'get_harvest_source_infos_for_user': harvester_dashboard_logic.get_harvest_source_infos_for_user
        }

    # ITemplateHelpers

    def get_helpers(self):
        """
        Provide template helper functions
        """
        return {
            'harvester_dashboard_organization_title': harvester_dashboard_organization_title
        }

    # IRouter

    def before_map(self, map):
        """adding custom routes to the ckan mapping"""

        map.connect('harvester_dashboard', '/harvest-dashboard',
                    controller='ckanext.harvester_dashboard.controllers:HarvesterDashboardController',  # noqa
                    action='dashboard')

        return map
