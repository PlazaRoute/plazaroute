import subprocess
import logging
from os.path import splitext
"""
Merge files together with osmosis
osmosis must be available in PATH!
"""


logger = logging.getLogger('plaza_preprocessing.osmosishelper')


def merge_osm_files(out_file, *filenames):
    logger.debug(f"Merging {filenames} to {out_file}")
    cmd = ['osmosis']
    for filename in filenames:
        extension = splitext(filename)[1]
        if extension == '.osm':
            cmd.append('--rx')
        else:
            cmd.append('--rb')
        cmd.append(filename)

    # add n - 1 merge commands
    cmd.extend(['--merge'] * (len(filenames) - 1))

    if splitext(out_file)[1] == '.osm':
        cmd.append('--wx')
    else:
        cmd.append('--wb')
    cmd.append(out_file)
    try:
        # osmosis writes all output to stderr
        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
    except FileNotFoundError as not_found_error:
        logger.error("Osmosis not found, is it installed and in PATH?")
        raise not_found_error
    except subprocess.CalledProcessError as process_error:
        for error_line in process_error.stderr.splitlines():
            logger.error(f"Error with osmosis: {error_line}")
        raise process_error
