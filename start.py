import ipywidgets as ipw

def get_start_widget(appbase, jupbase, notebase):
    #http://fontawesome.io/icons/
    template = """
    <table>
    <tr>
        <th style="text-align:center">Basics</th>
        <th style="width:70px" rowspan=2></th>
        <th style="text-align:center">Querying the Database</th>
        <th style="width:70px" rowspan=2></th>
        <th style="text-align:center">Advanced features</th>
    <tr>
    <td valign="top"><ul>
    <li><a href="{notebase}/notebooks/retrieve_structure_from_external_db.ipynb" target="_blank">Load a structure (2 min)</a>
    <li><a href="{notebase}/notebooks/submit_pw_calculation.ipynb" target="_blank">Submit a calculation (3 min)</a>
    <li><a href="{notebase}/notebooks/graph_visualisation.ipynb" target="_blank">Visualize the provenance graph (2 min)</a>
    </ul></td>
    
    <td valign="top"><ul>
    <li><a href="{notebase}/notebooks/query_database_statistics.ipynb" target="_blank">Nodes and their links</a>
    <li><a href="{notebase}/notebooks/query_structures_from_code.ipynb" target="_blank">Codes and Calculations (2 min)</a>
    <li><a href="{notebase}/notebooks/query_screening_database.ipynb" target="_blank">Electronic properties of perovskites (3 min)</a>
    </ul></td>

    <td valign="top"><ul>
    <li><a href="{notebase}/notebooks/sssp_seekpath_demo.ipynb" target="_blank">Automatic band structures </a>
    <li><a href="{notebase}/notebooks/equation_of_states.ipynb" target="_blank">Equation of state workflow</a>
    <li><a href="{notebase}/notebooks/equation_of_states_interactive.ipynb" target="_blank">Interactive equation of state (5 min)</a>
    <li><a href="{notebase}/notebooks/export_import.ipynb" target="_blank">Importing and Exporting Nodes (2 min)</a>
    </ul></td>

    </tr></table>
"""
    
    html = template.format(appbase=appbase, jupbase=jupbase, notebase=notebase)
    return ipw.HTML(html)
    
#EOF
