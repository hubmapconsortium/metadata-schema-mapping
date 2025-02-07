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
    parser = argparse.ArgumentParser(description='Create consolidated view showing evolution of '
                                                 'legacy metadata schema.',
                                     formatter_class=RawTextArgumentDefaultsHelpFormatter)
    parser.add_argument('dataset_type', help='dataset_type to which one or more legacy metadata schema belong')
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


def getgroupedschemas(group: str) -> list[str]:
    """
    Obtains a list of the legacy schemas associated with a group.
    :param group: name of the group

    Assumption: a file named group_schema_mapping.json exists in the script folder.
    The format of the file is:
    {
        <group> : [list of legacy schema names]
    }
    """
    listret = []
    fgroup = 'group_schema_mapping.json'
    try:
        with open(fgroup) as f:
            groups = json.load(f)
            if group in groups.keys():
                listret = groups.get(group)
        return listret

    except FileNotFoundError:
        print(f'Missing file: group_schema_mapping_json. This file groups legacy schema files.')
        exit(1)


def getschemafilenames(group: str) -> list[str]:

    """
    Builds a list of file names of versions of the specified metadata schema.
    :param group: name of a term used to gropu schema--i.e., the dataset_type.
    :return: list

    Assumptions:
    1. Schema files are named in format {schema}-v{version number}.json.
    2. Schema files are in the 'Schema Mapping' folder of the local repo.
    """

    # Get the subset of legacy schemas that associate with the specified group.
    groupedschemas = getgroupedschemas(group=group)

    listret = []

    # Get the complete list of files in the schema mapping directory.
    allschemas = os.listdir(getschemadir())

    # Build list of tuples of information on files that correspond to the grouped legacy schemas.
    # The tuple will include:
    # 1. file name
    # 2. file version number, parsed from the file name

    listfile = []

    for gschema in groupedschemas:
        for sch in allschemas:
            if gschema in sch:
                # Parse version number.
                version = sch.split('.json')[0].split('-')[-1]
                version = int(version[1:len(version)])
                listfile.append((sch, version))

    # Sort files by file name, then version number. This allows for correct numerical sorting for the case where the
    # number of versions of a file > 9.
    listsort = sorted(listfile, key=itemgetter(0, 1))
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
            listret.append({'file': schfile.split('.json')[0],
                            'content': json.load(f)})
    return listret


def buildvaluesobject(field: str) -> dict:
    """
    Build a 'values' object, containing the superset of all values from prior versions of schemas that are possible
    for a field in the latest schema.

    Format of return dictionary:
    {
        <name of value in latest schema>: <list of synonymous values from prior versions>
    }

    :param field:
    :return:
    """
    return {}

def buildfieldsobject(listversions: list) -> list:
    """
    Builds the fields list of the consolidated view.
    :param listversions: A list of schema mapping file information, formatted as described in the getschemajsons
                         function
    :return: list of dicts in format
    {
        'name': <name of field>,
        'prior_versions': <list of versions in which the field appears>,
        'values': <values dict for field>
    }
    """
    listfields = []
    listret = []

    # Build a "final field superset"--i.e., a consolidated list, sorted alphabetically, of the fields that are in
    # the final version of the schema for the group.
    # First, complile unsorted field list with duplicates.
    for schemafile in listversions:
        content = schemafile.get('content')
        # Get all fields.
        # Each non-null value in a versioned schema JSON corresponds to a field in the final version of the schema.
        for key in content:
            if content[key] is not None:
                listfields.append(content[key])

    # Drop duplicates, using a set.
    setfields = set(listfields)
    # Convert the set back to a list using unpack operator and sort.
    supersetfields = sorted([*setfields])

    # For each field in the final field superset, loop through each versioned schema file to document the
    # evolution of the field.
    # 1. If the field corresponds to a value in the previous version of a schema file, the field is in both the
    #    final schema and the previous schema.
    #    The key for the matched value corresponds to what the field was named in the previous schema.
    # 2. If the field does not correspond to a value in the previous version of a schema file, the field was
    #    introduced after the previous schema.

    for field in supersetfields:
        dictfield = {'name': field}
        setprior = set()
        for schemafile in listversions:
            content = schemafile.get('content')
            if field in content.values():
                previousfield = list(content.keys())[list(content.values()).index(field)]
                print(previousfield)
            else:
                previousfield = ''
            # Build unique set of field names from previous versions.
            setprior.add(previousfield)
            # Convert set to list with unpacking operator.
        dictfield['prior_versions'] = [*setprior]
        dictfield['values'] = buildvaluesobject(field)
        listret.append(dictfield)

    return listret

def buildconsolidatedview(name: str, listversions: list) -> dict:
    """
    Builds the "consolidated view"--a dictionary that describes the superset of fields and categorical values that are
    in all versions of a metadata schema.

    :param name: name of the group of legacy schema files--e.g., a dataset_type
    :param listversions: A list of schema mapping file information, formatted as described in the getschemajsons
                         function
    :return: a dict that consolidates and organizes schema information across versions
    """
    listv = []
    for schfile in listversions:
        listv.append(schfile.get('file').split('.json')[0])
    dictret = {
        'schema': name,
        'legacy_schemas': listv,
        'fields': buildfieldsobject(listversions=listversions)
    }

    return dictret
# ----------------------------------
# MAIN


# Obtain schema for which to create consolidated view.
args = getargs()
dataset_type = args.dataset_type
print(f'Creating consolidated view for dataset_type {dataset_type}.')

# Get list of versioned schema files, ordered by version.
listschemafiles = getschemafilenames(group=dataset_type)

# Read schema files.
listschemaversions = getschemajsons(listfiles=listschemafiles)

consolidatedview = buildconsolidatedview(name=dataset_type, listversions=listschemaversions)
print(consolidatedview)
