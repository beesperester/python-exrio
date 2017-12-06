""" Main python module. """

# system
import logging
import os

# filesystem
from fs.osfs import OSFS
from fs.errors import CreateFailed

# exrio
from exrio import rename_dir

def main():
    # try:
        
    # except CreateFailed as error:
    #     print error
    in_fs = OSFS(u'C:/Users/Bernhard Esperester/Desktop/wsds/scenes/UFA_WSDS_SC0110_S0010/img-cgi/lighting_UFA_WSDS_SC0110_S0010_v006_beresp/final')
    out_fs = OSFS(u'C:/Users/Bernhard Esperester/Desktop/wsds/scenes/UFA_WSDS_SC0110_S0010/img-cgi/lighting_UFA_WSDS_SC0110_S0010_v006_beresp/test_rename')

    layer_map = {
        r'^r$': 'R',
        r'^g$': 'G',
        r'^b$': 'B',
        r'^a$': 'A',
        r'diffuse': 'diffuse',
        r'shadow': 'shadow',
        r'ambient': 'emission',
        r'global illumination': 'gi',
        r'ambient occlusion': 'ao',
        r'reflection': 'reflection',
        r'refraction': 'refraction',
        r'normal pass': 'normal',
        r'position \(world\)': 'position_world',
        r'position \(camera\)': 'position_camera'
    }

    rename_dir(in_fs, out_fs, layer_map, None, int(os.environ["NUMBER_OF_PROCESSORS"]))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    main()