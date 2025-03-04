# SQL Formatter Pre-Commit Hook

This repository includes a pre-configured pre-commit hook to automatically format SQL and PL/SQL files before each commit, ensuring consistent code style across the project. It leverages Trivadis' advanced format settings for alignment, spacing, and other formatting standards.

## Features

- **Automatic Formatting**: Formats SQL files with specified extensions to maintain code consistency.
- **Supported File Types**: Includes common SQL and PL/SQL file extensions such as `.sql`, `.prc`, `.fnc`, `.pks`, `.pkb`, `.trg`, `.pls`, and more.
- **Configurable Settings**: Uses `trivadis_advanced_format.xml` for advanced formatting configurations, which can be customized as needed.
- **Flexible SQLcl Path**: Allows specifying the SQLcl path using the `SQL_PROGRAM` environment variable.

## Requirements

### SQLcl

This pre-commit hook requires Oracle SQLcl (SQL Command Line) to perform SQL formatting. SQLcl provides powerful SQL scripting and formatting capabilities. Follow these steps to download and install it:

- **Download SQLcl**: The latest version can be downloaded from [Oracle SQLcl Downloads](https://www.oracle.com/database/sqldeveloper/technologies/sqlcl/download/).
- **Install SQLcl**: Refer to the [installation guide](https://docs.oracle.com/en/database/oracle/sqlcl/19.4/sclsg/installing-and-getting-started-with-sqlcl.html) if needed.
  - Version 23.4 are supported - https://www.oracle.com/sqlcl/download/sqlcl-downloads-23.4.html

#### Optional: Set SQLcl Path

If SQLcl is not in your system PATH or if you want to specify a custom path, set the `SQL_PROGRAM` environment variable to the path of the `sql` binary. For example:

```bash
export SQL_PROGRAM="/path/to/sqlcl/bin/sql"
```

### Git

Ensure Git is installed as this pre-commit hook uses Git’s pre-commit hook system.

## Installation

To use this hook with `pre-commit`, add it to your `.pre-commit-config.yaml` file in the target repository. Here’s an example configuration:

```yaml
# .pre-commit-config.yaml
repos:
- repo: https://github.com/GentleGhostCoder/oracle-formatter-pre-commit-hook  # Replace with your GitHub repo URL
  rev: v1.0.0  # Use a tag, branch name, or commit SHA
  hooks:
    - id: oracle-formatter-hook
```

Then, install the hook by running:

```bash
pre-commit install
```

This command sets up the pre-commit hook to run automatically before each commit.

## How It Works

1. **Identify Relevant Files**: The hook detects files based on specified extensions.
2. **Format Files**: Each identified file is formatted using `formatter/format.js` via SQLcl, applying the settings in `trivadis_advanced_format.xml`.

## Usage

1. **Stage SQL Files**: Stage files for commit using `git add`.
2. **Commit Changes**: Commit staged files with `git commit`. The pre-commit hook will automatically format applicable files.

### Running Manually with `--all-files`

To format all files, not just staged files, you can run the pre-commit hook manually:

```bash
pre-commit run --all-files
```

This triggers the formatting of all files matching the specified extensions in the repository.

### Manual Formatting with the Python Entry Point

To manually format files without running the pre-commit hook, use the `orafmt` command directly if your module is installed:

```bash
orafmt file1.sql file2.sql
```

Alternatively, you can use the Python script directly:

```bash
python3 -m orafmt file1.sql file2.sql
```

This command will format the specified files according to the configurations.

## Advanced Configuration

To modify formatting settings, edit the `trivadis_advanced_format.xml` file. These options allow customization of alignment, line breaks, and spacing based on project needs.

## License

This formatter uses Trivadis PL/SQL Formatter, licensed under the Apache License, Version 2.0.  
The pre-commit hook itself is also available under the Apache License, Version 2.0.
