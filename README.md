[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/ltalirz/aiida_demos/master/?urlpath=apps/apps/home/start.ipynb)
# aiida_demos
A repository of jupyter notebooks containing examples, tutorials and demos of AiiDA.

To run a notebook:

```bash
cd /<path>/<to>/<aiida_demos>/notebooks
jupyter notebook
```

A Jupyter tab should open in your browser from which you can select the notebook you want to run.

If Jupyter does not open automatically, point your browser to http://localhost:8888/tree/

## Dependencies

The examples that use Quantum ESPRESSO rely on the `aiida-quantumespresso` plugin.
To install it run the following `pip` command:

    pip install aiida-quantumespresso

## Build locally

Testing locally
```
pip install repo2docker
repo2docker .
```
In order to go directly to app-mode, use the URL
`http://127.0.0.1:<port>/apps/apps/home/start.ipynb`
