#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

import argparse
from aiida.orm import CalculationFactory, DataFactory
from aiida.orm.code import Code
from aiida.orm.data.base import Int, Float, Str
from aiida.orm.data.upf import UpfData
from aiida.orm.data.structure import StructureData
from aiida.common.exceptions import NotExistent
from aiida.work.run import run, async, submit
from aiida.work.workchain import WorkChain, ToContext, while_, Outputs

from common.structure.generate import create_diamond_fcc, scale_structure
from common.pseudo.qe import get_pseudos

KpointsData = DataFactory("array.kpoints")
ParameterData = DataFactory('parameter')
PwCalculation = CalculationFactory('quantumespresso.pw')

def parser_setup():
    """
    Setup the parser of command line arguments and return it. This is separated from the main
    execution body to allow tests to effectively mock the setup of the parser and the command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Run an AiiDA workchain to compute the equation of state of a simple diamond structure',
    )
    parser.add_argument(
        '-c', type=str, required=True, dest='codename',
        help='the name of the AiiDA code that references QE pw.x'
    )
    parser.add_argument(
        '-p', type=str, required=True, dest='pseudo_family',
        help='the name of the AiiDA pseudo family'
    )
    parser.add_argument(
        '-e', type=str, default='C', dest='element',
        help='the element for which the fcc diamond structure is to be constructed (default: %(default)s)'
    )
    parser.add_argument(
        '-a', type=float, default=3.65, dest='alat',
        help='the lattice parameter of the fcc diamond structure in Angstrom (default: %(default).2f)'
    )
    parser.add_argument(
        '-n', type=int, default=5, dest='npoints',
        help='the number of calculations to compute. Scaling factors will be generated automatically in steps of 0.02 (default: %(default)d)'
    )

    return parser


class EquationOfState(WorkChain):
    """
    Workchain that for a given structure will compute the equation of state by
    computing the total energy for a set of derived structures with a scaled
    lattice parameter
    """

    @classmethod
    def define(cls, spec):
        super(EquationOfState, cls).define(spec)
        spec.input("structure", valid_type=StructureData)
        spec.input("codename", valid_type=Str)
        spec.input("pseudo_family", valid_type=Str)
        spec.input("npoints", valid_type=Int)
        spec.outline(
            cls.init,
            while_(cls.should_run_pw)(
                cls.run_pw,
                cls.parse_pw,
            ),
            cls.return_result,
        )
        spec.dynamic_output()

    def init(self):
        """
        Initialize variables and the scales we want to compute
        """
        kpoints = KpointsData()
        kpoints.set_kpoints_mesh([2, 2, 2])

        npoints = self.inputs.npoints.value
        self.ctx.i = 0
        self.ctx.scales = sorted([1 - pow(-1, x)*0.02*int((x+1)/2) for x in range(npoints)])
        self.ctx.result = []
        self.ctx.options = {
            "resources": {
                "num_machines": 1,
                "tot_num_mpiprocs": 1,
            },
            "max_wallclock_seconds": 30 * 60,
        }
        self.ctx.parameters = {
            "CONTROL": {
                "calculation": "scf",
                "tstress": True,
                "tprnfor": True,
            },
            "SYSTEM": {
                "ecutwfc": 30.,
                "ecutrho": 200.,
            },
            "ELECTRONS": {
                "conv_thr": 1.e-6,
            }
        }
        self.ctx.kpoints = kpoints
        self.ctx.pseudos = get_pseudos(self.inputs.structure, self.inputs.pseudo_family.value)

    def should_run_pw(self):
        """
        Determine whether a calculation should still be run
        """
        return self.ctx.i < len(self.ctx.scales)

    def run_pw(self):
        """
        Run a PwCalculation for the current scaling factor
        """
        scale = self.ctx.scales[self.ctx.i]
        structure = scale_structure(self.inputs.structure, Float(scale))
        self.ctx.i += 1

        # Create the input dictionary
        inputs = {
            'code'       : Code.get_from_string(self.inputs.codename.value),
            'pseudo'     : self.ctx.pseudos,
            'kpoints'    : self.ctx.kpoints,
            'structure'  : structure,
            'parameters' : ParameterData(dict=self.ctx.parameters),
            '_options'   : self.ctx.options,
        }

        # Create the calculation process and launch it
        self.report("Running pw.x for the scale factor {}".format(scale))
        process = PwCalculation.process()
        future  = async(process, **inputs)

        return ToContext(pw=Outputs(future))

    def parse_pw(self):
        """
        Extract the volume and total energy of the last completed PwCalculation
        """
        volume = self.ctx.pw["output_parameters"].dict.volume
        energy = self.ctx.pw["output_parameters"].dict.energy
        self.ctx.result.append((volume, energy))

        return

    def return_result(self):
        """
        Attach the results of the PwCalculations and the initial structure to the outputs
        """
        result = {
            "initial_structure": self.inputs.structure,
            "result": ParameterData(dict={"eos": self.ctx.result}),
        }

        for link_name, node in result.iteritems():
            self.out(link_name, node)

        self.report("Workchain <{}> completed successfully".format(self.calc.pk))

        return


def execute(args):
    """
    The main execution of the script, which will run some preliminary checks on the command
    line arguments before passing them to the workchain and running it
    """
    try:
        code = Code.get_from_string(args.codename)
    except NotExistent as exception:
        print "Execution failed: could not retrieve the code '{}'".format(args.codename)
        print "Exception report: {}".format(exception)
        return

    try:
        pseudo_family = UpfData.get_upf_group(args.pseudo_family)
    except NotExistent as exception:
        print "Execution failed: could not retrieve the pseudo family '{}'".format(args.pseudo_family)
        print "Exception report: {}".format(exception)
        return

    try:
        structure = create_diamond_fcc(Str(args.element), Float(args.alat))
    except Exception as exception:
        print "Execution failed: failed to construct a structure for the given element '{}'".format(args.element)
        print "Exception report: {}".format(exception)
        return

    outputs = run(
        EquationOfState,
        npoints=Int(args.npoints),
        structure=structure,
        codename=Str(args.codename),
        pseudo_family=Str(args.pseudo_family)
    )

    return outputs["result"]


def main():
    """
    Setup the parser to retrieve the command line arguments and pass them to the main execution function.
    """
    parser = parser_setup()
    args   = parser.parse_args()
    result = execute(args)

    print "\nFinal results of the equation of state workchain:\n"
    print "{volume:12}  {energy:12}".format(volume="Volume (A^3)", energy="Energy (eV)")
    print "{}".format("-"*26)
    for p in result.get_dict()['eos']:
        print "{volume:>12.5f}  {energy:>12.5f}".format(volume=p[0], energy=p[1])


if __name__ == "__main__":
    main()