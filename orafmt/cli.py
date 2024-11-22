import subprocess
import sys
from pathlib import Path
import argparse
import os
import tempfile


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
    module_dir = Path(__file__).parent.resolve()  # Module directory
    formatter_js = module_dir / "formatter" / "format.js"
    formatter_xml = module_dir / "formatter" / "trivadis_advanced_format.xml"
    arbori_file = module_dir / "formatter" / "trivadis_custom_format.arbori"
    sql_program = args.sql_program
    sqlcl_opts = ["-nolog", "-noupdates", "-S"]
    formatter_ext = (
        "sql,prc,fnc,pks,pkb,trg,vw,tps,tpb,tbp,plb,pls,rcv,spc,typ,"
        "aqt,aqp,ctx,dbl,tab,dim,snp,con,collt,seq,syn,grt,sp,spb,sps,pck"
    )

    # Ensure formatter and configuration exist
    if not formatter_js.is_file():
        print(f"Error: Formatter script '{formatter_js}' not found.")
        sys.exit(1)

    if not formatter_xml.is_file():
        print(f"Error: Formatter configuration '{formatter_xml}' not found.")
        sys.exit(1)

    # Check if any files are provided
    if not args.files:
        print("No files provided for formatting. Exiting.")
        sys.exit(0)

    # Create a temporary JSON file containing the files to be formatted
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json") as temp_file:
        json_file_path = temp_file.name
        json_content = [Path(f).resolve().as_posix() for f in args.files]
        temp_file.write("[\n")
        temp_file.write(",\n".join(f'  "{f}"' for f in json_content))
        temp_file.write("\n]")

    # Construct the SQL script content
    sql_script_content = f"""
script {formatter_js.as_posix()} "{json_file_path}" ext={formatter_ext} xml={formatter_xml.as_posix()} arbori={arbori_file}
EXIT
"""

    try:
        # Run SQLcl with the constructed SQL script content
        print(f"Running SQLcl to format files with dynamically constructed SQL script...")
        result = subprocess.run(
            [sql_program, *sqlcl_opts],
            input=sql_script_content,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
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
        if Path(json_file_path).exists():
            os.remove(json_file_path)


if __name__ == "__main__":
    main()
