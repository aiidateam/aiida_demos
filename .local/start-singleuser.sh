#!/bin/bash -e

# This script is executed whenever the docker container is (re)started.
export AIIDA_HOME=$HOME
export SCRIPTS=${HOME}/.local

#===============================================================================
# debugging
set -x

#===============================================================================
# start postgresql
source ${SCRIPTS}/postgres.sh
psql_start

#===============================================================================
# environment
export PYTHONPATH=${AIIDA_HOME}
export SHELL=/bin/bash

#===============================================================================
# setup AiiDA
aiida_backend=django

if [ ! -d ${AIIDA_HOME}/.aiida ]; then
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
      --repo ${AIIDA_HOME}/aiida_repository \
      default

   verdi profile setdefault verdi default
   verdi profile setdefault daemon default
   bash -c 'echo -e "y\nsome.body@xyz.com" | verdi daemon configureuser'

   # increase logging level
   #verdi devel setproperty logging.celery_loglevel DEBUG
   #verdi devel setproperty logging.aiida_loglevel DEBUG

   # start the daemon verdi daemon start

else
    if [ $aiida_backend = "django" ]; then
        verdi daemon stop || true
        echo "yes" | python /srv/conda/envs/kernel/lib/python2.7/site-packages/aiida/backends/djsite/manage.py --aiida-profile=default migrate
        verdi daemon start
    fi
fi

#===============================================================================
# setup AiiDA jupyter extension
if [ ! -e ${AIIDA_HOME}/.ipython/profile_default/ipython_config.py ]; then
   mkdir -p ${AIIDA_HOME}/.ipython/profile_default/
   echo > ${AIIDA_HOME}/.ipython/profile_default/ipython_config.py <<EOF
c = get_config()
c.InteractiveShellApp.extensions = [
   'aiida.common.ipython.ipython_magics'
]
EOF
fi

#===============================================================================
# create bashrc
if [ ! -e ${AIIDA_HOME}/.bashrc ]; then
   cp -v /etc/skel/.bashrc /etc/skel/.bash_logout /etc/skel/.profile ${AIIDA_HOME}/
   echo 'eval "$(verdi completioncommand)"' >> ${AIIDA_HOME}/.bashrc
   echo 'export PYTHONPATH="${AIIDA_HOME}"' >> ${AIIDA_HOME}/.bashrc
fi

# update the list of installed plugins
grep "reentry scan" ${AIIDA_HOME}/.bashrc || echo "reentry scan" >> ${AIIDA_HOME}/.bashrc

#===============================================================================
# install/upgrade apps
if [ ! -e ${AIIDA_HOME}/apps ]; then
   mkdir ${AIIDA_HOME}/apps
   touch ${AIIDA_HOME}/apps/__init__.py
   git clone https://github.com/materialscloud-org/mc-home ${AIIDA_HOME}/apps/home

   # make aiida demos discoverable by home app
   ln -s ${AIIDA_HOME} ${AIIDA_HOME}/apps/aiida_demos
fi

##===============================================================================
##start Jupyter notebook server
#cd ${AIIDA_HOME}
#${SCRIPTS}/matcloud-jupyterhub-singleuser                              \
#  --ip=0.0.0.0                                                   \
#  --port=8888                                                    \
#  --notebook-dir="${AIIDA_HOME}"                                      \
#  --NotebookApp.iopub_data_rate_limit=1000000000                 \
#  --NotebookApp.default_url="/apps/apps/home/start.ipynb"
#
##===============================================================================
#
##EOF
