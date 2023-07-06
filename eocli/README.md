# EoCLI (yo-cli)

## Overview:
EoCLI is meant to act as your main portal to using the Eototo ml platform. It serves for
development, job monitoring, and general run commands. Although Eototo can be imported and used
as a package for various use cases EoCLI is the preferred development team supported tooling.
Please consider this as a seperate optional package within Eototo that is an extension or plugin
of the general package.

## Current Functionality:
Below lists the current functionalities of EoCLI, their purposes, and an example usage.

### CI:
EoCLI CI uses the commands below for processing during CI, this is done to create parity between
local development and usage to CI. This procedure ensures developers and users that they can rely
on Eototo passing locally and on CI ensuring working usages and consistency without having to think
about CI passing but local not or vice versa.

### Formatting:
See above, formatting ensures that the linting passes successfully as linting conforms to the standard set
out by the Formatting. Formatting takes the hard work of fixing errors out of the developers hands.

### Linting:
See above.

### Testing:
Testing through EoCLI does two things
1. ensures every user including CI has the same testing and can reasonably rely on parity across all environments
2. guarantees that the passing tests locally and on CI accurately test the required components working the default environment

### Type Checking:
See above but for type checking!