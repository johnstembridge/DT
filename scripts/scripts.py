from globals import config
import os

location = config.get('locations')['scripts']
opsys  = config.get('OS')
file_type = 'sh' if opsys == 'linux' else 'bat'


def file_name(script_name):
    return os.path.join(location, script_name + "." + file_type)