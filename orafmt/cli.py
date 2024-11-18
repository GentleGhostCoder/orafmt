import subprocess
import sys
from pathlib import Path
import argparse
import os


def is_valid_file(file_path: str, valid_extensions: list[str]) -> bool:
    """Check if the file has a valid extension and exists."""
    return Path(file_path).suffix[1:] in valid_extensions and Path(file_path).is_file()


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Format SQL files using SQLcl.")
    parser.add_argument(
        "--sql-program",
        type=str,
        default=os.getenv("SQL_PROGRAM", "sql"),  # Use environment variable or default to "sql"
        help="Path to the SQL program (default: 'sql' or $SQL_PROGRAM).",
    )
    parser.add_argument("files", nargs="*", help="Files to format.")
    args = parser.parse_args()

    # Define paths and configurations
    script_dir = Path(__file__).parent
    formatter_js = script_dir / "formatter" / "format.js"
    formatter_xml = script_dir / "formatter" / "trivadis_advanced_format.xml"
    sql_program = args.sql_program
    sqlcl_opts = ["-nolog", "-noupdates", "-S"]
    formatter_ext = [
        "sql", "prc", "fnc", "pks", "pkb", "trg", "vw", "tps", "tpb", "tbp",
        "plb", "pls", "rcv", "spc", "typ", "aqt", "aqp", "ctx", "dbl", "tab",
        "dim", "snp", "con", "collt", "seq", "syn", "grt", "sp", "spb", "sps", "pck"
    ]

    # Filter files to only valid ones
    valid_files = [f for f in args.files if is_valid_file(f, formatter_ext)]
    if not valid_files:
        print("No valid files provided to the formatter. Exiting.")
        sys.exit(0)

    # Format each valid file
    for file in valid_files:
        print(f"Formatting file: {file}")
        try:
            # Construct the SQL script to execute
            sql_script = f"""
                script {formatter_js} "{file}" ext={','.join(formatter_ext)} xml={formatter_xml}
                EXIT
            """
            # Execute SQLcl or the SQL application
            result = subprocess.run(
                [sql_program, *sqlcl_opts],
                input=sql_script,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Print the result
            if result.returncode != 0:
                print(f"Error formatting {file}:\n{result.stderr}")
                sys.exit(result.returncode)
            else:
                print(f"Formatted {file} successfully.")

        except FileNotFoundError:
            print(f"Error: SQL program '{sql_program}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
