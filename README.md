[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/aiidateam/aiida_demos/master/?urlpath=apps/apps/home/start.ipynb)
# aiida_demos
A repository of jupyter notebooks containing examples, tutorials and demos of AiiDA.

## Installation

No installation needed - just click "launch binder"!

If you *prefer* to run the AiiDA demos on your computer,
see the [AiiDA documentation](https://aiida-core.readthedocs.io/en/stable/)
for instructions to install AiiDA. 

Then:
```bash
pip install aiida-quantumespresso
git clone https://github.com/aiidateam/aiida_demos
cd aiida_demos/notebooks
jupyter notebook
```
A Jupyter tab should open in your browser from which you can select the notebook you want to run.

If Jupyter does not open automatically, point your browser to http://localhost:8888/tree/

## Building the binder image locally (for development)

```
pip install jupyter-repo2docker
git clone https://github.com/aiidateam/aiida_demos
repo2docker aiida_demos
```

In order to enter directly into app-mode, use the URL
`http://127.0.0.1:<port>/apps/apps/home/start.ipynb`
