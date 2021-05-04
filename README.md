# Harvester Dashboard

Ckan extension that add a harvester dashboard that shows all the latest 
harvester jobs for the harvesters a user has access to

## Prerequisites

- ckanext-harvest needs to be installed

## Purpose
The extensions adds a named route: `harvester_dashboard` for displaying a harvester dashboard
The harvester dashboard displays the latest harvester job for all harvesters that a user 
is allowed to administer. (The user's adminstration rights are directly retrieved by 
check_access on 'harvest_source_update'.)

For each harvester job on the list links to the harvester-admin and the organization that 
the harvester belongs to are provided.

## Setup

- Add a tab on your `header.html` template to give access to the new route:

## Update translations

The extension is ready for adding translations, but so far no translations 
have been added.

