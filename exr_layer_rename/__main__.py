""" Main python module. """

# regex
import re
import copy

# exr
import OpenEXR

# filesystem
from fs.osfs import OSFS

def main():
    exr_fs = OSFS(u'C:/Users/Bernhard Esperester/Desktop/wsds/scenes/UFA_WSDS_SC0110_S0010/img-cgi/lighting_UFA_WSDS_SC0110_S0010_v005_beresp/final')

    # for file in exr_fs.walk.files(filter=['*.exr']):
    #     print file

    openexr_file = OpenEXR.InputFile(exr_fs.getsyspath(u'lighting_UFA_WSDS_SC0110_S0010_v005_beresp_1000.exr'))

    layer_map = {
        'r': 'R',
        'g': 'G',
        'b': 'A',
        'a': 'A',
        # 'diffuse': 'diffuse',
        # 'shadow': 'shadow',
        # 'ambient': 'emission',
        # 'global illumination': 'gi',
        # 'ambient occlusion': 'ao',
        # 'reflection': 'reflection',
        # 'refraction': 'refraction',
        # 'normal pass': 'normal',
        # 'position \(world\)': 'position_world',
        # 'position \(camera\)': 'position_camera'
    }

    openexr_header = openexr_file.header()
    channels = openexr_header['channels']

    # (r, g, b, a) = openexr_file.channels("RGBA")
    # print len(r), len(g), len(b), len(a)

    new_openexr_header = copy.deepcopy(openexr_header)
    # new_openexr_header['channels'] = {}

    new_openexr_file = OpenEXR.OutputFile(exr_fs.getsyspath(u'test.exr'), new_openexr_header)

    (r, g, b, a) = openexr_file.channels("RGBA")

    new_openexr_file.writePixels({'R': r, 'G': g, 'B': b, 'A': a})

    new_openexr_file.close()

    # matched_layers = {}

    # for layer_name, value in channels.iteritems():
    #     for pattern, replacement in layer_map.iteritems():
    #         if re.search(r'{}'.format(pattern), layer_name, flags=re.IGNORECASE):
    #             split_channel = layer_name.split('.')
                
    #             renamed_layer_name = '{layer_name}.{channel_name}'.format(layer_name=replacement, channel_name=split_channel[-1])

    #             # insert renamed channel into header with old channel value
    #             new_openexr_header['channels'].update({
    #                 renamed_layer_name: value
    #             })

    #             # store renamed layer with data
    #             matched_layers[renamed_layer_name] = openexr_file.channel(layer_name)

    # new_openexr_file = OpenEXR.OutputFile(exr_fs.getsyspath(u'test.exr'), new_openexr_header)

    # new_openexr_file.writePixels(matched_layers)

    # new_openexr_file.close()

if __name__ == '__main__':
    main()