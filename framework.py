import benchmarks.benchmark_WATERS as automotiveBench
import benchmarks.benchmark_Uniform as uniformBench
from e2eAnalyses.Davare2007 import davare07, davare07_inter
from e2eAnalyses.Becker2017 import becker17_NO_INFORMATION, becker17_RESPONSE_TIMES, becker17_SCHED_TRACE, becker17_LET
from e2eAnalyses.Kloda2018 import kloda18
from e2eAnalyses.Duerr2019 import duerr19, duerr19_mrt, duerr19_mrda
from e2eAnalyses.Martinez2020 import martinez20_impl, martinez20_let
from e2eAnalyses.Hamann2017 import hamann17
from e2eAnalyses.Guenzel2023_inter import guenzel23_local_mrt, guenzel23_local_mda, guenzel23_local_mrda, guenzel23_inter_mrt, guenzel23_inter_mrda
from e2eAnalyses.Guenzel2023_mixed import guenzel23_mix_pessimistic, guenzel23_mix, guenzel23_mix_improved
from e2eAnalyses.Guenzel2023_equi import guenzel23_equi_mda, guenzel23_equi_mrt, guenzel23_equi_mrda, guenzel23_equi_mrrt
from e2eAnalyses.Bi2022 import bi22, bi22_inter
from e2eAnalyses.Kordon2020 import kordon20
from e2eAnalyses.Guenzel2023_equi_extension1 import guenzel23_equi_impl_sched
from e2eAnalyses.Guenzel2023_equi_extension2 import guenzel23_equi_impl_rt
from e2eAnalyses.BeckerFast import beckerFast_NO_INFORMATION, beckerFast_RESPONSE_TIMES, beckerFast_SCHED_TRACE, beckerFast_LET
from e2eAnalyses.Gohari2022 import gohari22
import helpers
import plotting.plot as plot
import random as random
from multiprocessing import Pool
from utilities.scheduler import compute_all_schedules
from utilities.yaml_export import export_to_yaml
import time as time


# debug output
print_elapsed_time = False


class AnalysisMethod:
    """Class for describing e2e analysis methods"""

    def __init__(self, analysis_function, name, name_short, features):
        self.analysis = analysis_function
        self.name = name
        self.name_short = name_short
        self.features = features
        self.latencies = []

    def reset(self):
        """Deletes the saved latencies"""

        self.latencies = []

    def normalize(self, baseline):
        """Normalizes the latencies of this analysis method to the
        latencies of the given analysis method
        """

        if len(self.latencies) != len(baseline.latencies):
            return []
        else:
            return [(b-a)/b for a,b in zip(self.latencies, baseline.latencies)]


########################################################
### Dictionary with all implemented analysis methods ###
########################################################

# dictionary the holds the definitions of all implemented analysis methods with their names and features
analysesDict = {
    # intern_name : AnalysisMethod(analysis_method, long_name (used in GUI), short_name (used in plots), feature list)
    'davare07' : AnalysisMethod(davare07, 'Davare 2007 (baseline)', 'D07', features=['periodic', 'implicit']),
    'davare07_inter' : AnalysisMethod(davare07_inter, 'Davare 2007 (inter)', 'D07-I', features=['periodic', 'implicit', 'inter']),
    'becker17_NO_INFORMATION' : AnalysisMethod(becker17_NO_INFORMATION, 'Becker 2017 (Base MRDA)', 'B17', features=['periodic', 'implicit']),
    'becker17_RESPONSE_TIMES' : AnalysisMethod(becker17_RESPONSE_TIMES, 'Becker 2017 (RT MRDA)', 'B17(RT)', features=['periodic', 'implicit']),
    'becker17_SCHED_TRACE' : AnalysisMethod(becker17_SCHED_TRACE, 'Becker 2017 (ST MRDA)', 'B17(ST)', features=['periodic', 'implicit', 'schedule']),
    'becker17_LET' : AnalysisMethod(becker17_LET, 'Becker 2017 (LET MRDA)', 'B17(LET)', features=['periodic', 'LET']),
    'beckerFast_NO_INFORMATION': AnalysisMethod(beckerFast_NO_INFORMATION, 'Becker 2017 Fast (Base MRDA)', 'B17F', features=['periodic', 'implicit']),
    'beckerFast_RESPONSE_TIMES': AnalysisMethod(beckerFast_RESPONSE_TIMES, 'Becker 2017 Fast (RT MRDA)', 'B17F-RT', features=['periodic', 'implicit']),
    'beckerFast_SCHED_TRACE': AnalysisMethod(beckerFast_SCHED_TRACE, 'Becker 2017 Fast (ST MRDA)', 'B17F-ST', features=['periodic', 'implicit', 'schedule']),
    'beckerFast_LET': AnalysisMethod(beckerFast_LET, 'Becker 2017 Fast (LET MRDA)', 'B17F-LET', features=['periodic', 'LET']),
    'hamann17' : AnalysisMethod(hamann17, 'Hamann 2017 (baseline)', 'H17', features=['periodic', 'sporadic', 'LET']),
    'kloda18' : AnalysisMethod(kloda18, 'Kloda 2018', 'K18', features=['periodic', 'implicit']),
    'duerr19_mrt' : AnalysisMethod(duerr19_mrt, 'Dürr 2019 (MRT)', 'D19(MRT)', features=['periodic', 'sporadic', 'implicit', 'inter']),
    'duerr19_mrda' : AnalysisMethod(duerr19_mrda, 'Dürr 2019 (MRDA)', 'D19(MRDA)', features=['periodic', 'sporadic', 'implicit', 'inter']),
    # 'martinez20_impl' : AnalysisMethod(martinez20_impl, 'Martinez 2020 (Impl)', 'M20(Impl)', features=['periodic', 'implicit']),                                                            # TODO
    # 'kordon20' : AnalysisMethod(kordon20, 'Kordon 2020', 'K20',features=['periodic', 'LET']),                                                                                               # TODO
    # 'martinez20_let' : AnalysisMethod(martinez20_let, 'Martinez 2020 (LET)', 'M20(LET)', features=['periodic', 'LET']),                                                                     # TODO
    'bi22' : AnalysisMethod(bi22, 'Bi 2022', 'B22', features=['periodic', 'implicit']),
    'bi22_inter' : AnalysisMethod(bi22_inter, 'Bi 2022 (inter)', 'B22(I)', features=['periodic', 'implicit', 'inter']),
    'gohari22' : AnalysisMethod(gohari22, 'Gohari 2022', 'G22', features=['periodic', 'implicit']),
    'guenzel23_local_mrt' : AnalysisMethod(guenzel23_local_mrt, 'Günzel 2023 (local MRT)', 'G23(L-MRT)', features=['periodic', 'implicit', 'schedule']),
    'guenzel23_local_mda' : AnalysisMethod(guenzel23_local_mda, 'Günzel 2023 (local MDA)', 'G23(L-MDA)', features=['periodic', 'implicit', 'schedule']),
    'guenzel23_local_mrda' : AnalysisMethod(guenzel23_local_mrda, 'Günzel 2023 (local MRDA)', 'G23(L-MRDA)', features=['periodic', 'implicit', 'schedule']),
    'guenzel23_inter_mrt' : AnalysisMethod(guenzel23_inter_mrt, 'Günzel 2023 (inter MRT)', 'G23(I-MRT)', features=['periodic', 'implicit', 'inter', 'schedule']),
    'guenzel23_inter_mrda' : AnalysisMethod(guenzel23_inter_mrda, 'Günzel 2023 (inter MRDA)', 'G23(I-MRDA)', features=['periodic', 'implicit', 'inter', 'schedule']),
    'guenzel23_mix_pessimistic' : AnalysisMethod(guenzel23_mix_pessimistic, 'Günzel 2023 (mixed, pessimistic)', 'G23(MIX-P)', features=['periodic', 'sporadic', 'implicit', 'LET', 'mixed']),
    'guenzel23_mix' : AnalysisMethod(guenzel23_mix, 'Günzel 2023 (mixed)', 'G23(MIX)', features=['periodic', 'sporadic', 'implicit', 'LET', 'mixed']),
    'guenzel23_mix_improved' : AnalysisMethod(guenzel23_mix_improved, 'Günzel 2023 (mixed improved)', 'G23(MIX-I)', features=['periodic', 'sporadic', 'implicit', 'LET', 'mixed']),
    'guenzel23_equi_mda': AnalysisMethod(guenzel23_equi_mda, 'Günzel 2023 (equi MDA)', 'G23(EQ-MDA)', features=['periodic', 'LET']),
    'guenzel23_equi_mrt': AnalysisMethod(guenzel23_equi_mrt, 'Günzel 2023 (equi MRT)', 'G23(EQ-MRT)', features=['periodic', 'LET']),
    'guenzel23_equi_mrda': AnalysisMethod(guenzel23_equi_mrda, 'Günzel 2023 (equi MRDA)', 'G23(EQ-MRDA)', features=['periodic', 'LET']),
    'guenzel23_equi_mrrt': AnalysisMethod(guenzel23_equi_mrrt, 'Günzel 2023 (equi MRRT)', 'G23(EQ-MRRT)', features=['periodic', 'LET']),
    'guenzel23_equi_impl_sched': AnalysisMethod(guenzel23_equi_impl_sched, 'Günzel 2023 (equi+sched MRT)', 'G23(EQ-SCHED)', features=['periodic', 'implicit', 'schedule']),
    'guenzel23_equi_impl_rt': AnalysisMethod(guenzel23_equi_impl_rt, 'Günzel 2023 (equi+rt MRT)', 'G23(EQ-RT)', features=['periodic', 'implicit']),
}


############################################################
### Configuration parameters of the evaluation framework ###
############################################################

# default parameters for general settings
default_general_params = {
    'generate_cecs' : False,
    'store_generated_cecs' : False,
    'load_cecs_from_file' : False,
    'cecs_file_path' : '',
    'yaml_file_path' : '',
    'number_of_threads' : 1,
    'debug_output' : False
}

# default parameters for taskset generation
default_taskset_generation_params = {
    'use_automotive_taskset_generation': False,
    'use_uniform_taskset_generation': False,

    'target_util': 0.5,
    'number_of_tasksets': 1,
    'sporadic_ratio': 0.0,
    'let_ratio': 0.0,
    'bcet_ratio': 1.0,

    'use_semi_harmonic_periods': False,
    'min_number_of_tasks': 40,
    'max_number_of_tasks': 60,
    'min_period': 1,
    'max_period': 2000
}

# default parameters for cec generation
default_cec_generation_params = {
    'generate_automotive_cecs': False,
    'generate_random_cecs': False,

    'min_number_of_chains': 30,
    'max_number_of_chains': 60,

    'min_number_of_tasks_in_chain': 2,
    'max_number_of_tasks_in_chain': 10,

    'generate_interconnected_cecs': False,
    'min_number_ecus': 2,
    'max_number_ecus': 5,
    'number_of_inter_cecs': 1000
}

# default parameters for output generation
default_output_params = {
    'normalized_plots' : False,
    'absolute_plots' : False,
    'raw_analysis_results' : False,
    'output_dir' : '',
    'print_to_console' : False
}


######################
### Input checking ###
######################

def check_params(taskset_params, cec_params, warnings=True):
    """Checks the given taskset and cause-effect chain parameters for
    logical errors, in case an error was found an exception is thrown
    """

    # taskset params check
    assert taskset_params['target_util'] >= 0.01
    assert taskset_params['target_util'] <= 0.99
    assert taskset_params['number_of_tasksets'] >= 0
    assert taskset_params['sporadic_ratio'] >= 0.00
    assert taskset_params['sporadic_ratio'] <= 1.00
    assert taskset_params['let_ratio'] >= 0.00
    assert taskset_params['let_ratio'] <= 1.00
    assert taskset_params['min_number_of_tasks'] <= taskset_params['max_number_of_tasks']
    assert taskset_params['min_period'] <= taskset_params['max_period']

    # cec params check
    assert cec_params['min_number_of_chains'] <= cec_params['max_number_of_chains']
    assert cec_params['min_number_of_tasks_in_chain'] <= cec_params['max_number_of_tasks_in_chain']
    assert cec_params['min_number_ecus'] <= cec_params['max_number_ecus']

    # combination check
    assert not (cec_params['generate_automotive_cecs'] and taskset_params['use_uniform_taskset_generation'] and not taskset_params['use_semi_harmonic_periods'])

    # check for warnings
    if warnings:
        ...
        # TODO


def check_methods_and_cecs(analysis_methods, normalization_methods, cecs):
    """Check if all selected methods are applicable on cecs, in case an 
    error was found an exception is thrown
    """

    if len(cecs) > 0:
        methods = analysis_methods + normalization_methods

        if isinstance(cecs[0], tuple):
            flattened_list = []
            for cec_tuple in cecs:
                for cec in list(cec_tuple):
                    flattened_list.append(cec)
            cecs = flattened_list

        releases = set([cec.base_ts.check_feature('release_pattern') for cec in cecs])
        communications = set([cec.base_ts.check_feature('communication_policy') for cec in cecs])
        
        release_pattern = next(iter(releases)) if len(releases) == 1 else 'mixed'
        communication_policy = next(iter(communications)) if len(communications) == 1 else 'mixed'

        for method in methods:
            assert release_pattern in method.features, f'{method.name} does not support release pattern {release_pattern}'
            assert communication_policy in method.features, f'{method.name} does not support communication policy {communication_policy}'


####################
### Run Analyses ###
####################

def performAnalyses(cause_effect_chains, methods, number_of_threads):
    """Analyzes the given cause-effect chains with the given analysis methods"""

    latencies_all = []

    # delete values from previous runs
    for method in methods:
        method.reset()

    # compute new latencies
    for method in methods:
        if method == None:
            # method is not yet implemented
            latencies_all.append([])
            continue

        if method.latencies != []:
            # latencies have been computed by another analysis method
            latencies_all.append(method.latencies)
            continue

        t = time.time()

        # special cases for some analyses
        if method.name == 'Gohari 2022':
            latencies_single = method.analysis(cause_effect_chains)

        # default case for most analyses
        else:
            if isinstance(cause_effect_chains[0], tuple):
                # parallelization for interconnected cause-effect chains
                with Pool(number_of_threads) as pool:
                    latencies_single = pool.starmap(method.analysis, cause_effect_chains)
            else:
                # parallelization for local cause-effect chains
                with Pool(number_of_threads) as pool:
                    latencies_single = pool.map(method.analysis, cause_effect_chains)

        
        elapsed = time.time() - t

        # debug output
        if print_elapsed_time:
            print(f'{method.name}: {elapsed}')
        
        latencies_all.append(latencies_single)
        method.latencies = latencies_single

        # check if result can be reused for other analyses
        ... #TODO

    return latencies_all


###########################
### Interconnected cecs ###
###########################

def create_interconnected_cecs(cause_effect_chains, cec_params):
    """Generates interconnected cause-effect chains from local cause-effect chains"""

    interconncected_chains = []

    while len(interconncected_chains) < cec_params['number_of_inter_cecs']:
        n = random.randint(cec_params['min_number_ecus'], cec_params['max_number_ecus'])
        candidates = random.sample(cause_effect_chains, n)
        
        # only add candidate if cecs have different base ts
        tasksets = set([cec.base_ts for cec in candidates])
        if len(tasksets) == n:
            random.shuffle(candidates)
            interconncected_chains.append(tuple(candidates))

    return interconncected_chains


###########################
### Taskset adjustments ###
###########################

def remove_invalid_tasksets(tasksets):
    """Returns only those task sets, in which every task
    meets its deadline
    """

    valid_tasksets = tasksets.copy()
    for taskset in tasksets:
        for task in taskset:
            if taskset.wcrts[task] > task.deadline:
                valid_tasksets.remove(taskset)
                break
    tasksets = valid_tasksets
    return tasksets


def adjust_taskset_release_pattern(taskset, sporadic_ratio):
    for task in random.sample(taskset.lst, int(len(taskset.lst) * sporadic_ratio)):
        task.release_pattern = 'sporadic'


def adjust_taskset_communication_policy(taskset, let_ratio):
    for task in random.sample(taskset.lst, int(len(taskset.lst) * let_ratio)):
        task.communication_policy = 'LET'


def adjust_taskset_bcets(taskset, bcet_ratio):
    for task in taskset:
        task.bcet = task.wcet * bcet_ratio


#####################################
### Cause-Effect Chain generation ###
#####################################

def generate_cecs(general_params,
                  taskset_generation_params,
                  cec_generation_params,
                  output_params):
    """Generates a list of cause-effect chains with the
    given parameters
    """
    
    ### Parameter Check ###
    
    check_params(
        taskset_generation_params,
        cec_generation_params
    )

    ### Create Taskset ###

    # selected automotive benchmark
    if taskset_generation_params['use_automotive_taskset_generation']:
        tasksets = automotiveBench.generate_automotive_tasksets(
            taskset_generation_params, 
            general_params['number_of_threads']
        )

    # selected uniform benchmark
    if taskset_generation_params['use_uniform_taskset_generation']:
        tasksets = uniformBench.generate_uniform_tasksets(
            taskset_generation_params,
            general_params['number_of_threads']
        )

    for taskset in tasksets:
        adjust_taskset_release_pattern(taskset, taskset_generation_params['sporadic_ratio'])
        adjust_taskset_communication_policy(taskset, taskset_generation_params['let_ratio'])
        adjust_taskset_bcets(taskset, taskset_generation_params['bcet_ratio'])
        taskset.rate_monotonic_scheduling()
        taskset.compute_wcrts()

    # remove tasksets with tasks that miss their deadline
    tasksets = remove_invalid_tasksets(tasksets)


    ### Generate Cause Effect Chains ###

    cause_effect_chains = []

    if cec_generation_params['generate_automotive_cecs']:
        cause_effect_chains = automotiveBench.generate_automotive_cecs(
            tasksets, 
            cec_generation_params,
            general_params['number_of_threads']
        )

    if cec_generation_params['generate_random_cecs']:
        cause_effect_chains = uniformBench.generate_random_cecs(
            tasksets, 
            cec_generation_params,
            general_params['number_of_threads']
        )

    if cec_generation_params['generate_interconnected_cecs']:
        cause_effect_chains = create_interconnected_cecs(
            cause_effect_chains, 
            cec_generation_params
        )

    if general_params['store_generated_cecs']:
        if output_params['output_dir'] == '':
            output_params['output_dir'] = helpers.make_output_directory()
        helpers.write_data(output_params['output_dir'] + "cause_effect_chains.pickle", cause_effect_chains)
        export_to_yaml(output_params['output_dir'], cause_effect_chains)

    return cause_effect_chains


#########################
### Output generation ###
#########################

def save_raw_analysis_results(selected_analysis_methods,
                              selected_normalization_methods,
                              output_dir):
    """Saves the results of the analyses in a csv file in the
    given output directory
    """

    selected_methods = set(selected_analysis_methods + selected_normalization_methods)
    names_all = []
    latencies_all = []
    for method in selected_methods:
        names_all.append(method.name_short)
        latencies_all.append(method.latencies)

    helpers.export_to_csv(
        output_dir + "results.csv",
        names_all,
        latencies_all
    )


def generate_output(output_params, selected_analysis_methods, selected_normalization_methods):
    """Generates the output files (diagrams/csv-file) with the results from the analyses"""

    if output_params['normalized_plots']:
        if output_params['output_dir'] == '':
            output_params['output_dir'] = helpers.make_output_directory()
        plot.create_normalized_plots(
            selected_analysis_methods, 
            selected_normalization_methods, 
            output_params['output_dir']
        )

    if output_params['absolute_plots']:
        if output_params['output_dir'] == '':
            output_params['output_dir'] = helpers.make_output_directory()
        plot.create_absolute_plots(
            selected_analysis_methods, 
            output_params['output_dir']
        )

    if output_params['raw_analysis_results']:
        if output_params['output_dir'] == '':
            output_params['output_dir'] = helpers.make_output_directory()
        save_raw_analysis_results(
            selected_analysis_methods,
            selected_normalization_methods,
            output_params['output_dir']
        )

    if output_params['print_to_console']:
        for analysis_method in selected_analysis_methods:
            print(analysis_method.latencies)


##########################
### Evaluation methods ###
##########################

def run_evaluation(general_params,
                   taskset_generation_params,
                   cec_generation_params,
                   selected_analysis_methods,
                   selected_normalization_methods,
                   output_params):
    """Runs a complete evaluation
    
    Includes the following steps:
    1. Loading/Generating a list of (interconnected/local) cause-effect chains
    2. Analyzing the list of cause-effect chains
    3. Generating the output files (diagrams/csv-file)
    """

    ### Create/Load Chains from file ###

    if general_params['load_cecs_from_file']:
        cause_effect_chains = helpers.load_data(general_params['cecs_file_path'])
    elif general_params['generate_cecs']:
        cause_effect_chains = generate_cecs(
            general_params,
            taskset_generation_params,
            cec_generation_params,
            output_params
        )
    else:
        return ''


    check_methods_and_cecs(
        selected_analysis_methods,
        selected_normalization_methods,
        cause_effect_chains
    )

    ### Run Analyses ###

    # check if at least one analysis method needs the schedule
    schedule_needed = sum([method.features.count('schedule') for method in selected_analysis_methods + selected_normalization_methods]) > 0
    if schedule_needed:
        compute_all_schedules(
            cause_effect_chains, 
            general_params['number_of_threads']
        )

    performAnalyses(
        cause_effect_chains,
        selected_analysis_methods + selected_normalization_methods, 
        general_params['number_of_threads']
    )


    ### Generate output ###

    generate_output(
        output_params,
        selected_analysis_methods,
        selected_normalization_methods,
    )

    return output_params['output_dir']