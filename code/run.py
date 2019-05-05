from evaluations import system
from register import registered_clients
from evaluations.decorator import REGISTRY
import json


stream = open("matrix.yml", "r")
yml_dict = system.load_yml()


def transform_yml_to_tag(provider, map):
    list_of_methods = []
    for key in map:
        i = 0
        for action in map[key]:
            if isinstance(action, dict):
                for sub_action in action:
                    list_of_methods.append(((provider + ':' + key + ':' + sub_action), map[key][i][sub_action]))
                    i += 1
            else:
                list_of_methods.append(((provider + ':' + key + ':' + action), []))
    return list_of_methods


def get_method(map, point):
    if point in map:
        return map[point]
    elif '*' + point[3:] in map:
        return map['*' + point[3:]]


for experiment in yml_dict:
    for cm in yml_dict[experiment]['cmps']:
        for provider in yml_dict[experiment]['providers']:
            system.create_or_open_dir(yml_dict[experiment]['output_dir'] + '/' + experiment)
            if yml_dict[experiment]['pre_experiment']:
                for method, params in transform_yml_to_tag(provider, yml_dict[experiment]['pre_experiment']):
                    call_method = get_method(REGISTRY[cm], method)
                    if call_method:
                        getattr(registered_clients[cm], get_method(REGISTRY[cm], method))(*tuple(params))
            if yml_dict[experiment]['actions']:
                f = open(cm + '_' + provider, 'a', 0)
                for i in range(yml_dict[experiment]['repetitions']):
                    for method, params in transform_yml_to_tag(provider, yml_dict[experiment]['actions']):
                        call_method = get_method(REGISTRY[cm], method)
                        if call_method:
                            f.write(json.dumps(getattr(registered_clients[cm],
                                                       get_method(REGISTRY[cm], method))(*tuple(params))))
                            f.write('\n')
            if yml_dict[experiment]['post_experiment']:
                for method, params in transform_yml_to_tag(provider, yml_dict[experiment]['post_experiment']):
                    call_method = get_method(REGISTRY[cm], method)
                    if call_method:
                        getattr(registered_clients[cm], get_method(REGISTRY[cm], method))(*tuple(params))
