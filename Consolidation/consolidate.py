#!/usr/bin/env python
# coding: utf-8

"""
Initial version: February 2025

Creates a JSON file that consolidates for a specified metadata schema:
1. versions of the metadata schema
2. valuesets for categorical metadata

"""

import argparse
import os
from operator import itemgetter
import json


class RawTextArgumentDefaultsHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawTextHelpFormatter
):
    pass


def getargs() -> argparse.Namespace:

    # Parse arguments.
    parser = argparse.ArgumentParser(description='Create consolidated view JSON for specified metadata schema.',
                                     formatter_class=RawTextArgumentDefaultsHelpFormatter)
    parser.add_argument('schema')
    argsret = parser.parse_args()

    return argsret


def getschemadir() -> str:
    """
    Returns the name of the directory that contains schema files.
    """
    # Get absolute path to schema directory.
    fpath = os.path.dirname(os.getcwd())
    fpath = os.path.join(fpath, 'Schema Mapping')
    return fpath


def getschemafilenames(sch_name: str) -> list[str]:

    """
    Builds a list of file names of versions of the specified metadata schema.
    :param sch_name: name of the schema
    :return: list

    Assumptions:
    1. Schema files are named in format {schema}-v{version number}.json.
    2. Schema files are in the 'Schema Mapping' folder of the local repo.
    """

    listret = []

    # Get the list of files and directories in the specified path.
    content_list = os.listdir(getschemadir())

    # Build list of tuples of information on files that correspond to the specified schema.
    # The tuple will include:
    # 1. file name
    # 2. file version number parsed from the file name

    listfile = []
    for item in content_list:
        if sch_name in item:
            # Parse version number.
            version = item.split('.json')[0].split('-')[-1]
            version = int(version[1:len(version)])
            listfile.append((item, version))

    # Sort files by the version number. This allows for correct numerical sorting for the case where the
    # number of versions > 9.
    listsort = sorted(listfile, key=itemgetter(1))
    for ls in listsort:
        listret.append(ls[0])

    return listret


def getschemajsons(listfiles: list) -> list[dict]:
    """
    Builds a list of content for a specified set of JSON files.
    :param listfiles: list of file names to read
    :return: list of dicts corresponding to the JSON content of the files.

    Format:
    [
        {
            'file': <file name>,
            'content': <dict from JSON content of file>
        }
    ]

    """

    listret = []
    for schfile in listfiles:
        fin = os.path.join(getschemadir(), schfile)
        with open(fin) as f:
            listret.append({'file': schfile,
                            'content': json.load(f)})
    return listret

# ----------------------------------
# MAIN


# Obtain schema for which to create consolidated view.
args = getargs()
schema = args.schema
print(f'Creating consolidated view for {schema}.')

# Get list of versioned schema files, ordered by version.
listschemafiles = getschemafilenames(sch_name=schema)

# Read schema files.
listschemas = getschemajsons(listfiles=listschemafiles)
print(listschemas)
