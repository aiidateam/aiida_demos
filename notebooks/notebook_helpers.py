def get_code_options(plugin_classes):
    """
    Return AiiDA codes using a specific set of plugins
    
    :param plugin_classes: a dictionary of the type
      {'pw': 'quantumespresso.pw', 'ph': 'quantumespresso.ph'}
      where the key is a label and the value is the plugin to check for.
      It will return the set of codes that exist on the same machine.
    """
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import Code, Computer
    from aiida.backends.utils import get_automatic_user
    
    current_user = get_automatic_user()
    
    qb = QueryBuilder()
    qb.append(Computer,
          filters={'enabled': True},
          project=['*'], tag='computer')
    ordered_tags = []
    for tag, plugin_class in plugin_classes.iteritems():
        ordered_tags.append(tag)
        qb.append(Code,
          filters={'attributes.input_plugin': {'==': plugin_class},
                   'extras.hidden': {"~==": True}
            },
            project='label', tag='{}code'.format(tag), has_computer='computer')
    all_results = qb.all()
    # Filter in python only the ones that are actually user_configured
    # codeset[0] is the computer
    # codeset[1:] are the various code names, depending on the ones asked in input
    return [{tag: "{}@{}".format(codename, codeset[0].name) for codename, tag in zip(codeset[1:], ordered_tags)} 
            for codeset in all_results 
            if codeset[0].is_user_configured(current_user) and codeset[0].is_user_enabled(current_user)]

def get_code_pwonly_dropdown():
    """
    This function returns a group containing a dropdown list to select a
    valid available Quantum ESPRESSO pw.x code.

    To use it::

      code_group = get_code_pwonly_dropdown()


    You can later retrieve the value as follows::
   
      from IPython.display import display
      code_group = get_code_pwonly_dropdown()
      display(code_group)

    If this is None, then no code was found.
    Otherwise it will be a dictionary, where the only available key
    is 'pw' and the value is the code name, so you can get the code as::

       code_name = code_names['pw']
       code = Code.get_from_string(code_name)
    """
    import ipywidgets as ipw

    code_options_full = None
    in_codename = ipw.Dropdown(options=[], disabled=True)

    code_options_full = get_code_options(plugin_classes={
        'pw': 'quantumespresso.pw'})
    code_strings = ["{}".format(code_option['pw']) 
        for code_option in code_options_full]  
        
    if code_options_full is None:
        in_codename.options=[["Error while retrieving the list of codes", None]]
        in_codename.disabled=True
        in_codename.value = None
    elif not code_options_full:
        in_codename.options = [["No AiiDA codes configured yet", None]]
        in_codename.disabled = True
        in_codename.value = None
    else:
        code_options = zip(code_strings, code_options_full)
        in_codename.options=code_options
        in_codename.disabled = False
        # Set default value (first entry)
        in_codename.value = code_options[0][1]    
                
    code_group = ipw.HBox(
        [
            ipw.Label(value="Select a quantum code to use: "), 
            in_codename,
        ])

    return code_group

