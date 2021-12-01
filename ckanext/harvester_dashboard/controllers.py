# encoding: utf-8

import logging
from ckan.lib.base import BaseController, render
from ckan.common import c, request, _
import ckan.plugins.toolkit as tk
from ckanext.harvester_dashboard.helpers import \
    harvester_dashboard_organization_title
log = logging.getLogger(__name__)
RESULT_GATHER_ERRORS = 'gather-errors'
RESULT_IMPORT_ERRORS = 'import-errors'
RESULT_NO_UPDATES = 'no-updates'
RESULT_OK = 'ok'
RESULT_ALL = 'all'
RESULT_OPTIONS = [{'text': _('Results: all results'),
                   'value': RESULT_ALL},
                  {'text': _('Results: gather errors'),
                   'value': RESULT_GATHER_ERRORS},
                  {'text': _('Results: import errors'),
                   'value': RESULT_IMPORT_ERRORS},
                  {'text': _('Results: no updates'),
                   'value': RESULT_NO_UPDATES},
                  {'text': _('Results: okay'),
                   'value': RESULT_OK}]
RUN_OPTIONS = [{'text': _('Run: all'), 'value': RESULT_ALL},
               {'text': _('Run: finished'), 'value': 'Finished'},
               {'text': _('Run: running'), 'value': 'Running'},
               {'text': _('Run: current'), 'value': 'Current'}]


class HarvesterDashboardController(BaseController):
    """Controller for Harvester Dashboard Route"""
    def dashboard(self):
        c.q = request.params.get('q', '')
        c.source_type = request.params.get('source_type', RESULT_ALL)
        c.job_result = request.params.get('job_result', RESULT_ALL)
        c.job_run = request.params.get('job_run', RESULT_ALL)
        context = {'user': c.user,
                   'auth_user_obj': c.userobj}
        harvest_source_list = tk.get_action('get_harvest_source_infos_for_user')(context, {})  # noqa
        c.source_type_options = _get_source_type_options(harvest_source_list)
        c.job_result_options = RESULT_OPTIONS
        c.job_run_options = RUN_OPTIONS
        harvest_source_list = filter(
            lambda harvest_source_info: _source_type_test(harvest_source_info,
                                                          c.source_type),
            harvest_source_list
        )
        harvest_source_list = filter(
            lambda harvest_source_info: _job_result_test(harvest_source_info,
                                                         c.job_result),
            harvest_source_list)
        harvest_source_list = filter(
            lambda harvest_source_info: _job_run_test(harvest_source_info,
                                                      c.job_run),
            harvest_source_list)
        if c.q:
            harvest_source_list = filter(
                lambda harvest_source_info:
                _source_name_test(
                    harvest_source_info,
                    c.q
                ),
                harvest_source_list)
        c.harvest_source_infos = harvest_source_list
        return render('harvester_dashboard/list.html')


def _source_type_test(harvest_source_info, source_type):
    if source_type == RESULT_ALL:
        return True
    source_type_match = harvest_source_info.get('source')\
        and harvest_source_info.get('source').type == source_type
    if source_type_match:
        return True
    return False


def _source_name_test(harvest_source_info, q):
    organization_title = harvester_dashboard_organization_title(
        harvest_source_info.get('organization').title
    )
    organization_match = q in organization_title
    harvest_source_match = q in harvest_source_info.get('source').title
    if organization_match or harvest_source_match:
        return True
    return False


def _job_result_test(harvest_source_info, job_result):
    if job_result == RESULT_ALL:
        return True
    job = harvest_source_info.get('job')
    if job:
        stats = job.last_job.get('stats')
        if job_result == RESULT_GATHER_ERRORS:
            if job.last_job.get('gather_error_summary'):
                return True
            else:
                return False
        if job_result == RESULT_NO_UPDATES:
            if stats and not stats.get('updated') and not stats.get('added'):
                return True
            else:
                return False
        if job_result == RESULT_IMPORT_ERRORS:
            if job.last_job.get('object_error_summary'):
                return True
            else:
                return False
        if job_result == RESULT_OK:
            job_result_ok = not stats or \
                            not stats.get('updated') \
                            and not stats.get('added') \
                            or stats.get('errored')
            if job_result_ok:
                return False
            else:
                return True


def _job_run_test(harvest_source_info, job_run):
    if job_run == RESULT_ALL:
        return True
    job = harvest_source_info.get('job')
    if job:
        if job.last_job.get('status') == job_run:
            return True
        stats = job.last_job.get('stats')
        if job_run == 'Current' and stats.get(None):
            return True
    return False


def _get_source_type_options(harvest_source_list):
    source_types = set([info.get('source').type
                        for info in harvest_source_list])
    source_type_options = [{'text': _('Source Type: all'), 'value': RESULT_ALL}]
    source_type_options.extend([{'text': type, 'value': type}
                                for type in source_types])
    return source_type_options
