import ipywidgets as ipw

def get_start_widget(appbase, jupbase, notebase):
    #http://fontawesome.io/icons/
    template = """
    <style>
    .CustomLiMarginAiiDADemos li{{
      margin-top: 10px;
    }}
    </style>
    <div style="line-height: 1.4;" class="CustomLiMarginAiiDADemos">
    <p style="margin-bottom: 10px;">
    This app contains a number of simple Jupyter notebooks that
    show and demo basic features of AiiDA.
    {need_sample_data}
    </p>
    <table>
    <tr>
        <th style="text-align:left">Basics</th>
        <th style="width:70px" rowspan=2></th>
        <th style="text-align:left">Querying the Database</th>
        <th style="width:70px" rowspan=2></th>
        <th style="text-align:left">Advanced features</th>
    <tr>
    <td valign="top"><ul>
    <li><a href="{notebase}/notebooks/retrieve_structure_from_external_db_COD.ipynb" target="_blank">Import a structure from the COD database</a> (2&nbsp;min)
    <li><a href="{notebase}/notebooks/submit_pw_calculation.ipynb" target="_blank">Submit a simple Quantum&nbsp;ESPRESSO pw.x calculation</a> (3&nbsp;min)
    <li><a href="{notebase}/notebooks/graph_visualisation.ipynb" target="_blank">Visualize the provenance graph</a> (2&nbsp;min)
    </ul></td>
    
    <td valign="top"><ul>
    <li><a href="{notebase}/notebooks/query_database_statistics.ipynb" target="_blank">Query and get statistics on nodes and links in the DB</a> (2&nbsp;min)
    <li><a href="{notebase}/notebooks/query_structures_from_code.ipynb" target="_blank">Query for Codes and Calculations</a> (2&nbsp;min)
    <li><a href="{notebase}/notebooks/query_screening_database.ipynb" target="_blank">Query the electronic and magnetic properties of perovskites with different DFT functionals</a> (3&nbsp;min)
    </ul></td>

    <td valign="top"><ul>
    <li><a href="{notebase}/notebooks/sssp_seekpath_demo.ipynb" target="_blank">Automatic band structures with the SSSP pseudopotentials and the seekpath k-paths</a> (5&nbsp;min)
    <li><a href="{notebase}/notebooks/equation_of_states_interactive.ipynb" target="_blank">Interactive workflow to compute an equation of state</a> (5&nbsp;min)
    <li><a href="{notebase}/notebooks/export_import.ipynb" target="_blank">Importing and exporting nodes between differen AiiDA profiles</a> (2&nbsp;min)
    </ul></td>

    </tr></table></div>
"""
    from aiida import is_dbenv_loaded, load_dbenv
    if not is_dbenv_loaded():
        load_dbenv()
    from aiida.orm import load_node
    from aiida.common.exceptions import NotExistent

    need_sample_data_template = """<div class="alert alert-box alert-warning">
    For most of them, you first need to <emph>import some sample data</emph>,
    that you can do <a href="{notebase}/notebooks/import_sample_data.ipynb">
    using this simple notebook</a>.</div>"""

    try:
        n = load_node('2bc836d1-02ee-4d5e-acc3-925f0878d767')
        need_sample_data = "" # No message to show
    except NotExistent:
        need_sample_data = need_sample_data_template # Show the warning
    
    
    html = template.format(appbase=appbase, jupbase=jupbase,
                           notebase=notebase, need_sample_data=need_sample_data)
    return ipw.HTML(html)
    
#EOF
