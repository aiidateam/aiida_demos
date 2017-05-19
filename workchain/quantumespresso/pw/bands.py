# -*- coding: utf-8 -*-
from aiida.orm import CalculationFactory, DataFactory, Code
from aiida.orm.data.base import Bool, Float, Int, Str
from aiida.work.run import submit, async
from aiida.work.workfunction import workfunction
from aiida.work.workchain import WorkChain, ToContext, if_, while_, Outputs
from aiida.common.links import LinkType
from aiida.common.datastructures import calc_states
from seekpath.aiidawrappers import get_path, get_explicit_k_path
from aiida.workflows.user.workchain.quantumespresso.pw.base import PwBaseWorkChain

UpfData = DataFactory('upf')
KpointsData = DataFactory('array.kpoints')
ParameterData = DataFactory('parameter')
StructureData = DataFactory('structure')
PwCalculation = CalculationFactory('quantumespresso.pw')

class PwBandsWorkChain(WorkChain):
    """
    Workchain to relax and compute the band structure for a given input structure
    using Quantum Espresso's pw.x
    """
    def __init__(self, *args, **kwargs):
        super(PwBandsWorkChain, self).__init__(*args, **kwargs)

    @classmethod
    def define(cls, spec):
        super(PwBandsWorkChain, cls).define(spec)
        spec.input('codename', valid_type=Str)
        spec.input('structure', valid_type=StructureData)
        spec.input('protocol', valid_type=Str, default=Str('standard'))
        spec.outline(
            cls.setup_protocol,
            cls.setup_structure,
            cls.setup_kpoints,
            cls.setup_pseudo_potentials,
            cls.setup_parameters,
            cls.run_relax,
            cls.run_seekpath,
            cls.run_scf,
            cls.run_bands,
            cls.run_results,
        )
        spec.dynamic_output()

    def setup_protocol(self):
        """
        Setup of context variables and inputs for the PwBaseWorkChains. Based on the specified
        protocol, we define values for variables that affect the execution of the calculations
        """
        self.ctx.inputs = {
            'codename': self.inputs.codename,
            'parameters': {},
            'settings': {},
            'options': ParameterData(dict={
                'resources': {
                    'num_machines': 1
                },
                'max_wallclock_seconds': 1800,
            }),
        }

        if self.inputs.protocol == 'standard':
            self.report('running the workchain in the "{}" protocol'.format(self.inputs.protocol.value))
            self.ctx.protocol = {
                'kpoints_mesh_offset': [0., 0., 0.],
                'kpoints_mesh_density': 0.2,
                'convergence_threshold': 2.E-06,
                'smearing': 'marzari-vanderbilt',
                'degauss': 0.02,
                'occupations': 'smearing',
                'tstress': True,
                'pseudo_familyname': 'SSSP',
                'pseudo_data': {
                    'H':  {'cutoff': 55,  'dual': 8,  'pseudo': '031US'},
                    'He': {'cutoff': 55,  'dual': 4,  'pseudo': 'SG15'},
                    'Li': {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.4'},
                    'Be': {'cutoff': 40,  'dual': 8,  'pseudo': 'GBRV-1.4'},
                    'B':  {'cutoff': 40,  'dual': 8,  'pseudo': '031PAW'},
                    'C':  {'cutoff': 50,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'N':  {'cutoff': 55,  'dual': 8,  'pseudo': 'THEOS'},
                    'O':  {'cutoff': 45,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'F':  {'cutoff': 50,  'dual': 8,  'pseudo': 'GBRV-1.4'},
                    'Ne': {'cutoff': 200, 'dual': 8,  'pseudo': '100PAW'},
                    'Na': {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Mg': {'cutoff': 35,  'dual': 8,  'pseudo': 'GBRV-1.4'},
                    'Al': {'cutoff': 30,  'dual': 8,  'pseudo': '100PAW'},
                    'Si': {'cutoff': 30,  'dual': 8,  'pseudo': '100US'},
                    'P':  {'cutoff': 30,  'dual': 8,  'pseudo': '100US'},
                    'S':  {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Cl': {'cutoff': 35,  'dual': 8,  'pseudo': 'GBRV-1.4'},
                    'Ar': {'cutoff': 120, 'dual': 8,  'pseudo': '100US'},
                    'K':  {'cutoff': 50,  'dual': 8,  'pseudo': '100US'},
                    'Ca': {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Sc': {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Ti': {'cutoff': 35,  'dual': 8,  'pseudo': 'GBRV-1.4'},
                    'V':  {'cutoff': 40,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Cr': {'cutoff': 40,  'dual': 8,  'pseudo': 'GBRV-1.5'},
                    'Mn': {'cutoff': 70,  'dual': 12, 'pseudo': '031PAW'},
                    'Fe': {'cutoff': 90,  'dual': 12, 'pseudo': '031PAW'},
                    'Co': {'cutoff': 55,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Ni': {'cutoff': 45,  'dual': 8,  'pseudo': 'GBRV-1.4'},
                    'Cu': {'cutoff': 40,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Zn': {'cutoff': 40,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Ga': {'cutoff': 35,  'dual': 8,  'pseudo': '031US'},
                    'Ge': {'cutoff': 40,  'dual': 8,  'pseudo': '100PAW'},
                    'As': {'cutoff': 30,  'dual': 8,  'pseudo': '031US'},
                    'Se': {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Br': {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.4'},
                    'Kr': {'cutoff': 100, 'dual': 8,  'pseudo': '031US'},
                    'Rb': {'cutoff': 50,  'dual': 4,  'pseudo': 'SG15'},
                    'Sr': {'cutoff': 35,  'dual': 8,  'pseudo': '100US'},
                    'Y':  {'cutoff': 35,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Zr': {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Nb': {'cutoff': 35,  'dual': 8,  'pseudo': '031PAW'},
                    'Mo': {'cutoff': 35,  'dual': 4,  'pseudo': 'SG15'},
                    'Tc': {'cutoff': 30,  'dual': 4,  'pseudo': 'SG15'},
                    'Ru': {'cutoff': 40,  'dual': 4,  'pseudo': 'SG15'},
                    'Rh': {'cutoff': 45,  'dual': 8,  'pseudo': '100PAW'},
                    'Pd': {'cutoff': 55,  'dual': 8,  'pseudo': '100PAW'},
                    'Ag': {'cutoff': 35,  'dual': 8,  'pseudo': 'GBRV-1.4'},
                    'Cd': {'cutoff': 40,  'dual': 8,  'pseudo': '031US'},
                    'In': {'cutoff': 35,  'dual': 8,  'pseudo': '031US'},
                    'Sn': {'cutoff': 35,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Sb': {'cutoff': 40,  'dual': 8,  'pseudo': 'GBRV-1.4'},
                    'Te': {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'I':  {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Xe': {'cutoff': 120, 'dual': 8,  'pseudo': '100US'},
                    'Cs': {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Ba': {'cutoff': 40,  'dual': 4,  'pseudo': 'SG15'},
                    'Hf': {'cutoff': 35,  'dual': 8,  'pseudo': '031US'},
                    'Ta': {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'W':  {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Re': {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Os': {'cutoff': 35,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Ir': {'cutoff': 40,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Pt': {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.4'},
                    'Au': {'cutoff': 45,  'dual': 4,  'pseudo': 'SG15'},
                    'Hg': {'cutoff': 30,  'dual': 8,  'pseudo': 'GBRV-1.2'},
                    'Tl': {'cutoff': 30,  'dual': 8,  'pseudo': '031US'},
                    'Pb': {'cutoff': 40,  'dual': 8,  'pseudo': '031PAW'},
                    'Bi': {'cutoff': 35,  'dual': 8,  'pseudo': '031PAW'},
                    'Po': {'cutoff': 45,  'dual': 8,  'pseudo': '100US'},
                    'Rn': {'cutoff': 45,  'dual': 8,  'pseudo': '100US'},
                    'La': {'cutoff': 55,  'dual': 8,  'pseudo': 'Wentzcovitch'},
                    'Ce': {'cutoff': 45,  'dual': 8,  'pseudo': 'Wentzcovitch'},
                    'Pr': {'cutoff': 50,  'dual': 8,  'pseudo': 'Wentzcovitch'},
                    'Nd': {'cutoff': 40,  'dual': 8,  'pseudo': 'Wentzcovitch'},
                    'Sm': {'cutoff': 40,  'dual': 8,  'pseudo': 'Wentzcovitch'},
                    'Eu': {'cutoff': 55,  'dual': 8,  'pseudo': 'Wentzcovitch'},
                    'Tb': {'cutoff': 40,  'dual': 8,  'pseudo': 'Wentzcovitch'},
                    'Dy': {'cutoff': 40,  'dual': 8,  'pseudo': 'Wentzcovitch'},
                    'Ho': {'cutoff': 40,  'dual': 8,  'pseudo': 'Wentzcovitch'},
                    'Er': {'cutoff': 40,  'dual': 8,  'pseudo': 'Wentzcovitch'},
                    'Tm': {'cutoff': 40,  'dual': 8,  'pseudo': 'Wentzcovitch'},
                    'Yb': {'cutoff': 40,  'dual': 8,  'pseudo': 'Wentzcovitch'},
                    'Lu': {'cutoff': 45,  'dual': 8,  'pseudo': 'Wentzcovitch'},
                }
            }

    def setup_structure(self):
        """
        We use SeeKPath to determine the primitive structure for the given input structure, if it
        wasn't yet the case.
        """
        seekpath_result = seekpath_structure(self.inputs.structure)
        self.ctx.structure_initial_primitive = seekpath_result['primitive_structure']

    def setup_kpoints(self):
        """
        Define the k-point mesh for the relax and scf calculations. Also get the k-point path for
        the bands calculation for the initial input structure from SeeKpath
        """
        kpoints_mesh = KpointsData()
        kpoints_mesh.set_cell_from_structure(self.inputs.structure)
        kpoints_mesh.set_kpoints_mesh_from_density(
            distance=self.ctx.protocol['kpoints_mesh_density'],
            offset=self.ctx.protocol['kpoints_mesh_offset']
        )

        self.ctx.kpoints_mesh = kpoints_mesh

    def setup_pseudo_potentials(self):
        """
        Based on the given input structure and the protocol, use the SSSP library to determine the
        optimal pseudo potentials for the different elements in the structure
        """
        structure = self.ctx.structure_initial_primitive
        pseudo_familyname = self.ctx.protocol['pseudo_familyname']
        self.ctx.inputs['pseudos'] = get_pseudos(structure, pseudo_familyname)

    def setup_parameters(self):
        """
        Setup the default input parameters required for a PwCalculation and the PwBaseWorkChain
        """
        structure = self.ctx.structure_initial_primitive
        ecutwfc = []
        ecutrho = []

        for kind in structure.get_kind_names():
            try:
                dual = self.ctx.protocol['pseudo_data'][kind]['dual']
                cutoff = self.ctx.protocol['pseudo_data'][kind]['cutoff']
                cutrho = dual * cutoff
                ecutwfc.append(cutoff)
                ecutrho.append(cutrho)
            except KeyError as exception:
                self.abort_nowait('failed to retrieve the cutoff or dual factor for {}'.format(kind))

        natoms = len(structure.sites)
        conv_thr = self.ctx.protocol['convergence_threshold'] * natoms

        self.ctx.inputs['parameters'] = {
            'CONTROL': {
                'restart_mode': 'from_scratch',
                'tstress': self.ctx.protocol['tstress'],
            },
            'SYSTEM': {
                'ecutwfc': max(ecutwfc),
                'ecutrho': max(ecutrho),
                'smearing': self.ctx.protocol['smearing'],
                'degauss': self.ctx.protocol['degauss'],
                'occupations': self.ctx.protocol['occupations'],
            },
            'ELECTRONS': {
                'conv_thr': conv_thr,
            }
        }

    def run_relax(self):
        """
        Run the PwBaseWorkChain in vc-relax mode to relax the input structure
        """
        inputs = dict(self.ctx.inputs)

        # Set the correct pw.x input parameters
        calculation_mode = 'vc-relax'
        inputs['parameters']['CONTROL']['calculation'] = calculation_mode

        # Final input preparation, wrapping dictionaries in ParameterData nodes
        inputs['kpoints'] = self.ctx.kpoints_mesh
        inputs['structure'] = self.ctx.structure_initial_primitive
        inputs['parameters'] = ParameterData(dict=inputs['parameters'])
        inputs['settings'] = ParameterData(dict=inputs['settings'])

        running = submit(PwBaseWorkChain, **inputs)

        self.report('launching PwBaseWorkChain<{}> in {} mode'.format(running.pid, calculation_mode))

        return ToContext(workchain_relax=running)

    def run_seekpath(self):
        """
        Run the relaxed structure through SeeKPath to get the new primitive structure, just in case
        the symmetry of the cell changed in the cell relaxation step
        """
        try:
            structure = self.ctx.workchain_relax.out.output_structure
        except:
            self.abort_nowait('failed to get the output structure from vc-relax run')
            return

        seekpath_result = seekpath_structure(structure)

        self.ctx.structure_relaxed_primitive = seekpath_result['primitive_structure']
        self.ctx.kpoints_path = seekpath_result['explicit_kpoints_path']

        self.out('final_relax_structure', seekpath_result['primitive_structure'])
        self.out('final_seekpath_parameters', seekpath_result['parameters'])

    def run_scf(self):
        """
        Run the PwBaseWorkChain in scf mode on the primitive cell of the relaxed input structure
        """
        inputs = dict(self.ctx.inputs)

        # Set the correct pw.x input parameters
        calculation_mode = 'scf'
        inputs['parameters']['CONTROL']['calculation'] = calculation_mode

        # Final input preparation, wrapping dictionaries in ParameterData nodes
        inputs['kpoints'] = self.ctx.kpoints_mesh
        inputs['structure'] = self.ctx.structure_relaxed_primitive
        inputs['parameters'] = ParameterData(dict=inputs['parameters'])
        inputs['settings'] = ParameterData(dict=inputs['settings'])

        running = submit(PwBaseWorkChain, **inputs)

        self.report('launching PwBaseWorkChain<{}> in {} mode'.format(running.pid, calculation_mode))

        return ToContext(workchain_scf=running)

    def run_bands(self):
        """
        Run the PwBaseWorkChain in bands mode on the primitive cell of the relaxed input structure
        """
        calculation_scf = self.ctx.workchain_scf.get_outputs(link_type=LinkType.CALL)[0]
        self.out('scf_parameters', calculation_scf.out.output_parameters)

        inputs = dict(self.ctx.inputs)

        # Set the correct pw.x input parameters
        restart_mode = 'restart'
        calculation_mode = 'bands'
        inputs['parameters']['CONTROL']['restart_mode'] = restart_mode
        inputs['parameters']['CONTROL']['calculation'] = calculation_mode
        inputs['settings']['also_bands'] = True

        # Final input preparation, wrapping dictionaries in ParameterData nodes
        inputs['parent_folder'] = self.ctx.workchain_scf.out.remote_folder
        inputs['kpoints'] = self.ctx.kpoints_path
        inputs['structure'] = self.ctx.structure_relaxed_primitive
        inputs['parameters'] = ParameterData(dict=inputs['parameters'])
        inputs['settings'] = ParameterData(dict=inputs['settings'])

        running = submit(PwBaseWorkChain, **inputs)

        self.report('launching PwBaseWorkChain<{}> in {} mode'.format(running.pid, calculation_mode))

        return ToContext(workchain_bands=running)

    def run_results(self):
        """
        Attach the relevant output nodes from the band calculation to the workchain outputs
        for convenience
        """
        calculation_band = self.ctx.workchain_bands.get_outputs(link_type=LinkType.CALL)[0]

        self.report('workchain succesfully completed'.format())
        self.out('band_parameters', calculation_band.out.output_parameters)
        self.out('bandstructure', calculation_band.out.output_band)


@workfunction
def seekpath_structure(structure):

    seekpath_info = get_path(structure)
    explicit_path = get_explicit_k_path(structure)

    primitive_structure = seekpath_info.pop('primitive_structure')
    conv_structure = seekpath_info.pop('conv_structure')
    parameters = ParameterData(dict=seekpath_info)

    result = {
        'parameters': parameters,
        'conv_structure': conv_structure,
        'primitive_structure': primitive_structure,
        'explicit_kpoints_path': explicit_path['explicit_kpoints'],
    }

    return result


def get_pseudos(structure, family_name):
    """
    Set the pseudo to use for all atomic kinds, picking pseudos from the
    family with name family_name.

    :param family_name: the name of the group containing the pseudos
    """
    from collections import defaultdict
    from aiida.orm.data.upf import get_pseudos_from_structure

    # A dict {kind_name: pseudo_object}
    kind_pseudo_dict = get_pseudos_from_structure(structure, family_name)

    # We have to group the species by pseudo, I use the pseudo PK
    # pseudo_dict will just map PK->pseudo_object
    pseudo_dict = {}
    # Will contain a list of all species of the pseudo with given PK
    pseudo_species = defaultdict(list)

    for kindname, pseudo in kind_pseudo_dict.iteritems():
        pseudo_dict[pseudo.pk] = pseudo
        pseudo_species[pseudo.pk].append(kindname)

    pseudos = {}
    for pseudo_pk in pseudo_dict:
        pseudo = pseudo_dict[pseudo_pk]
        kinds = pseudo_species[pseudo_pk]
        for kind in kinds:
            pseudos[kind] = pseudo

    return pseudos
