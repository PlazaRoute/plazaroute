import subprocess
from os.path import splitext
"""
Merge files together with osmosis
osmosis must be available in PATH!
"""


def merge_three_osm_files(out_file, *filenames):
    cmd = ['osmosis']
    for filename in filenames:
        extension = splitext(filename)[1]
        if extension == '.osm':
            cmd.append('--rx')
        else:
            cmd.append('--rb')
        cmd.append(filename)

    cmd.extend(['--merge', '--merge'])

    if splitext(out_file)[1] == '.osm':
        cmd.append('--wx')
    else:
        cmd.append('--wb')
    cmd.append(out_file)

    subprocess.run(cmd, check=True)
