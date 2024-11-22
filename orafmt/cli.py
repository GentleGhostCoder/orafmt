import platform
import subprocess
import sys
from pathlib import Path
import argparse
import os
import tempfile
import shutil


def escape_path(path: Path) -> str:
    """Double-escape paths for SQLcl compatibility."""
    if platform.system() == "Windows":
        return str(path).replace("\\", "\\\\")  # Double escape backslashes for Windows
    return str(path)  # No additional escaping needed for Linux


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Format SQL files using SQLcl.")
    parser.add_argument(
        "--sql-program",
        type=str,
        default=os.getenv("SQL_PROGRAM", shutil.which("sql")),  # Use env var or default to "sql"
        help="Path to the SQL program (default: 'sql' or $SQL_PROGRAM).",
    )
    parser.add_argument("files", nargs="*", help="Files to format.")
    args = parser.parse_args()

    # Define paths and configurations
    module_dir = Path(__file__).parent.resolve()
    formatter_js = module_dir / "formatter" / "format.js"
    formatter_xml = module_dir / "formatter" / "trivadis_advanced_format.xml"
    arbori_file = module_dir / "formatter" / "trivadis_custom_format.arbori"
    sql_program = args.sql_program
    sqlcl_opts = ["-nolog", "-noupdates", "-S"]
    formatter_ext = (
        "sql,prc,fnc,pks,pkb,trg,vw,tps,tpb,tbp,plb,pls,rcv,spc,typ,"
        "aqt,aqp,ctx,dbl,tab,dim,snp,con,collt,seq,syn,grt,sp,spb,sps,pck"
    )

    # Validate required files
    for path, label in [(formatter_js, "Formatter JS"), (formatter_xml, "Formatter XML")]:
        if not path.is_file():
            print(f"Error: {label} '{path}' not found.")
            sys.exit(1)

    # Check if any files are provided
    if not args.files:
        print("No files provided for formatting. Exiting.")
        sys.exit(0)

    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json") as temp_file:
        json_file_path = Path(temp_file.name).resolve()
        json_content = [escape_path(Path(f).resolve()) for f in args.files]
        temp_file.write("[\n")
        temp_file.write(",\n".join(f'  "{f}"' for f in json_content))
        temp_file.write("\n]")

    # Construct SQL script content
    arbori_arg = f"arbori={escape_path(arbori_file)}" if arbori_file.is_file() else ""
    sql_script_content = f"""
script {escape_path(formatter_js)} "{escape_path(json_file_path)}" ext={formatter_ext} xml={escape_path(formatter_xml)} {arbori_arg}
EXIT
"""

    try:
        # Run SQLcl with the constructed SQL script content
        print("Running SQLcl to format files with dynamically constructed SQL script...")

        result = subprocess.run(
            [sql_program, *sqlcl_opts],
            input=sql_script_content,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
        )

        # Handle SQLcl output
        if result.returncode != 0:
            print(f"SQLcl failed with error:\n{result.stderr}")
            sys.exit(result.returncode)
        else:
            print(f"Formatting completed successfully. Output:\n{result.stdout}")

    except FileNotFoundError:
        print(f"Error: SQL program '{sql_program}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Clean up the temporary JSON file
        try:
            if json_file_path.exists():
                os.remove(json_file_path)
        except Exception as cleanup_error:
            print(f"Failed to clean up temporary JSON file: {cleanup_error}")


if __name__ == "__main__":
    main()
