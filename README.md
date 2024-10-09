# Schema Mapping Resources

## Overview
This repository contains a collection of JSON files representing mappings between legacy schemas and updated schemas stored as CEDAR templates. The mappings are organized into two main aspects:

- *Schema Mappings*: These files map old fields from the legacy schema to their corresponding fields in the new, updated schema. This ensures that any data structured under the old schema can be correctly translated and aligned with the new schema.

- *Value Mappings*: These files map old permissible values from the legacy schema to new permissible values in the updated schema. This guarantees that any data values constrained by the old schema can be matched to appropriate values in the new schema.

## Generation
The mappings provided here were generated with the assistance of Large Language Model (LLM) tools to enhance the accuracy and efficiency of finding possible matches. These tools helped ensure the mappings reflect a close alignment between the old and new schemas that reduced manual work and improving overall consistency. However, a manual human inspection is still needed to ensure the correctness.

## Usage
Feel free to explore the JSON files in this repository for schema transformation, migration projects, or general reference when transitioning from older metadata structures to newer, more standardized formats.
