# import PySimpleGUI as sg
import FreeSimpleGUI as sg
from framework import *
import webbrowser
import sys
import traceback

catch_exceptions = False

def popUp(title, messages):
    """launches a basic pop-up window with a title and
    a message
    """

    view = list(map(lambda message : [sg.T(message)], messages))
    view.append([sg.Push(), sg.B('OK'), sg.Push()])
    sg.Window(title, [view]).read(close=True)


def inititalizeUI():
    """launches the main window of the GUI
    """

    sg.theme('system default')

    # Definition of the user interface layout

    layoutMenu = [sg.Menu([
        ['Links', [
            'E2E-Framework', 
            'Masterthesis', 
            'End-to-End',
            'End-to-End_Inter',
            'End-to-End_Mixed',
            'End-to-End_Equi',
            'np-data-age-analysis',
            'ChainMiss',
            # 'PySimpleGUI'
            'FreeSimpleGUI'
        ]], 
        ['Help', 
            ['About']
        ]
    ], k='-MENUBAR-')]

    layoutGeneral = [sg.Frame('General Settings', [
        [sg.Radio('Generate Cause-Effect Chains', "RadioGeneral", default=True, k='-Generate_CEC_Radio-', enable_events=True), sg.Checkbox('Store generated Cause-Effect Chains (pickle/YAML)', default=False, k='-Store_CECs_Box-', pad=((60,0),(0,0)))],
        [sg.Radio('Load Cause-Effect Chains from File', "RadioGeneral", default=False, k='-Load_CEC_Radio-', enable_events=True), sg.Text('File:', pad=((35,0),(0,0))), sg.Input(s=30, k='-File_Input-', disabled=True), sg.FileBrowse(file_types=(("CEC File", "*.pickle"),), k="-Browse-", disabled=True)],
        [sg.Text('Threads:'), sg.Input(s=5, k='-Threads_Input-', default_text='1')],
    ], expand_x=True)]

    layoutTaskset = [sg.Frame('Taskset Configuration', [
        [sg.Radio('Automotive Benchmark', "RadioTaskset", default=True, k='-Automotive_Taskset_Radio-', enable_events=True)],
        [sg.Radio('Uniform Taskset Generation', "RadioTaskset", default=False, k='-Uniform_Taskset_Radio-', enable_events=True)],
            [sg.Checkbox('Semi-Harmonic Periods', default=True, k='-Semi_harmonic_Box-', pad=((30,0),(0,0)), disabled=True, enable_events=True)],
            [sg.Text('Min Number Tasks:', pad=((35,0),(0,0))), sg.Input(s=5, k='-MINT_Input-', disabled=True, default_text='40'), sg.Text('Max Number Tasks:'), sg.Input(s=5, k='-MAXT_Input-', disabled=True, default_text='60')],
            [sg.Text('Min Period:', pad=((35,0),(0,0))), sg.Input(s=10, k='-PMIN_Input-', disabled=True, default_text='1'), sg.Text('Max Period:'), sg.Input(s=10, k='-PMAX_Input-', disabled=True, default_text='2000')],
        [sg.Text('Target Utilization:'), sg.Spin(values=[i for i in range(0, 101)], initial_value=50, key='-Utilization_Spin-', s=(3,1))],
        [sg.Text('Number of Tasksets:'), sg.Input(s=10, k='-Number_Tasksets_Input-', default_text='1')],
        [sg.Text('Percentage of sporadic Tasks in Taskset:'), sg.Spin(values=[i for i in range(0, 101)], initial_value=0, key='-Sporadic_Ratio_Spin-', s=(3,1))],
        [sg.Text('Percentage of Tasks using LET Communication:'), sg.Spin(values=[i for i in range(0, 101)], initial_value=0, key='-LET_Ratio_Spin-', s=(3,1))],
        [sg.Text('BCET Percentage (BCET relative to WCET):'), sg.Spin(values=[i for i in range(0, 101)], initial_value=100, key='-BCET_Ratio_Spin-', s=(3,1))]
    ], expand_x=True)]

    layoutChain = [sg.Frame('Cause-Effect Chain Configuration', [
        [sg.Radio('Automotive Benchmark', "RadioChain", default=True, k='-Automotive_CEC_Radio-', enable_events=True)],
        [sg.Radio('Random CECs', "RadioChain", default=False, k='-Random_CEC_Radio-', enable_events=True), sg.Text('Min Tasks:'), sg.Input(s=5, k='-Number_Tasks_Min_Input-', default_text='2', disabled=True), sg.Text('Max Tasks:'), sg.Input(s=5, k='-Number_Tasks_Max_Input-', default_text='10', disabled=True)],
        [sg.Text('Min Chains per Taskset:'), sg.Input(s=5, k='-Number_Chains_Min_Input-', default_text='30'), sg.Text('Max Chains per Taskset:'), sg.Input(s=5, k='-Number_Chains_Max_Input-', default_text='60')],
        [sg.Checkbox('Interconnected CECs', default=False, k='-Inter_CECs_Box-', enable_events=True), sg.Text('Min ECUs:'), sg.Input(s=3, k='-Min_ECUs_Input-', default_text='2', disabled=True), sg.Text('Max ECUs:'), sg.Input(s=3, k='-Max_ECUs_Input-', default_text='5', disabled=True), sg.Text('Number of inter Chains:'), sg.Input(s=7, k='-Number_Interconnected_Chains_Input-', default_text='1000', disabled=True)]
    ], expand_x=True)]

    layoutAnalysis = [sg.Frame('Analysis Configuration', [
        [sg.Frame('Analysis Methods', [[sg.TabGroup([[
            sg.Tab('Implicit Com',[[sg.Column(
                [[sg.Checkbox(method.name, default=False, k=method_key)] 
                    for method_key, method 
                    in analysesDict.items() 
                    if 'implicit' in method.features 
                    and 'mixed' not in method.features], 
                expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]
            ), 
            sg.Tab('LET Com',[[sg.Column(
                [[sg.Checkbox(method.name, default=False, k=method_key)] for method_key, method in analysesDict.items() if 'LET' in method.features and 'mixed' not in method.features], 
                expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]
            ),
            sg.Tab('Mixed Com',[[sg.Column(
                [[sg.Checkbox(method.name, default=False, k=method_key)] for method_key, method in analysesDict.items() if 'mixed' in method.features], 
                expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]
            )
        ]], expand_x=True)]], expand_x=True),
        sg.Frame('Normalization Methods', [[sg.TabGroup([[
            sg.Tab('Implicit Com',[[sg.Column(
                [[sg.Checkbox(method.name, default=False, k='n_'+method_key)] for method_key, method in analysesDict.items() if 'implicit' in method.features and 'mixed' not in method.features],  
                expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]
            ),  
            sg.Tab('LET Com',[[sg.Column(
                [[sg.Checkbox(method.name, default=False, k='n_'+method_key)] for method_key, method in analysesDict.items() if 'LET' in method.features and 'mixed' not in method.features], 
                expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]
            ),
            sg.Tab('Mixed Com',[[sg.Column(
                [[sg.Checkbox(method.name, default=False, k='n_'+method_key)] for method_key, method in analysesDict.items() if 'mixed' in method.features], 
                expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]
            )
        ]], expand_x=True)]], expand_x=True)
        ]
    ], expand_x=True, size=(None, 220))]

    layoutPlot = [sg.Frame('Output Configuration', [
        [sg.Checkbox('Create normalized Plots (relative Latency Reduction)', default=True, k='-CBP1-')],
        [sg.Checkbox('Create absolute Plots', default=False, k='-CBP2-')],
        [sg.Checkbox('Export Analyses Results (CSV)', default=False, k='-CBP3-')]
    ], expand_x=True, expand_y=True)]

    ttk_style = 'default'

    layout = [
        [layoutMenu],
        [layoutGeneral],
        [layoutTaskset],
        [layoutChain],
        [layoutAnalysis],
        [layoutPlot],
        [sg.Button('Run Evaluation'), sg.Button('Print CLI Commands')]
    ]

    font = ("Arial", 11)
    window = sg.Window('Evaluation Framework for End-to-End Analysis', layout, font=font, ttk_theme=ttk_style)
    return window


def updateUI(window, event, values):
    """updates the GUI after an event occurred
    """

    if event == '-Generate_CEC_Radio-':
        window['-Store_CECs_Box-'].update(disabled=False)
        window['-File_Input-'].update(disabled=True)
        window['-Browse-'].update(disabled=True)
        window['-Automotive_Taskset_Radio-'].update(disabled=False)
        window['-Uniform_Taskset_Radio-'].update(disabled=False)
        window['-Utilization_Spin-'].update(disabled=False)
        window['-Number_Tasksets_Input-'].update(disabled=False)
        if values['-Automotive_Taskset_Radio-']:
            window['-Automotive_CEC_Radio-'].update(disabled=False)
        if values['-Uniform_Taskset_Radio-']:
            window['-Semi_harmonic_Box-'].update(disabled=False)
            window['-MINT_Input-'].update(disabled=False)
            window['-MAXT_Input-'].update(disabled=False)
            window['-PMIN_Input-'].update(disabled=False)
            window['-PMAX_Input-'].update(disabled=False)
        if values['-Semi_harmonic_Box-']:
            window['-Automotive_CEC_Radio-'].update(disabled=False)
        window['-Random_CEC_Radio-'].update(disabled=False)
        if values['-Random_CEC_Radio-']:
            window['-Number_Tasks_Min_Input-'].update(disabled=False)
            window['-Number_Tasks_Max_Input-'].update(disabled=False)
        window['-Number_Chains_Min_Input-'].update(disabled=False)
        window['-Number_Chains_Max_Input-'].update(disabled=False)
        window['-Sporadic_Ratio_Spin-'].update(disabled=False)
        window['-LET_Ratio_Spin-'].update(disabled=False)
        window['-BCET_Ratio_Spin-'].update(disabled=False)
        window['-Inter_CECs_Box-'].update(disabled=False)
        if values['-Inter_CECs_Box-']:
            window['-Min_ECUs_Input-'].update(disabled=False)
            window['-Max_ECUs_Input-'].update(disabled=False)
            window['-Number_Interconnected_Chains_Input-'].update(disabled=False)
            for method_key, method in analysesDict.items():
                if not 'inter' in method.features:
                    window[method_key].update(False, disabled=True)
                    window['n_'+method_key].update(False, disabled=True)

    if event == '-Load_CEC_Radio-':
        window['-Store_CECs_Box-'].update(disabled=True)
        window['-File_Input-'].update(disabled=False)
        window['-Browse-'].update(disabled=False)
        window['-Automotive_Taskset_Radio-'].update(disabled=True)
        window['-Uniform_Taskset_Radio-'].update(disabled=True)
        window['-Utilization_Spin-'].update(disabled=True)
        window['-Number_Tasksets_Input-'].update(disabled=True)
        window['-Semi_harmonic_Box-'].update(disabled=True)
        window['-MINT_Input-'].update(disabled=True)
        window['-MAXT_Input-'].update(disabled=True)
        window['-PMIN_Input-'].update(disabled=True)
        window['-PMAX_Input-'].update(disabled=True)
        window['-Automotive_CEC_Radio-'].update(disabled=True)
        window['-Random_CEC_Radio-'].update(disabled=True)
        window['-Number_Tasks_Min_Input-'].update(disabled=True)
        window['-Number_Tasks_Max_Input-'].update(disabled=True)
        window['-Number_Chains_Min_Input-'].update(disabled=True)
        window['-Number_Chains_Max_Input-'].update(disabled=True)
        window['-Sporadic_Ratio_Spin-'].update(disabled=True)
        window['-LET_Ratio_Spin-'].update(disabled=True)
        window['-BCET_Ratio_Spin-'].update(disabled=True)
        window['-Inter_CECs_Box-'].update(disabled=True)
        window['-Min_ECUs_Input-'].update(disabled=True)
        window['-Max_ECUs_Input-'].update(disabled=True)
        window['-Number_Interconnected_Chains_Input-'].update(disabled=True)
        for method_key, method in analysesDict.items():
            if not 'inter' in method.features:
                window[method_key].update(disabled=False)
                window['n_'+method_key].update(disabled=False)

    if event == '-Automotive_Taskset_Radio-':
        window['-Semi_harmonic_Box-'].update(disabled=True)
        window['-MINT_Input-'].update(disabled=True)
        window['-MAXT_Input-'].update(disabled=True)
        window['-PMIN_Input-'].update(disabled=True)
        window['-PMAX_Input-'].update(disabled=True)
        window['-Automotive_CEC_Radio-'].update(disabled=False)

    if event == '-Uniform_Taskset_Radio-':
        window['-Semi_harmonic_Box-'].update(disabled=False)
        window['-MINT_Input-'].update(disabled=False)
        window['-MAXT_Input-'].update(disabled=False)
        window['-PMIN_Input-'].update(disabled=False)
        window['-PMAX_Input-'].update(disabled=False)
        if not values['-Semi_harmonic_Box-']:
            window['-Automotive_CEC_Radio-'].update(disabled=True)

    if event == '-Automotive_CEC_Radio-':
        window['-Number_Tasks_Min_Input-'].update(disabled=True)
        window['-Number_Tasks_Max_Input-'].update(disabled=True)

    if event == '-Random_CEC_Radio-':
        window['-Number_Tasks_Min_Input-'].update(disabled=False)
        window['-Number_Tasks_Max_Input-'].update(disabled=False)

    if event == '-Semi_harmonic_Box-':
        if values['-Semi_harmonic_Box-']:
            window['-Automotive_CEC_Radio-'].update(disabled=False)
        else:
            window['-Automotive_CEC_Radio-'].update(disabled=True)
            window['-Random_CEC_Radio-'].update(value=True)

    if event == '-Inter_CECs_Box-':
        if values['-Inter_CECs_Box-']:
            window['-Min_ECUs_Input-'].update(disabled=False)
            window['-Max_ECUs_Input-'].update(disabled=False)
            window['-Number_Interconnected_Chains_Input-'].update(disabled=False)
            for method_key, method in analysesDict.items():
                if not 'inter' in method.features:
                    window[method_key].update(False, disabled=True)
                    window['n_'+method_key].update(False, disabled=True)
        else:
            window['-Min_ECUs_Input-'].update(disabled=True)
            window['-Max_ECUs_Input-'].update(disabled=True)
            window['-Number_Interconnected_Chains_Input-'].update(disabled=True)
            for method_key, method in analysesDict.items():
                if not 'inter' in method.features:
                    window[method_key].update(disabled=False)
                    window['n_'+method_key].update(disabled=False)


def runVisualMode(window):
    """controls GUI window and reacts to the users input
    """

    while True:
        event, values = window.read()
        updateUI(window, event, values)

        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            break

        if event == 'E2E-Framework':
            webbrowser.open_new('https://github.com/E2E-Evaluation-org/E2EEvaluation')

        if event == 'Masterthesis':
            webbrowser.open_new('https://github.com/E2E-Evaluation-org/E2EEvaluation/blob/main/doc/E2EEvaluation.pdf')

        if event == 'End-to-End':
            webbrowser.open_new('https://github.com/tu-dortmund-ls12-rt/end-to-end')

        if event == 'End-to-End_Inter':
            webbrowser.open_new('https://github.com/tu-dortmund-ls12-rt/end-to-end_inter')

        if event == 'End-to-End_Mixed':
            webbrowser.open_new('https://github.com/tu-dortmund-ls12-rt/end-to-end_mixed')

        if event == 'End-to-End_Equi':
            webbrowser.open_new('https://github.com/tu-dortmund-ls12-rt/mrt_mda')

        if event == 'np-data-age-analysis':
            webbrowser.open_new('https://github.com/porya-gohary/np-data-age-analysis')

        if event == 'ChainMiss':
            webbrowser.open_new('https://github.com/PaoloPazzaglia/ChainMiss')

        # if event == 'PySimpleGUI':
        #     webbrowser.open_new('https://www.pysimplegui.com/')
        
        if event == 'FreeSimpleGUI':
            webbrowser.open_new('https://freesimplegui.readthedocs.io/')

        if event == 'About':
            popUp('About', [
                'Author: Robin Edmaier', 
                'Parts of this framework are based on existing implementations.', 
                '', 
                'This framework is published as free software under the MIT license.'
            ])

        if event == 'Run Evaluation' or event == 'Print CLI Commands':

            ##################################
            ### Gather all inputs from GUI ###
            ##################################

            general_params = dict(default_general_params)
            taskset_params = dict(default_taskset_generation_params)
            cec_params = dict(default_cec_generation_params)
            output_params = dict(default_output_params)

            #print(values)

            # General
            general_params['generate_cecs'] = values['-Generate_CEC_Radio-']
            general_params['store_generated_cecs'] = values['-Store_CECs_Box-']
            general_params['load_cecs_from_file'] = values['-Load_CEC_Radio-']
            try:
                general_params['number_of_threads'] = int(values['-Threads_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid number of threads '{values['-Threads_Input-']}'!"])
                continue
            general_params['cecs_file_path'] = values['-File_Input-']

            # Taskset
            taskset_params['use_automotive_taskset_generation'] = values['-Automotive_Taskset_Radio-']
            taskset_params['use_uniform_taskset_generation'] = values['-Uniform_Taskset_Radio-']
            try:
                taskset_params['target_util'] = int(values['-Utilization_Spin-'])/100
                if taskset_params['target_util'] > 1 or taskset_params['target_util'] < 0:
                    raise ValueError
            except ValueError:
                popUp('ValueError', [f"Invalid target utilization '{values['-Utilization_Spin-']}'!"])
                continue
            try:
                taskset_params['number_of_tasksets'] = int(values['-Number_Tasksets_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid number of tasksets '{values['-Number_Tasksets_Input-']}'!"])
                continue
            taskset_params['use_semi_harmonic_periods'] = values['-Semi_harmonic_Box-']
            try:
                taskset_params['min_number_of_tasks'] = int(values['-MINT_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid number of min tasks '{values['-MINT_Input-']}'!"])
                continue
            try:
                taskset_params['max_number_of_tasks'] = int(values['-MAXT_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid number of max tasks '{values['-MAXT_Input-']}'!"])
                continue
            try:
                taskset_params['min_period'] = int(values['-PMIN_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid min period '{values['-PMIN_Input-']}'!"])
                continue
            try:
                taskset_params['max_period'] = int(values['-PMAX_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid max period '{values['-PMAX_Input-']}'!"])
                continue
            try:
                taskset_params['sporadic_ratio'] = int(values['-Sporadic_Ratio_Spin-'])/100
            except ValueError:
                popUp('ValueError', [f"Invalid sporadic tasks percentage '{values['-Sporadic_Ratio_Spin-']}'!"])
                continue
            try:
                taskset_params['let_ratio'] = int(values['-LET_Ratio_Spin-'])/100
            except ValueError:
                popUp('ValueError', [f"Invalid percentage for LET communication '{values['-LET_Ratio_Spin-']}'!"])
                continue
            try:
                taskset_params['bcet_ratio'] = int(values['-BCET_Ratio_Spin-'])/100
            except ValueError:
                popUp('ValueError', [f"Invalid BCET percentage '{values['-BCET_Ratio_Spin-']}'!"])
                continue

            # Cause-effect chains
            cec_params['generate_automotive_cecs'] = values['-Automotive_CEC_Radio-']
            cec_params['generate_random_cecs'] = values['-Random_CEC_Radio-']
            try:
                cec_params['min_number_of_tasks_in_chain'] = int(values['-Number_Tasks_Min_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid min number of tasks '{values['-Number_Tasks_Min_Input-']}'!"])
                continue
            try:
                cec_params['max_number_of_tasks_in_chain'] = int(values['-Number_Tasks_Max_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid max number of tasks '{values['-Number_Tasks_Max_Input-']}'!"])
                continue
            try:
                cec_params['min_number_of_chains'] = int(values['-Number_Chains_Min_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid min number of chains '{values['-Number_Chains_Min_Input-']}'!"])
                continue
            try:
                cec_params['max_number_of_chains'] = int(values['-Number_Chains_Max_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid max number of chains '{values['-Number_Chains_Max_Input-']}'!"])
                continue
            cec_params['generate_interconnected_cecs'] = values['-Inter_CECs_Box-']
            try:
                cec_params['min_number_ecus'] = int(values['-Min_ECUs_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid min number of ECUs '{values['-Min_ECUs_Input-']}'!"])
                continue
            try:
                cec_params['max_number_ecus'] = int(values['-Max_ECUs_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid max number of ECUs '{values['-Max_ECUs_Input-']}'!"])
                continue
            try:
                cec_params['number_of_inter_cecs'] = int(values['-Number_Interconnected_Chains_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid number of interconnected CECs '{values['-Number_Interconnected_Chains_Input-']}'!"])
                continue
            
            # Analysis
            selected_analysis_methods = []
            for method in analysesDict.keys():
                if values[method] == True:
                    selected_analysis_methods.append(analysesDict[method])

            selected_normalization_methods = []
            for method in analysesDict.keys():
                if values['n_' + method] == True:
                    selected_normalization_methods.append(analysesDict[method])
            
            # Plots
            output_params['normalized_plots'] = values['-CBP1-']
            output_params['absolute_plots'] = values['-CBP2-']
            output_params['raw_analysis_results'] = values['-CBP3-']

            if event == 'Run Evaluation':

                ################################
                ### Run Evaluation Framework ###
                ################################

                if catch_exceptions:
                    try:
                        run_evaluation(
                            general_params,
                            taskset_params,
                            cec_params,
                            selected_analysis_methods,
                            selected_normalization_methods,
                            output_params
                        )

                        # Positive Feedback Pop-Up
                        popUp('Info', 
                            ['Run finished without any errors.', 
                            'Results are saved in:', 
                            output_params['output_dir']]
                        )

                    except AssertionError:
                        # Some parameters are wrong

                        _, _, tb = sys.exc_info()
                        tb_info = traceback.extract_tb(tb)
                        filename, line, func, text = tb_info[-1]

                        # Negative Feedback Pop-Up
                        popUp('Assertion Error', 
                            ['Could not run the Evaluation:',
                            f'An error occurred on line {line} of {filename} in statement',
                            f'{text}']
                        )

                    except Exception as exception:
                        # Unknown error

                        print(exception.__cause__)

                        # Negative Feedback Pop-Up
                        popUp('Unknown Error', 
                            ['An unknown error occurred on during the evaluation',
                            'See the traceback of the error in the system console']
                        )

                else:

                    run_evaluation(
                        general_params,
                        taskset_params,
                        cec_params,
                        selected_analysis_methods,
                        selected_normalization_methods,
                        output_params
                    )

                    # Positive Feedback Pop-Up
                    popUp('Info', 
                        ['Run finished without any errors.', 
                        'Results are saved in:', 
                        output_params['output_dir']]
                    )

            if event == 'Print CLI Commands':
                generation_command = 'python3 e2eMain.py generate-cecs -o cli_'
                analysis_command = 'python3 e2eMain.py analyze-cecs -f cli_cause_effect_chains.pickle'

                for param in general_params:
                    if general_params[param] != False and general_params[param] != '' and param != 'generate_cecs':
                        if isinstance(general_params[param], bool):
                            generation_command = generation_command + f' --{param}'
                            analysis_command = analysis_command + f' --{param}'
                        else:
                            generation_command = generation_command + f' --{param}={general_params[param]}'
                            analysis_command = analysis_command + f' --{param}={general_params[param]}'
                
                for param in taskset_params:
                    if taskset_params[param] != False:
                        if isinstance(taskset_params[param], bool):
                            generation_command = generation_command + f' --{param}'
                        else:
                            generation_command = generation_command + f' --{param}={taskset_params[param]}'

                for param in cec_params:
                    if cec_params[param] != False:
                        if isinstance(cec_params[param], bool):
                            generation_command = generation_command + f' --{param}'
                        else:
                            generation_command = generation_command + f' --{param}={cec_params[param]}'

                for analysis_method in selected_analysis_methods:
                    analysis_command = analysis_command + f' -a {analysis_method.analysis.__name__}'

                for normalization_method in selected_normalization_methods:
                    analysis_command = analysis_command + f' -n {normalization_method.analysis.__name__}'

                for param in output_params:
                    if output_params[param] != False and output_params[param] != '':
                        if isinstance(output_params[param], bool):
                            analysis_command = analysis_command + f' --{param}'
                        else:
                            analysis_command = analysis_command + f' --{param}={output_params[param]}'

                print('')
                if general_params['generate_cecs']:
                    print('###----- 2 Commands -----###')
                    print(generation_command)
                    print('')
                else:
                    print('###----- 1 Command  -----###')
                print(analysis_command)