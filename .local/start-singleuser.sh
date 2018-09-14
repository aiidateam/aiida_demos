#!/bin/bash -e
# This script is executed whenever the docker container is (re)started.

#===============================================================================
# set aiidalab variables
export AIIDALAB_HOME=$HOME
export AIIDALAB_APPS=$HOME/apps
export AIIDALAB_SCRIPTS=${HOME}/.local

#===============================================================================
# debugging
set -x

#===============================================================================
# start postgresql
source ${AIIDALAB_SCRIPTS}/postgres.sh
psql_start

#===============================================================================
# environment
export PYTHONPATH=${AIIDALAB_HOME}
export SHELL=/bin/bash

#===============================================================================
# setup AiiDA
aiida_backend=django

if [ ! -d ${AIIDALAB_HOME}/.aiida ]; then
   verdi setup                          \
      --non-interactive                 \
      --email some.body@xyz.com         \
      --first-name Some                 \
      --last-name Body                  \
      --institution XYZ                 \
      --backend $aiida_backend          \
      --db_user aiida                   \
      --db_pass aiida_db_passwd         \
      --db_name aiidadb                 \
      --db_host localhost               \
      --db_port 5432                    \
      --repo ${AIIDALAB_HOME}/.aiida/repository-default \
      default

   verdi profile setdefault verdi default
   verdi profile setdefault daemon default
   bash -c 'echo -e "y\nsome.body@xyz.com" | verdi daemon configureuser'

   # increase logging level
   #verdi devel setproperty logging.celery_loglevel DEBUG
   #verdi devel setproperty logging.aiida_loglevel DEBUG

   # start the daemon
   verdi daemon start

else
    if [ $aiida_backend = "django" ]; then
        verdi daemon stop || true
        echo "yes" | python /usr/local/lib/python2.7/dist-packages/aiida/backends/djsite/manage.py --aiida-profile=default migrate
        verdi daemon start
    fi
fi

#===============================================================================
# setup AiiDA jupyter extension
if [ ! -e ${AIIDALAB_HOME}/.ipython/profile_default/ipython_config.py ]; then
   mkdir -p ${AIIDALAB_HOME}/.ipython/profile_default/
   echo > ${AIIDALAB_HOME}/.ipython/profile_default/ipython_config.py <<EOF
c = get_config()
c.InteractiveShellApp.extensions = [
   'aiida.common.ipython.ipython_magics'
]
EOF
fi

#===============================================================================
# create bashrc
if [ ! -e ${AIIDALAB_HOME}/.bashrc ]; then
   cp -v /etc/skel/.bashrc /etc/skel/.bash_logout /etc/skel/.profile ${AIIDALAB_HOME}/
   echo 'eval "$(verdi completioncommand)"' >> ${AIIDALAB_HOME}/.bashrc
   echo 'export PYTHONPATH="${AIIDALAB_HOME}"' >> ${AIIDALAB_HOME}/.bashrc
fi

# update the list of installed plugins
grep "reentry scan" ${AIIDALAB_HOME}/.bashrc || echo "reentry scan" >> ${AIIDALAB_HOME}/.bashrc

#===============================================================================
# install/upgrade apps
if [ ! -e ${AIIDALAB_APPS} ]; then
   mkdir ${AIIDALAB_APPS}
   touch ${AIIDALAB_APPS}/__init__.py
   git clone https://github.com/materialscloud-org/mc-home ${AIIDALAB_APPS}/home

fi

##EOF
