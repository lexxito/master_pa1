import matplotlib.pyplot as plt
import numpy as np
import json
import glob
import system

fin_dict = {}

#for data_file in glob.glob("/home/lexxito/experiments/*/*"):
for data_file in glob.glob("/home/lexxito/MasterProjects/PA1/experiments_data/*/*"):
    exp = data_file.split('/')[-2].split('_')[0]
    name = exp + '_' + data_file.split('/')[-1].split('_')[0]
    if data_file.split('/')[-2] != 'pics':
        try:
            f = open(data_file, 'r')
            for line in f:
                js_dict = json.loads(line)
                for key in js_dict:
                    for sub_key in js_dict[key]:
                        if sub_key == 'time':
                            mod_key = key+'_'+sub_key
                            if mod_key not in fin_dict:
                                fin_dict[mod_key] = {}
                            if name not in fin_dict[mod_key]:
                                fin_dict[mod_key][name] = np.array([])
                            else:
                                fin_dict[mod_key][name] = np.append(fin_dict[mod_key][name], js_dict[key]['time'])
                        if sub_key == 'consumption':
                            def python_cons(stat):
                                if stat in js_dict[key]['consumption']['start']:
                                    adap_key = key + '_' + stat.split('_')[0]
                                    if adap_key not in fin_dict:
                                        fin_dict[adap_key] = {}
                                    if name not in fin_dict[adap_key]:
                                        fin_dict[adap_key][name] = np.array([])
                                    else:
                                        fin_dict[adap_key][name] = np.append(fin_dict[adap_key][name],
                                                                             js_dict[key]['consumption']['end'][stat][0] -
                                                                             js_dict[key]['consumption']['start'][stat][0])

                            def docker_cons(stat):
                                if 'cpu_use' not in js_dict[key]['consumption']['start']:
                                    for container in js_dict[key]['consumption']['start']:
                                        adap_key = key + '_' + stat
                                        if adap_key not in fin_dict:
                                            fin_dict[adap_key] = {}
                                        if name not in fin_dict[adap_key]:
                                            fin_dict[adap_key][name] = {}
                                        container_name = js_dict[key]['consumption']['start'][container]['image']
                                        if container_name not in fin_dict[adap_key][name]:
                                            fin_dict[adap_key][name][container_name] = np.array([])
                                        else:
                                            try:
                                                fin_dict[adap_key][name][container_name] = \
                                                        np.append(fin_dict[adap_key][name][container_name],
                                                                  (js_dict[key]['consumption']['end'][container]
                                                                   [stat + '_stats'][stat+'_usage']['usage_in_usermode'] -
                                                                   js_dict[key]['consumption']['start'][container]
                                                                   [stat + '_stats'][stat+'_usage']['usage_in_usermode'])
                                                                  )
                                            except KeyError:
                                                fin_dict[adap_key][name][container_name] = \
                                                    np.append(fin_dict[adap_key][name][container_name],
                                                              (js_dict[key]['consumption']['end']
                                                               [container][stat + '_stats']['usage'] -
                                                               js_dict[key]['consumption']['start']
                                                               [container][stat + '_stats']['usage'])
                                                              )
                            python_cons('cpu_use')
                            python_cons('memory_use')
                            docker_cons('cpu')
                            docker_cons('memory')
        except IOError:
            pass


def normalize_docker_consumption(full_dict, image_map):
    for variable in full_dict:
        for platform in full_dict[variable]:
            for sub_platform in image_map:
                if sub_platform in platform:
                    if image_map[sub_platform] in full_dict[variable][platform]:
                        full_dict[variable][platform] = full_dict[variable][platform][image_map[sub_platform]]
    return full_dict


def get_axis_label(graph_name):
    if 'cpu' in graph_name:
        return 'CPU time, ms'
    elif 'memory' in graph_name:
        return 'Memory, KB'
    elif 'time' in graph_name:
        return 'Latency, ms'


def generate_all_single_boxplots(full_dict):
    for graph_name in full_dict:
        list_name = graph_name.split(':')
        folder = list_name[1]+'_'+list_name[2]
        # system.create_or_open_dir('/home/lexxito/experiments/pics/'+folder)
        system.create_or_open_dir('/home/lexxito/MasterProjects/PA1/graphs/'+folder)
        list_of_data = []
        labels = []
        for platform in full_dict[graph_name]:
            full_dict[graph_name][platform].shape = (-1, 1)
            plt.figure(1, figsize=(3, 3))
            ax = plt.subplot(111)
            plt.title(graph_name, fontsize=8)
            plt.boxplot(full_dict[graph_name][platform], labels=[platform])
            mu = full_dict[graph_name][platform].mean()
            median = np.median(full_dict[graph_name][platform])
            sigma = full_dict[graph_name][platform].std()
            textstr = '$\mu=%.2f$\n$\mathrm{median}=%.2f$\n$\sigma=%.2f$' % (mu, median, sigma)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            plt.text(0.55, 0.95, textstr, transform=ax.transAxes, fontsize=5,
                     verticalalignment='top', bbox=props)
            plt.ylabel(get_axis_label(graph_name), fontsize=8)
            plt.xticks(fontsize=8)
            plt.yticks(fontsize=5, rotation=90)
            plt.savefig(platform + '.pdf', format='pdf')
            plt.close()
            list_of_data.append(full_dict[graph_name][platform])
            labels.append(platform)
            try:
                plt.figure(1, figsize=(10, 10))
                plt.title(graph_name, fontsize=8)
                plt.ylabel(get_axis_label(graph_name), fontsize=8)
                plt.xticks(fontsize=8)
                plt.yticks(fontsize=5, rotation=90)
                plt.boxplot(list_of_data, labels=labels)
                plt.savefig(folder + '.pdf', format='pdf')
                plt.close()
            except ValueError as e:
                print e


def generate_table(full_dict):
    table_dict = {}
    for graph_name in full_dict:
        key_array = graph_name.split(':')
        provider = key_array[0]
        source = key_array[1]
        action = key_array[2].split('_')[0]
        param = key_array[2].split('_')[1]
        if provider not in table_dict:
            table_dict[provider] = {}
        if source not in table_dict[provider]:
            table_dict[provider][source] = {}
        if action not in table_dict[provider][source]:
            table_dict[provider][source][action] = {}

        for platform in full_dict[graph_name]:
            platform_clean = platform.split('_')[0]
            platform_dict = {}
            np_array = full_dict[graph_name][platform]
            platform_dict['median'] = np.median(np_array)
            platform_dict['sigma'] = np_array.std()
            platform_dict['mu'] = np_array.mean()

            if platform_clean not in table_dict[provider][source][action]:
                table_dict[provider][source][action][platform_clean] = {}
            table_dict[provider][source][action][platform_clean][param] = platform_dict

    matrix_map = {}
    for provider in table_dict:
        for source in table_dict[provider]:
            for action in table_dict[provider][source]:
                for platform in table_dict[provider][source][action]:
                    for param in table_dict[provider][source][action][platform]:
                        if param not in matrix_map:
                            matrix_map[param] = []
                        for value in table_dict[provider][source][action][platform][param]:
                            if value not in matrix_map[param]:
                                matrix_map[param].append(value)

    # create a header
    max_length = 0
    for param in matrix_map:
        max_length += len(matrix_map[param])

    space_for_columns = '& & &'
    full_table_latex = '\\begin{tabular}{llll%s}\n' % (max_length*'l')
    full_table_latex += '\t\\hline\n'
    full_table_latex += '\t\multirow{3}{*}{pr.} & \multirow{3}{*}{source} & \multirow{3}{*}{action} & ' \
                        '\multirow{3}{*}{platform} & \multicolumn{%s}{c}{metrics} \\\ \n' % (str(max_length))
    full_table_latex += '\t%s' % space_for_columns

    for characteristic in matrix_map:
        if 'memory' in characteristic:
            unit='KB'
        elif 'cpu' in characteristic:
            unit = 'cpu/sec'
        else:
            unit = 'sec'
        full_table_latex += ' & \multicolumn{%s}{c}{%s}' % (len(matrix_map[characteristic]), characteristic+','+unit)
    full_table_latex += '\\\ \n \t'+space_for_columns

    for characteristic in matrix_map:
        for var in matrix_map[characteristic]:
            full_table_latex += ' & '+var

    full_table_latex += '\\\ \n \t\hline\n \\\[-1em]'

    # crate rest of the body

    for provider in table_dict:
        max_rows = 0
        for source in table_dict[provider]:
            for action in table_dict[provider][source]:
                max_rows += len(table_dict[provider][source][action])
        full_table_latex += '\t\multirow{%s}{*}{%s}' % (max_rows, provider)
        for source in table_dict[provider]:
            max_rows = 0
            for action in table_dict[provider][source]:
                max_rows += len(table_dict[provider][source][action])
            full_table_latex += ' & \multirow{%s}{*}{\\rotatebox[origin=c]{90}{%s}}' % (max_rows, source)
            for action in table_dict[provider][source]:
                full_table_latex += ' & \multirow{%s}{*}{%s}' % (len(table_dict[provider][source][action]), action)
                for platform in table_dict[provider][source][action]:
                    full_table_latex += ' & ' + platform
                    for characteristic in matrix_map:
                        if characteristic in table_dict[provider][source][action][platform]:
                            for var in matrix_map[characteristic]:
                                if var in table_dict[provider][source][action][platform][characteristic]:
                                    full_n = table_dict[provider][source][action][platform][characteristic][var]
                                    number = '%.2f' % full_n
                                    if len(str(number)) < 8:
                                        full_table_latex += ' & ' + str(number)
                                    else:
                                        full_table_latex += ' & ' + "{:.2e}".format(float(number))
                                else:
                                    full_table_latex += ' & pass'
                        else:
                            full_table_latex += ' &' * len(matrix_map[characteristic])
                    full_table_latex += '\\\ \\\[-1em] \n \t ' + space_for_columns[:-2]
                full_table_latex = full_table_latex[:-4] + '\\\[-1em] \cline{3-%s} \\\[-1em] ' % (4 + max_length) + ' &'
            full_table_latex = full_table_latex[:-2]
        full_table_latex += '\hline\n'
    full_table_latex += '\\end{tabular}'
    print full_table_latex


c_map = {'manageiq': 'manageiq/manageiq:gaprindashvili-3', 'mistio': 'mist/mist:io-v3-0-0'}
new_dict = normalize_docker_consumption(fin_dict, c_map)
cpu_dict = {}
memory_dict = {}
time_dict = {}

for element in new_dict:
    if 'cpu' in element:
        cpu_dict[element] = new_dict[element]
    if 'time' in element:
        time_dict[element] = new_dict[element]
    if 'memory' in element:
        memory_dict[element] = new_dict[element]

generate_table(time_dict)

generate_table(cpu_dict)

generate_table(memory_dict)

generate_all_single_boxplots(new_dict)
