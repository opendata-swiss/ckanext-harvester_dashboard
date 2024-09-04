# coding=UTF-8

import logging
from collections import namedtuple, defaultdict
from ckan import model
import ckan.plugins.toolkit as tk
from ckanext.harvest.model import HarvestSource

HarvestSourceInfo = namedtuple('HarvestSourceInfo', ['organization'])
OrganizationInfo = namedtuple('OrganizationInfo', ['name', 'title'])
HarvestJobInfo = namedtuple('HarvestJobInfo', ['last_job'])
PackageInfo = namedtuple('PackageInfo', ['name'])

log = logging.getLogger(__name__)


def get_harvester_job_dict(context, data_dict, harvest_source_ids_for_user):
    """get latest harvest jobs for each harvest source
    the user has access to"""
    harvest_jobs = \
        tk.get_action('harvest_job_list')({'ignore_auth': True}, {})
    last_harvest_job_dict = defaultdict(lambda: None)
    for harvest_job in harvest_jobs:
        source_id = harvest_job['source_id']
        user_filter = source_id in harvest_source_ids_for_user
        job_not_set_filter = not last_harvest_job_dict.get(source_id)
        if user_filter and job_not_set_filter:
            last_harvest_job_id = harvest_job['id']
            harvest_job_result = \
                tk.get_action('harvest_job_show')({'ignore_auth': True},
                                                  {'id': last_harvest_job_id})
            last_harvest_job_dict[harvest_job['source_id']] = \
                HarvestJobInfo(last_job=harvest_job_result)
    return last_harvest_job_dict


def get_harvest_source_name_dict(harvest_source_ids):
    """get package names for harvest sources, so that
    urls to the harvesters can be added"""
    packages = \
        model.Session.query(model.Package)\
                     .filter(model.Package.id.in_(harvest_source_ids))\
                     .all()
    harvest_source_name_dict = \
        {package.id: PackageInfo(name=package.name)
         for package in packages}
    return harvest_source_name_dict


def get_organizations_for_harvest_sources(harvest_source_ids):
    """gets organizations for harvest_sources, so that it can be decided to
    which sources a user has access to"""
    members = \
        model.Session.query(model.Member) \
                     .filter(model.Member.capacity == 'organization') \
                     .filter(model.Member.state == 'active') \
                     .filter(model.Member.table_name == 'package') \
                     .filter(model.Member.table_id.in_(harvest_source_ids)) \
                     .all()
    harvest_source_org_dict = {}
    for member in members:
        harvest_source_org_dict[member.table_id] = member.group_id
    return harvest_source_org_dict


def get_harvest_source_dict():
    """gets all active harvest sources"""
    harvest_sources = model.Session.query(HarvestSource).filter(HarvestSource.active == True).all()  # noqa
    return {source.id: source for source in harvest_sources}


def get_organizations_id_dict():
    """get organizations with ids and title"""
    organizations = model.Session.query(model.Group)\
                                 .filter(model.Group.state == 'active')\
                                 .filter(model.Group.type == 'organization')\
                                 .all()
    organization_dict = {organization.id: OrganizationInfo(
        name=organization.name, title=organization.title)
                         for organization in organizations}
    return organization_dict


def get_harvest_source_ids_for_user(context, harvest_source_ids):
    """check for which harvest source the current user has admin rights"""
    harvest_source_ids_for_user = []
    for source_id in harvest_source_ids:
        log.debug("Processing a harvest source id: %s", source_id)
        model = context.get('model')
        pkg = model.Package.get(source_id)
        log.debug("Get package using a harvest source id: %s", pkg)

        try:
            tk.check_access('harvest_source_update',
                            context,
                            {'id': source_id})
            harvest_source_ids_for_user.append(source_id)
        except tk.NotAuthorized:
            pass
    return harvest_source_ids_for_user


def get_harvest_source_infos_for_user(context, data_dict):
    """get harvest source infos for display to a user
    """
    harvest_source_dict = get_harvest_source_dict()
    harvest_source_ids = harvest_source_dict.keys()
    harvest_source_name_dict = get_harvest_source_name_dict(harvest_source_ids)
    harvest_source_org_dict = \
        get_organizations_for_harvest_sources(harvest_source_ids)
    organization_dict = get_organizations_id_dict()

    harvest_source_ids_for_user = \
        get_harvest_source_ids_for_user(context,
                                        harvest_source_ids)

    harvest_sources_last_job_dict = \
        get_harvester_job_dict(context,
                               data_dict,
                               harvest_source_ids_for_user)

    harvest_source_infos = []
    for source_id, organization_id in harvest_source_org_dict.items():
        if source_id in harvest_source_ids_for_user:
            harvest_source_info = {
                'organization': organization_dict.get(organization_id),
                'source': harvest_source_dict.get(source_id),
                'job': harvest_sources_last_job_dict.get(source_id),
                'source_name': harvest_source_name_dict.get(source_id)
            }
            harvest_source_infos.append(harvest_source_info)
    return harvest_source_infos
