from aiida.backends.utils import load_dbenv, is_dbenv_loaded

if not is_dbenv_loaded():
    load_dbenv()
from aiida.orm import DataFactory

def create_diamond_fcc(element):
    """
    Workfunction to create a diamond crystal structure of a given element.
    At the moment only Si and Ge are valid elements (for C we miss the pseudo)
    :param element: The element to create the structure with.
    :return: The structure.
    """
    import numpy as np

    elem_alat= {
                'Si': 5.431, # Angstrom
                "Ge": 5.658,
               }

    # Validate input element
    symbol = str(element)
    if symbol not in elem_alat.keys():
       raise ValueError("Valid elements are only Si and Ge")

    # Create cel starting from a protopype with alat=1
    alat = elem_alat[symbol]
    the_cell = np.array([[0., 0.5, 0.5],
                         [0.5, 0., 0.5],
                         [0.5, 0.5, 0.]]) * alat
 
    # Create a structure data object
    StructureData = DataFactory("structure")
    structure = StructureData(cell=the_cell)
    structure.append_atom(position=(0., 0., 0.), symbols=str(element))
    structure.append_atom(position=(0.25*alat, 0.25*alat, 0.25*alat), symbols=str(element))
    return structure

def rescale(structure, scale):
    """
    Workfunction to rescale a structure

    :param structure: An AiiDA structure to rescale
    :param scale: The scale factor
    :return: The rescaled structure
    """
    the_ase = structure.get_ase()
    new_ase = the_ase.copy()
    new_ase.set_cell(the_ase.get_cell() * float(scale), scale_atoms=True)
    new_structure = DataFactory('structure')(ase=new_ase)
    return new_structure

