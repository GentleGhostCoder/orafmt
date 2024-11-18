import subprocess
import sys
from pathlib import Path


def main():
    # Define paths and configurations
    script_dir = Path(__file__).parent
    formatter_js = script_dir / "formatter" / "format.js"
    formatter_xml = script_dir / "formatter" / "trivadis_advanced_format.xml"
    sql_program = "sql"  # Default to "sql". Update this if needed.
    sqlcl_opts = ["-nolog", "-noupdates", "-S"]
    formatter_ext = "sql,prc,fnc,pks,pkb,trg,vw,tps,tpb,tbp,plb,pls,rcv,spc,typ,aqt,aqp,ctx,dbl,tab,dim,snp,con,collt,seq,syn,grt,sp,spb,sps,pck"

    # Check if files are provided
    if len(sys.argv) < 2:
        print("No files provided to the formatter. Exiting.")
        sys.exit(0)

    # Format each file
    for file in sys.argv[1:]:
        print(f"Formatting file: {file}")
        try:
            # Construct the SQL script to execute
            sql_script = f"""
                script {formatter_js} "{file}" ext={formatter_ext} xml={formatter_xml}
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
