#!/usr/bin/env python
# coding: utf-8

"""
Initial version: February 2025

Creates JSON files that consolidate:
1. file names in versions of the metadata schema
2. valuesets for categorical metadata

"""

import os
import json


def getpath(dirname: str) -> str:
    """
    Returns the full path of the specified directory.
    :param dirname: name of directory.
    """
    # Get absolute path to specified directory.
    fpath = os.path.dirname(os.getcwd())
    fpath = os.path.join(fpath, dirname)
    return fpath


def getgroupedschemas() -> dict:
    """
    Obtains a list of the legacy schema files, grouped by schema.

    Assumption: a file named group_schema_mapping.json exists in the script folder.
    The format of the file is:
    {
        <group> : [list of legacy schema names]
    }
    """
    fgroup = 'group_schema_mapping.json'
    try:
        with open(fgroup) as f:
            groups = json.load(f)
        return groups

    except FileNotFoundError:
        print(f'Missing file: group_schema_mapping_json. This file groups legacy schema files.')
        exit(1)


def buildconsolidatedvalueview() -> dict:
    """
    Build a values dict, consolidating value mappings.

    """

    dictret = {}
    path = getpath(dirname='Value Mapping')
    listfieldfiles = os.listdir(path)

    for fval in listfieldfiles:
        valfile = os.path.join(path, fval)
        try:
            with open(valfile) as f:
                maps = json.load(f)
                print(maps)
                dictret[fval] = maps
        except FileNotFoundError:
            continue
    return dictret


def buildfieldsobject(listversions: list) -> dict:
    """
    Builds the field mapping of the consolidated view.
    :param listversions: A list of schema mapping file information, obtained from getgroupedschemas function.
    :return: dict in format, for fields from all versions
    {
        <name of field in a previous version of the schema>: <name of the field in the final version of the schema>
    }
    """
    dictret = {}
    listfields = []

    for version in listversions:
        fversion = os.path.join(getpath(dirname='Schema Mapping'), version)
        with open(fversion) as f:
            fieldmaps = json.load(f)
        for key in fieldmaps:
            if key not in listfields:
                listfields.append(key)
                dictret[key] = fieldmaps[key]

    return dictret


def buildconsolidatedfieldview(dictgroupedfiles: dict) -> dict:
    """
    Builds the "consolidated view"--a dictionary that describes the superset of fields that are
    in all versions of metadata schemas.
    :param dictgroupedfiles: A dictionary of schema mapping file information, formatted as described in
                             the getschemajsons function
    :return: a dict of dicts that consolidates and organizes schema information across versions
    """
    dictret = {}
    for key in dictgroupedfiles:
        if key == 'comments':
            continue

        listv = []
        versions = dictgroupedfiles[key]
        for v in versions:
            listv.append(v.split('.json')[0])
        dictret[key] = {
            'versions': listv,
            'field_mappings': buildfieldsobject(listversions=versions)
        }

    return dictret


def writeviewtojsonfile(dictview: dict, filename:str):
    """
    Writes a consolidated view dictionary to a json file.
    :param dictview: consolidated view dictionary.
    :param filename: output file name
    """
    with open(filename, 'w') as file:
        json.dump(dictview, file, indent=4)

# ----------------------------------
# MAIN


# Get grouped list of versioned schema files, ordered by version.
dictgroupschemafiles = getgroupedschemas()

consolidatedfieldview = buildconsolidatedfieldview(dictgroupedfiles=dictgroupschemafiles)
writeviewtojsonfile(dictview=consolidatedfieldview, filename='schema_fields.json')
consolidatedvalueview = buildconsolidatedvalueview()
writeviewtojsonfile(dictview=consolidatedvalueview, filename='value_fields.json')
