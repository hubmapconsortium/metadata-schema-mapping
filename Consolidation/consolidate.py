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
    parser.add_argument('group', help='group to which one or more legacy metadata schema belong--'
                                      'e.g., dataset_type')
    argsret = parser.parse_args()

    return argsret


def getpath(dirname: str) -> str:
    """
    Returns the full path of the specified directory.
    :param dirname: name of directory.
    """
    # Get absolute path to specified directory.
    fpath = os.path.dirname(os.getcwd())
    fpath = os.path.join(fpath, dirname)
    return fpath


def getgroupedschemas(groupname: str) -> list[str]:
    """
    Obtains a list of the legacy schemas associated with a group.
    :param groupname: name of the group

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
            if groupname in groups.keys():
                listret = groups.get(group)
        return listret

    except FileNotFoundError:
        print(f'Missing file: group_schema_mapping_json. This file groups legacy schema files.')
        exit(1)


def getschemafilenames(groupname: str) -> list[str]:

    """
    Builds a list of file names of versions of the specified metadata schema.
    :param groupname: name of a term used to gropu schema--i.e., the dataset_type.
    :return: list

    Assumptions:
    1. Schema files are named in format {schema}-v{version number}.json.
    2. Schema files are in the 'Schema Mapping' folder of the local repo.
    """

    # Get the subset of legacy schemas that associate with the specified group.
    groupedschemas = getgroupedschemas(groupname=groupname)

    listret = []

    # Get the complete list of files in the schema mapping directory.
    allschemas = os.listdir(getpath(dirname='Schema Mapping'))

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
        fin = os.path.join(getpath(dirname='Schema Mapping'), schfile)
        with open(fin) as f:
            listret.append({'file': schfile.split('.json')[0],
                            'content': json.load(f)})
    return listret


def buildvaluesobject(field: str) -> dict:
    """
    Build a 'values' object, containing information on the superset of fields in all versions of the schema.

    The format of the return matches that of files in the Value Mapping folder:
    {
        <name of value in a prior version>: <name(s) of values in the final version>
    }

    A list for final version names corresponds to an ambiguous mapping that will require
    :param field: name of a field
    """

    # Look for the value mapping file for the field. Only fields with categorical values will have value mapping fields.
    # Read the value mapping field.

    groupedvalues = {}
    valfile = f'{field}.json'
    fval = os.path.join(getpath(dirname='Value Mapping'), valfile)
    try:
        with open(fval) as f:
            maps = json.load(f)
            return maps

    except FileNotFoundError:
        # Field is not categorical
        return groupedvalues


def buildfieldsobject(listversions: list) -> list:
    """
    Builds the fields list of the consolidated view.
    :param listversions: A list of schema mapping file information, formatted as described in the getschemajsons
                         function
    :return: list of dicts in format
    {
        'name': <name of field in a previous version of the schema>,
        'final_version': <name of the field in the final version of the schema>,
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
        # Each key in a versioned schema JSON corresponds to a field in a previous version of the schema.
        for key in content:
            if content[key] is not None:
                listfields.append(key)

    # Drop duplicates, using a set.
    setfields = set(listfields)
    # Convert the set back to a list using unpack operator and sort.
    supersetfields = sorted([*setfields])

    # For each field in the final field superset, loop through each versioned schema file to document the
    # evolution of the field.
    # 1. If the field corresponds to a key in the previous version of a schema file, the field was in the
    #    previous schema.
    #    The value for the matched key corresponds to what the field was named in the previous schema.
    # 2. If the field does not correspond to a key in the previous version of a schema file, the field was not
    #    in the previous schema.

    for field in supersetfields:
        dictfield = {'name': field}
        setmatches = set()
        listmatches = []
        for schemafile in listversions:
            content = schemafile.get('content')
            if field in content.keys():
                # The field was in the previous schema. Check for a corresponding field in the final schema.
                setmatches.add(content[field])
            # Assumption: a field in a prior version of a schema will match, at most, one field in the final schema.
            # i.e., field a in version 1 and a in version 2 will both match to field b in final.
            # Convert set to list and take the first element.
            listmatches = [*setmatches]
        dictfield['final_version'] = listmatches[0]
        dictfield['mapped_values'] = buildvaluesobject(field)
        listret.append(dictfield)

    return listret


def buildconsolidatedview(groupname: str, listversions: list) -> dict:
    """
    Builds the "consolidated view"--a dictionary that describes the superset of fields and categorical values that are
    in all versions of a metadata schema.

    :param groupname: name of the group of legacy schema files--e.g., a dataset_type
    :param listversions: A list of schema mapping file information, formatted as described in the getschemajsons
                         function
    :return: a dict that consolidates and organizes schema information across versions
    """
    listv = []
    for schfile in listversions:
        listv.append(schfile.get('file').split('.json')[0])
    dictret = {
        'schema': groupname,
        'prior_versions': listv,
        'fields': buildfieldsobject(listversions=listversions)
    }

    return dictret


def writeviewtojsonfile(dictview: dict):
    """
    Writes a consolidated view dictionary to a json file.
    :param dictview: consolidated view dictionary.
    """
    fout = dictview.get('schema') + '.json'
    with open(fout, 'w') as file:
        json.dump(dictview, file, indent=4)

# ----------------------------------
# MAIN


# Obtain schema for which to create consolidated view.
args = getargs()
group = args.group
print(f'Creating consolidated view for group {group}.')

# Get list of versioned schema files, ordered by version.
listschemafiles = getschemafilenames(groupname=group)

# Read and consolidate schema files.
listschemaversions = getschemajsons(listfiles=listschemafiles)
consolidatedview = buildconsolidatedview(groupname=group, listversions=listschemaversions)

writeviewtojsonfile(dictview=consolidatedview)
