from create_rescale import create_diamond_fcc, rescale
from common_wf import generate_scf_input_params
from aiida.work import run, Process
from aiida.work import workfunction as wf
from aiida.orm.data.base import Str, Float
from aiida.orm import CalculationFactory, DataFactory

PwCalculation = CalculationFactory('quantumespresso.pw')

scale_facs = (0.96, 0.98, 1.0, 1.02, 1.04)
labels = ["c1", "c2", "c3", "c4", "c5"]

@wf
def run_eos_wf(codename, pseudo_family, element):
    print "Workfunction node identifiers: {}".format(Process.current().calc)
    #Instantiate a JobCalc process and create basic structure
    JobCalc = PwCalculation.process()
    s0 = create_diamond_fcc(Str(element))
    
    calcs = {}
    for label, factor in zip(labels, scale_facs):
        s = rescale(s0,Float(factor))
        inputs = generate_scf_input_params(s, str(codename), Str(pseudo_family))
        print "Running a scf for {} with scale factor {}".format(element, factor)
        result = run(JobCalc,**inputs)
        calcs[label] = get_info(result)

    eos = []
    for label in labels:
        eos.append(calcs[label])
    
    #Return information to plot the EOS
    ParameterData = DataFactory("parameter")
    retdict = {
            'initial_structure': s0,
            'result': ParameterData(dict={'eos_data': eos})
        }

    return retdict


def get_info(calc_results):
    return (calc_results['output_parameters'].dict.volume,
            calc_results['output_parameters'].dict.energy,
            calc_results['output_parameters'].dict.energy_units)

def run_eos(codename='pw-5.1@localhost', pseudo_family='GBRV_lda', element="Si"):
    return run_eos_wf(Str(codename), Str(pseudo_family), Str(element))

if __name__ == '__main__':
    run_eos()
