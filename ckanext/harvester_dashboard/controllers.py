# encoding: utf-8

import logging
from ckan.lib.base import BaseController, render
from ckan.common import c, request, config, _
from ckan.lib.base import render
import ckan.plugins.toolkit as tk
log = logging.getLogger(__name__)


class HarvesterDashboardController(BaseController):
    """Controller for Harvester Dashboard Route"""
    def dashboard(self):
        context = {'user': c.user,
                   'auth_user_obj': c.userobj}
        c.harvest_source_infos = tk.get_action('get_harvest_source_infos_for_user')(context, {})  # noqa

        return render('harvester_dashboard/list.html')


