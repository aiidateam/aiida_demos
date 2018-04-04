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
    <li><a href="{jupbase}/notebooks/retrieve_structure_from_external_db.ipynb" target="_blank">Load a structure</a>
    <li><a href="{jupbase}/notebooks/submit_pw_calculation.ipynb" target="_blank">Submit a calculation</a>
    <li><a href="{jupbase}/notebooks/graph_visualization.ipynb" target="_blank">Visualize the provenance graph</a>
    </ul></td>
    
    <td valign="top"><ul>
    <li><a href="{jupbase}/notebooks/query_database_statistics.ipynb" target="_blank">Nodes and their links</a>
    <li><a href="{jupbase}/notebooks/query_structures_from_code.ipynb" target="_blank">Codes and Calculations</a>
    <li><a href="{jupbase}/notebooks/query_screening_database.ipynb" target="_blank">Electronic properties of perovskites</a>
    </ul></td>

    <td valign="top"><ul>
    <li><a href="{jupbase}/notebooks/sssp_seekpath_demo.ipynb" target="_blank">Automatic band structures</a>
    <li><a href="{jupbase}/notebooks/equation_of_states.ipynb" target="_blank">Equation of state workflow</a>
    <li><a href="{jupbase}/notebooks/equation_of_states_interactive.ipynb" target="_blank">Interactive equation of state</a>
    <li><a href="{jupbase}/notebooks/export_import.ipynb" target="_blank">Importing and Exporting Nodes</a>
    </ul></td>

    </tr></table>
"""
    
    html = template.format(appbase=appbase, jupbase=jupbase, notebase=notebase)
    return ipw.HTML(html)
    
#EOF
