import subprocess
import time
import urllib2
import docker
import wget
import socket
import os
import scripts
import ssl
import yaml
import shutil
import psutil
import configparser


config = configparser.ConfigParser()
config.read('configuration.ini')

FNULL = open(os.devnull, 'w')
client = docker.from_env()
scripts_path = scripts.__file__[:-len(scripts.__file__.split('/')[-1])]


def load_yml():
    stream = open("matrix.yml", "r")
    return yaml.load(stream)


def config_validation(section, variable):
    if section not in config:
        buf = get_env_vars(variable)
    else:
        buf = config[section][variable]
        if not buf:
            buf = get_env_vars(variable)
    return buf


def get_env_vars(key):
    buf = os.environ.get(key)
    if not buf:
        raise Exception('Variable %s is not defined.' % key)
    return buf


def get_current_time():
    return time.time()


def create_or_open_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)


def delete_dir(directory):
    try:
        shutil.rmtree(directory)
    except OSError:
        pass


def get_folder_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return transform_size(total_size)


def wget_download(directory, url):
    create_or_open_dir(directory)
    wget.download(url)


def docker_compose_command(command, directory, method='call'):
    create_or_open_dir(directory)
    getattr(subprocess, method)(('docker-compose %s' % command).split(),
                                stdout=FNULL, stderr=subprocess.STDOUT)


def docker_pull(url):
    client.images.pull(url)


def libcloud_bash_command(script, path, env_name):
    create_or_open_dir(path)
    subprocess.call(('bash %slibcloud/%s.sh %s %s' % (scripts_path, script, path, env_name)).split(),
                    stdout=FNULL, stderr=subprocess.STDOUT)


def docker_run(image, port):
    client.containers.run(image=image, privileged=True, detach=True, ports=port)


def docker_create_user(directory, login, password):
    create_or_open_dir(directory)
    subprocess.call(('bash %smistio/create_mistio_user.sh %s %s' % (scripts_path, login, password)).split(),
                    stdout=FNULL, stderr=subprocess.STDOUT)


def docker_get_images_sizes(name):
    total_size = 0
    for image in client.images.list():
        if hasattr(image, 'tags'):
            if any(name in s for s in image.tags):
                total_size += image.attrs['Size']
    return transform_size(total_size)


def docker_get_container(container_id):
    return client.containers.get(container_id)


def docker_get_stats(list_of_containers):
    cons_dict = {}
    for container in list_of_containers:
        container_object = docker_get_container(container)
        stats = container_object.stats(stream=False)
        cons_dict[container] = {'cpu_stats': stats['cpu_stats'],
                                'memory_stats': stats['memory_stats'],
                                'image': get_container_image(container_object)}
    return cons_dict


def get_container_image(container):
    return container.attrs['Config']['Image']


def docker_containers_get(name):
    list_of_containers = []
    for container in client.containers.list():
        if name in get_container_image(container):
            list_of_containers.append(container)
    return list_of_containers


def docker_container_stop_and_delete(name):
    for container in docker_containers_get(name):
        container.remove(force=True)


def docker_delete_images():
    for image in client.images.list():
        client.images.remove(image.short_id, force=True)


def get_python_usage():
    pid = os.getpid()
    py = psutil.Process(pid)
    return {'memory_use': py.memory_info(), 'memory_percent': py.memory_percent(),
            'cpu_use': py.cpu_times(), 'cpu_percent': py.cpu_percent(interval=1.0)}


def transform_size(size):
    size = float(size)
    if size/1000 < 1:
        return size, 'B'
    size /= 1000
    if size/1000 < 1:
        return size, 'KB'
    size /= 1000
    if size/1000 < 1:
        return size, 'MB'
    size /= 1000
    if size/1000 < 1:
        return size, 'GB'


def wait_service(url, ssl_enable=True):
    while True:
        try:
            if ssl_enable:
                if urllib2.urlopen(url).getcode() == 200:
                    return
            else:
                context = ssl._create_unverified_context()
                if urllib2.urlopen(url, context=context).getcode() == 200:
                    return
        except (urllib2.URLError, socket.SO_ERROR):
            time.sleep(0.5)


def create_file_with_size_kb(size):
    with open(str(size) + '_KB', 'wb') as f:
        f.seek(size*1000)
        f.write('0')
