# Bootstrap Update Mode Documentation

## Overview

The `bootstrap.py` script now includes a `--update` mode that provides safe template updates for existing projects. This mode allows you to synchronize your project with the latest template files while preserving any modifications you've made to existing files.

## Key Features

- **Safe File Updates**: Only updates files that haven't been modified by the user
- **User Modification Detection**: Uses SHA256 hashing to detect changes in existing files
- **Automatic Backups**: Creates backup copies of files before overwriting
- **Template Hash Tracking**: Maintains a record of original template file hashes
- **Comprehensive Reporting**: Provides detailed statistics about the update operation
- **Symbolic Link Management**: Updates symbolic links in the pages/ directory

## How It Works

### 1. File Hashing System

The update mode uses SHA256 hashing to track the original state of template files:

1. During the first update, it calculates and stores hashes of all template files in `.roo/.template_hashes.json`
2. On subsequent updates, it compares current file hashes with stored hashes to detect modifications
3. Only files that haven't been modified are updated

### 2. Update Process

1. **Clone Template Repository**: Downloads the latest template from the specified repository
2. **File Analysis**: Scans all template directories and compares with existing project files
3. **Modification Detection**: Checks each existing file against stored hashes
4. **Safe Copying**: 
   - Adds new files that don't exist in the project
   - Updates existing files only if they haven't been modified
   - Skips files that have user modifications
   - Creates backups before overwriting any files
5. **Symbolic Link Update**: Refreshes symbolic links in the pages/ directory
6. **Report Generation**: Provides statistics on added, updated, and skipped files

## Usage

### Basic Update Command

```bash
python bootstrap.py --update
```

### Update with Custom Repository

```bash
python bootstrap.py --update --repo https://github.com/user/custom-template.git
```

## Update Statistics

The update mode provides detailed statistics at the end of the operation:

- **Added files**: New files that were added to the project
- **Updated files**: Existing files that were updated (unmodified files)
- **Skipped files**: Files that were not updated because they were modified by the user
- **Errors**: Any errors that occurred during the update process

## Safety Features

### 1. User Modification Protection

Files that have been modified by the user are never overwritten. Instead, they are skipped with a notification.

### 2. Backup System

Before any file is updated, a backup copy is created with a `.backup` extension.

### 3. Template Hash Persistence

File hashes are stored in `.roo/.template_hashes.json` to track the original state of files across multiple update operations.

## When to Use Update Mode

Use the `--update` mode when you want to:

1. Add new template files that were introduced in the latest version
2. Update existing template files that you haven't modified
3. Refresh symbolic links and other template metadata
4. Synchronize your project with the latest template improvements

## Best Practices

### 1. Regular Updates

Run the update mode periodically to keep your project synchronized with the latest template improvements.

### 2. Review Skipped Files

After an update, review the skipped files to manually merge any important template changes.

### 3. Backup Your Project

Although the update mode is safe, always ensure your project is backed up before running updates.

### 4. Check Update Reports

Review the statistics provided at the end of the update to understand what changes were made.

## Troubleshooting

### No Files Updated

If no files are updated, it may be because:
- All existing files have been modified by the user
- The template repository hasn't changed since the last update
- There may be network issues accessing the template repository

### Hash File Issues

If there are issues with the template hash file (`.roo/.template_hashes.json`):
- The system will continue to work but may be less accurate in detecting modifications
- You can delete the file to start fresh with a new update operation

## Example Output

```
--- 🔄 Updating existing project with latest RooCode template ---

📁 Processing directory: .roo
  ✅ Added new file: rules/new_guideline.md
  🔄 Updated file: rules/existing_guideline.md
  ⏭️  Skipped modified file: rules/customized_guideline.md

📁 Processing directory: scripts
  ✅ Added new file: development/new_script.py

📊 Update Summary:
   ✅ Added files: 2
   🔄 Updated files: 1
   ⏭️  Skipped files (user modified): 1

✅ Project update completed successfully!
```

## Limitations

1. **Manual Merge Required**: Files with user modifications must be manually updated to incorporate template changes
2. **Directory Structure Dependent**: Only works with the standard RooCode template directory structure
3. **Hash-based Detection**: Relies on file hashing which may not detect all types of modifications in complex scenarios