#!/bin/bash
set -e

echo "This is travis-build.bash..."

echo "Updating GPG keys..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
curl -L https://packagecloud.io/github/git-lfs/gpgkey | sudo apt-key add -
wget -qO - https://www.mongodb.org/static/pgp/server-3.2.asc | sudo apt-key add -

echo "Adding archive repository for postgres..."
sudo rm /etc/apt/sources.list.d/pgdg*
echo "deb https://apt-archive.postgresql.org/pub/repos/apt trusty-pgdg-archive main" | sudo tee -a /etc/apt/sources.list
echo "deb-src https://apt-archive.postgresql.org/pub/repos/apt trusty-pgdg-archive main" | sudo tee -a /etc/apt/sources.list

echo "Removing old repository for cassandra..."
sudo rm /etc/apt/sources.list.d/cassandra*

echo "Installing the packages that CKAN requires..."
sudo apt-get update -qq
sudo apt-get install solr-jetty libcommons-fileupload-java

echo "Installing CKAN and its Python dependencies..."
git clone https://github.com/ckan/ckan
cd ckan
if [ $CKANVERSION == 'master' ]
then
    echo "CKAN version: master"
else
    CKAN_TAG=$(git tag | grep ^ckan-$CKANVERSION | sort --version-sort | tail -n 1)
    git checkout $CKAN_TAG
    echo "CKAN version: ${CKAN_TAG#ckan-}"
fi

# install the recommended version of setuptools
if [ -f requirement-setuptools.txt ]
then
    echo "Updating setuptools..."
    pip install -r requirement-setuptools.txt
fi

python setup.py develop

pip install -r requirements.txt
pip install -r dev-requirements.txt
cd -

echo "Setting up Solr..."
printf "NO_START=0\nJETTY_HOST=127.0.0.1\nJETTY_PORT=8983\nJAVA_HOME=$JAVA_HOME" | sudo tee /etc/default/jetty
sudo cp ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
sudo service jetty restart

echo "Creating the PostgreSQL user and database..."
sudo -u postgres psql -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
sudo -u postgres psql -c 'CREATE DATABASE ckan_test WITH OWNER ckan_default;'

echo "Initialising the database..."
cd ckan
paster db init -c test-core.ini
cd -

echo "Installing ckanext-harvest and its requirements..."
git clone --depth 1 --branch v1.4.2 https://github.com/ckan/ckanext-harvest
cd ckanext-harvest
python setup.py develop
pip install -r pip-requirements.txt
paster harvester initdb -c ../ckan/test-core.ini
cd -

echo "Installing ckanext-harvester_dashboard..."
git clone https://github.com/opendata-swiss/ckanext-harvester_dashboard
python setup.py develop
pip install -r requirements.txt
pip install -r dev-requirements.txt
cd -

echo "travis-build.bash is done."
