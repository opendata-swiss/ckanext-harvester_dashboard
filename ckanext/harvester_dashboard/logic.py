# coding=UTF-8

import logging
from collections import namedtuple, defaultdict
from ckan import authz, model
import ckan.plugins.toolkit as tk
from ckanext.harvest.model import HarvestJob, HarvestSource

HarvestSourceInfo = namedtuple('HarvestSourceInfo', ['organization'])
OrganizationInfo = namedtuple('OrganizationInfo', ['name', 'title'])
HarvestJobInfo = namedtuple('HarvestJobInfo', ['last_job'])
PackageInfo = namedtuple('PackageInfo', ['name'])

log = logging.getLogger(__name__)


def get_harvester_job_dict(context, data_dict, harvest_source_ids_for_user):
    """get latest harvest jobs for each harvest source the user has access to"""
    harvest_jobs = tk.get_action('harvest_job_list')( {'ignore_auth': True}, {})
    last_harvest_job_dict = defaultdict(lambda:None)
    for harvest_job in harvest_jobs:
        source_id = harvest_job['source_id']
        user_filter = source_id in harvest_source_ids_for_user
        job_not_set_filter = not last_harvest_job_dict.get(source_id)
        if user_filter and job_not_set_filter:
            last_harvest_job_dict[harvest_job['source_id']] = HarvestJobInfo(
                last_job=harvest_job
            )
    return last_harvest_job_dict


def get_harvest_source_name_dict(harvest_source_ids):
    """get package names for harvest sources, so that urls to the harvesters can be added"""
    packages = model.Session.query(model.Package)\
                            .filter(model.Package.id.in_(harvest_source_ids))\
                            .all()  # noqa
    harvest_source_name_dict = {package.id: PackageInfo(name=package.name)  # noqa
                                for package in packages}
    return harvest_source_name_dict


def get_organizations_for_harvest_sources(harvest_source_ids):
    """gets organizations for harvest_sources, so that it can be decided to
    which sources a user has access to"""
    members = model.Session.query(model.Member) \
                           .filter(model.Member.capacity == 'organization')\
                           .filter(model.Member.table_name == 'package') \
                           .filter(model.Member.table_id.in_(harvest_source_ids))\
                           .all()  # noqa
    harvest_source_org_dict = {}
    for member in members:
        harvest_source_org_dict[member.table_id] = member.group_id
    return harvest_source_org_dict


def get_harvest_source_dict():
    """gets all active harvest sources"""
    harvest_sources = model.Session.query(HarvestSource).filter(HarvestSource.active == True).all()  # noqa
    return {source.id: source for source in harvest_sources}


def get_harvest_organizations_for_user(context, data_dict):
    """gets all organizations where user can administer the harvesters"""
    organizations_for_user = tk.get_action('organization_list_for_user')(context, data_dict)  # noqa
    organization_dict_by_id = {}
    for organization in organizations_for_user:
        if organization.get('capacity') in ['admin', 'editor']:
            organization_dict_by_id[organization['id']] = {
                'name': organization['name'],
                'title': organization['title']
            }
    return organization_dict_by_id


def get_harvest_source_infos_for_user(context, data_dict):
    """get harvest source infos for display to a user
    """
    harvest_source_dict = get_harvest_source_dict()
    harvest_source_ids = harvest_source_dict.keys()
    harvest_source_name_dict = get_harvest_source_name_dict(harvest_source_ids)
    harvest_source_org_dict = get_organizations_for_harvest_sources(harvest_source_ids)

    harvest_organizations_for_user_as_dict = get_harvest_organizations_for_user(context, data_dict)
    organization_ids_for_user = harvest_organizations_for_user_as_dict.keys()
    harvest_source_ids_for_user = [source_id for source_id in harvest_source_ids
                                   if harvest_source_org_dict[source_id] in organization_ids_for_user]
    harvest_sources_last_job_dict = get_harvester_job_dict(context, data_dict, harvest_source_ids_for_user)

    harvest_source_infos = []
    for source_id, organization_id in harvest_source_org_dict.items():
        if source_id in harvest_source_ids_for_user:
            harvest_source_info = {
                'organization': harvest_organizations_for_user_as_dict.get(organization_id),
                'source': harvest_source_dict.get(source_id),
                'job': harvest_sources_last_job_dict.get(source_id),
                'source_name' : harvest_source_name_dict.get(source_id)
            }
            harvest_source_infos.append(harvest_source_info)
    return harvest_source_infos
