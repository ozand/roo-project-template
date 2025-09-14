# RooCode Project Template

This is a template for creating new projects with the RooCode framework. It provides a standardized structure and tools for project initialization, migration, and updates.

## Bootstrap Script

The `bootstrap.py` script is the primary tool for managing RooCode projects. It provides three main modes of operation:

### 1. Initialization Mode (`--init`)

Initializes a new project with the RooCode template structure:

```bash
python bootstrap.py --init
```

This mode:
- Copies template directories to your project
- Creates symbolic links for rules and commands in the pages/ directory
- Sets up the basic project structure

### 2. Migration Mode (`--migrate`)

Migrates an existing project to the RooCode template structure:

```bash
python bootstrap.py --migrate
```

This mode:
- Copies template directories to your project
- Migrates existing documentation from legacy locations to the pages/ directory
- Creates symbolic links for rules and commands in the pages/ directory

### 3. Update Mode (`--update`)

Safely updates an existing project with the latest template files while preserving user modifications:

```bash
python bootstrap.py --update
```

This mode includes advanced safety features:
- Uses SHA256 hashing to detect changes in existing files
- Only updates files that haven't been modified by the user
- Creates backup copies of files before overwriting
- Maintains a record of original template file hashes
- Provides comprehensive reporting on the update operation
- Updates symbolic links in the pages/ directory

For detailed information about the `--update` mode, see:
- [Bootstrap Update Mode Documentation](docs/.guidelines/bootstrap_update_mode.md)
- [Bootstrap Update Changelog](docs/bootstrap_update_changelog.md)

## Prerequisites

- Python 3.7 or higher
- Git

## Usage

1. Download the bootstrap script:
   ```bash
   curl -O https://raw.githubusercontent.com/ozand/roo-project-template/main/bootstrap.py
   ```

2. Run the script with the desired mode:
   ```bash
   python bootstrap.py --init    # For new projects
   python bootstrap.py --migrate # For existing projects
   python bootstrap.py --update  # For updating existing projects
   ```

## Template Structure

The template includes the following directories:

- `.roo/` - RooCode configuration and rules
- `scripts/` - Development and maintenance scripts
- `pages/` - Documentation and knowledge base files
- `docs/` - Additional documentation
- `journals/` - Daily work logs

## Contributing

To contribute to this template:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.