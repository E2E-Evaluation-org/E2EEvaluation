from framework import *
import getopt


def print_help():

    general_params = []
    general_params.extend(['  --' + param + ' (' + str(default_general_params[param]) + ')' for param in list(default_general_params.keys()) if isinstance(default_general_params[param], bool)])
    general_params.extend(['  --' + param + '=<value> (' + "''" + ')' for param in list(default_general_params.keys()) if isinstance(default_general_params[param], str)])
    general_params.extend(['  --' + param + '=<value> (' + str(default_general_params[param]) + ')' for param in list(default_general_params.keys()) if not isinstance(default_general_params[param], str) and not isinstance(default_general_params[param], bool)])
    
    taskset_params = []
    taskset_params.extend(['  --' + param + ' (' + str(default_taskset_generation_params[param]) + ')' for param in list(default_taskset_generation_params.keys()) if isinstance(default_taskset_generation_params[param], bool)])
    taskset_params.extend(['  --' + param + '=<value> (' + "''" + ')' for param in list(default_taskset_generation_params.keys()) if isinstance(default_taskset_generation_params[param], str)])
    taskset_params.extend(['  --' + param + '=<value> (' + str(default_taskset_generation_params[param]) + ')' for param in list(default_taskset_generation_params.keys()) if not isinstance(default_taskset_generation_params[param], str) and not isinstance(default_taskset_generation_params[param], bool)])

    cec_params = []
    cec_params.extend(['  --' + param + ' (' + str(default_cec_generation_params[param]) + ')' for param in list(default_cec_generation_params.keys()) if isinstance(default_cec_generation_params[param], bool)])
    cec_params.extend(['  --' + param + '=<value> (' + "''" + ')' for param in list(default_cec_generation_params.keys()) if isinstance(default_cec_generation_params[param], str)])
    cec_params.extend(['  --' + param + '=<value> (' + str(default_cec_generation_params[param]) + ')' for param in list(default_cec_generation_params.keys()) if not isinstance(default_cec_generation_params[param], str) and not isinstance(default_cec_generation_params[param], bool)])

    output_params = []
    output_params.extend(['  --' + param + ' (' + str(default_output_params[param]) + ')' for param in list(default_output_params.keys()) if isinstance(default_output_params[param], bool)])
    output_params.extend(['  --' + param + '=<value> (' + "''" + ')' for param in list(default_output_params.keys()) if isinstance(default_output_params[param], str)])
    output_params.extend(['  --' + param + '=<value> (' + str(default_output_params[param]) + ')' for param in list(default_output_params.keys()) if not isinstance(default_output_params[param], str) and not isinstance(default_output_params[param], bool)])

    print('## 1. Generating cause-effect chains with the framework ##')
    print('  python3 e2eMain.py generate-cecs [general_param|taskset_param|cec_param|output_param]')
    print('')
    print('## 2. Analyzing cause-effect chains with the framework ##')
    print('  python3 e2eMain.py analyze-cecs [general_param|-a analysis_method|-n analysis_method|output_param]')
    print('')
    print('## 3. Basic Analysis Mode ##')
    print('  python3 e2eMain.py <analysis_method> <cecs_file_path> [number_of_threads]')
    print('')

    print('## Available Options ##')
    print('')
    print('General Parameters:')
    for param in general_params: print(param)
    print('')
    print('Task Set Parameters:')
    for param in taskset_params: print(param)
    print('')
    print('Cause-Effect Chain Parameters:')
    for param in cec_params: print(param)
    print('')
    print('Analysis Methods:')
    print('  ' + str(list(analysesDict.keys())))
    print('')
    print('Output Parameters:')
    for param in output_params: print(param)


# helper function
def replace_value(dict, key, new_value):
    """Replaces the value at dict[key] with the given new_value.
    new_value is parsed into the type of the previous value.
    """
    old_value = dict[key]
    if new_value == '':
        dict[key] = True
        return
    if isinstance(old_value, int):
        dict[key] = int(new_value)
        return
    if isinstance(old_value, float):
        dict[key] = float(new_value)
        return
    raise ValueError('Could not parse value for', key)


def runCLIMode(args):
    """starts the CLI mode of the framework
    cli mode has three options:
    1. create cause-effect chains and store them in a file
    2. load cause-effect chains from a file and analyse them
    3. simple mode, analyze cec-file with only one analysis method
    """

    # get default parameters
    general_params = dict(default_general_params)
    taskset_generation_params = dict(default_taskset_generation_params)
    cec_generation_params = dict(default_cec_generation_params)
    selected_analysis_methods = []
    selected_normalization_methods = []
    output_params = dict(default_output_params)

    ##################
    #### Read args ###
    ##################

    if args[0] == 'generate-cecs':

        general_params['generate_cecs'] = True
        general_params['store_generated_cecs'] = True

        try:
            options, arguments = getopt.getopt(
                args[1:],
                "t:o:d",
                [param + '=' for param in list(general_params.keys()) if not isinstance(general_params[param], bool)] + 
                [param for param in list(general_params.keys()) if isinstance(general_params[param], bool)] +
                [param + '=' for param in list(taskset_generation_params.keys()) if not isinstance(taskset_generation_params[param], bool)] + 
                [param for param in list(taskset_generation_params.keys()) if isinstance(taskset_generation_params[param], bool)] +
                [param + '=' for param in list(cec_generation_params.keys()) if not isinstance(cec_generation_params[param], bool)] + 
                [param for param in list(cec_generation_params.keys()) if isinstance(cec_generation_params[param], bool)] +
                [param + '=' for param in list(output_params.keys()) if not isinstance(output_params[param], bool)] + 
                [param for param in list(output_params.keys()) if isinstance(output_params[param], bool)]
            )
        except getopt.GetoptError as err:
            print(f"[ERROR] Getopt: {err}")
            print('[ERROR] Could not parse input parameters')
            print('')
            print_help()
            return

        for option, value in options:
            option = option.replace('-', '')
            if option in taskset_generation_params.keys():
                replace_value(taskset_generation_params, option, value)
            if option in cec_generation_params.keys():
                replace_value(cec_generation_params, option, value)
            if option == 't':
                general_params['number_of_threads'] = int(value)
            if option == 'o':
                output_params['output_dir'] = value
            if option == 'd':
                general_params['debug_output'] = True
            if option == 'h':
                print_help()
                return


    elif args[0] == 'analyze-cecs':

        general_params['load_cecs_from_file'] = True

        try:
            options, arguments = getopt.getopt(
                args[1:],
                "a:df:hn:o:t:",
                [param + '=' for param in list(general_params.keys()) if not isinstance(general_params[param], bool)] + 
                [param for param in list(general_params.keys()) if isinstance(general_params[param], bool)] +
                [param + '=' for param in list(output_params.keys()) if not isinstance(output_params[param], bool)] + 
                [param for param in list(output_params.keys()) if isinstance(output_params[param], bool)]
            )
        except getopt.GetoptError as err:
            print(f"[ERROR] Getopt: {err}")
            print('[ERROR] Could not parse input parameters')
            print('')
            print_help()
            return

        for option, value in options:
            option = option.replace('-', '')
            if option in general_params.keys():
                replace_value(general_params, option, value)
            elif option in output_params.keys():
                replace_value(output_params, option, value)
            elif option == 't':
                general_params['number_of_threads'] = int(value)
            elif option == 'o':
                output_params['output_dir'] = value
            elif option == 'd':
                general_params['debug_output'] = True
            elif option == 'f':
                general_params['cecs_file_path'] = value
            elif option == 'a':
                selected_analysis_methods.append(analysesDict[value])
            elif option == 'n':
                selected_normalization_methods.append(analysesDict[value])
            elif option == 'h':
                print_help()
                return


    elif len(args) == 2 or len(args) == 3:
        # simplest mode
        # first argument is the analysis method
        # second argument is the file to analyze
        # (optional) third argument is the number of threads

        general_params['load_cecs_from_file'] = True
        general_params['cecs_file_path'] = args[1]
        general_params['number_of_threads'] = int(args[2]) if len(args) == 3 else 1
        output_params['print_to_console'] = True
        selected_analysis_methods.append(analysesDict[args[0]])

    elif args[0] == '-h' or args[0] == '--h' or args[0] == '--help':
        print_help()
        return

    else:
        print(f"[ERROR] Unknown parameter: '{args[0]}'")
        print('[ERROR] Could not parse input parameters')
        print('')
        print_help()
        return
    

    ################################
    ### Run Evaluation Framework ###
    ################################

    # Debug Output
    if general_params['debug_output']:
        print('[Info] general params:', general_params)
        print('[Info] taskset_generation_params:', taskset_generation_params)
        print('[Info] cec_generation_params:', cec_generation_params)
        print('[Info] selected analysis methods:', selected_analysis_methods)
        print('[Info] selected normalization methods:', selected_normalization_methods)
        print('[Info] output params:', output_params)

    run_evaluation(
        general_params,
        taskset_generation_params,
        cec_generation_params,
        selected_analysis_methods,
        selected_normalization_methods,
        output_params
    )

    # Debug Output
    if general_params['debug_output']:
        print('[Info] Run finished without any errors')
        print('[Info] Results are saved in:', output_params['output_dir'])
        



