# Documentation

This directory contains documentation for the RooCode project template and its components.

## Table of Contents

- [Bootstrap Update Mode](.guidelines/bootstrap_update_mode.md) - Detailed documentation for the bootstrap script's update functionality
- [Bootstrap Update Changelog](bootstrap_update_changelog.md) - Comprehensive changelog and documentation for the bootstrap script's update mode

## Overview

The documentation in this directory provides guidance on using and maintaining the RooCode project template, with a particular focus on the bootstrap script and its various modes of operation.

## Bootstrap Script Documentation

The bootstrap script (`bootstrap.py`) is a key component of the RooCode project template that provides three main modes of operation:

1. **--init mode**: Initializes a new project with the RooCode template structure
2. **--migrate mode**: Migrates an existing project to the RooCode template structure
3. **--update mode**: Safely updates an existing project with the latest template files while preserving user modifications

The `--update` mode is particularly powerful as it:
- Uses SHA256 hashing to detect changes in existing files
- Only updates files that haven't been modified by the user
- Creates backup copies of files before overwriting
- Maintains a record of original template file hashes
- Provides comprehensive reporting on the update operation
- Updates symbolic links in the pages/ directory

For detailed information about the `--update` mode, see:
- [Bootstrap Update Mode Documentation](.guidelines/bootstrap_update_mode.md)
- [Bootstrap Update Changelog](bootstrap_update_changelog.md)