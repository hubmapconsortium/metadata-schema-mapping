# Metadata Schema Mapping
## Consolidation script
# Objectives
## User Stories
1. For a given metadata schema, I want to know:
   - all prior versions of the schema 
   - fields organized by schema version 
   - the evolution of a field through the schema versions, including 
      - in what schema version the field first appeared 
      - how the field name changed 
      - whether the field disappeared (was deprecated), and in what version
   - all values for a field, regardless of schema version
2. I want to be able to update to the current metadata schema the metadata fields for a dataset that was ingested under a prior version of the schema.


## Example inquiries

1. In which version of the ims-desi schema did the field "ms_source" become "ms_ionization_technique"? (*Answer: v1*)
2. What is the history of the "version" field in the ims-desi scehma? (*Answer: added in v1; deprecated in v2.*)
3. What are all the acquisition instrument vendor names that we've used for what we now call "Thermo Fisher Scientific" in ims-desi? (*Answer: "Thermo Fisher", "Thermo Fisher Scientific"*)

# Resources

This repo describes mappings between versions of metadata schema for fields and (categorical) values.

## Challenges

1. There is a schema field mapping file for each version of a schema. Each file shows mappings between a version and the current version, but not between versions.
2. If a field name changed, it is necessary to allow for searching on either name.

# Solution

Develop a Python script that uses the metadata schema mapping files to generate a consolidated view of all fields and values for a schema. 

The consolidated view would:

- flatten fields at the schema level, but for each field
- show all schema versions that contain the field
- if the field name changed, show all versions of the field
- flatten values at the schema level

# Example consolidated view as JSON
See example_metadata_mapping.json in this folder.
(The **use_case** object is for purposes of documentation of the example.)

The JSON structure accounts for the following known use cases:

1. A field has the same name in all versions. 
2. A field changed name between versions. 
3. Field creation/deprecation:
   - A field was deprecated between the initial version and the next version. 
   - A field was introduced in an intermediate version, but deprecated before the final version. 
   - A new field was created in the final version.
