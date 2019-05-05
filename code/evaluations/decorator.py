import system
REGISTRY = {}


class Decorators:
    def __init__(self):
        self.REGISTRY_ENTRY = {}

    @classmethod
    def timing(cls, output=False):
        def real_decorator(f):
            cls.REGISTRY_ENTRY = {f.func_code.co_filename.split('/')[-2]:  f.func_name}

            def wrapper(*args, **kwargs):
                start_time = system.get_current_time()
                result = f(*args, **kwargs)
                delta = system.get_current_time() - start_time
                if output:
                    result['time'] = delta * 1000
                    return result
                return {'time': delta * 1000}
            return wrapper
        return real_decorator

    @classmethod
    def python_consumption(cls):
        def real_decorator(f):
            def wrapper(*args, **kwargs):
                cons_dict = {'start': system.get_python_usage()}
                result = f(*args, **kwargs)
                cons_dict['end'] = system.get_python_usage()
                result['consumption'] = cons_dict
                return result
            return wrapper
        return real_decorator

    @classmethod
    def docker_consumption(cls, list_of_containers):
        def real_decorator(f):
            def wrapper(*args, **kwargs):
                start_cons = system.docker_get_stats(list_of_containers)
                result = f(*args, **kwargs)
                end_cons = system.docker_get_stats(list_of_containers)
                result['consumption'] = {'start': start_cons, 'end': end_cons}
                return result
            return wrapper
        return real_decorator

    @classmethod
    def tagging(cls, tag):
        def real_decorator(f):
            for key in cls.REGISTRY_ENTRY:
                if key not in REGISTRY:
                    REGISTRY[key] = {}
                REGISTRY[key][tag.lower()] = cls.REGISTRY_ENTRY[key]

            def wrapper(*args, **kwargs):
                result = {tag.lower(): f(*args, **kwargs)}
                return result
            return wrapper
        return real_decorator
