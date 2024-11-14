#!/bin/sh

# Define paths for SQLcl and formatter configurations
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORMATTER_JS=$(cygpath -w "$SCRIPT_DIR/formatter/format.js" 2>/dev/null || echo "$SCRIPT_DIR/formatter/format.js")
SQL_PROGRAM="${SQL_PROGRAM:-sql}"  # Use the SQL_PROGRAM environment variable if set, otherwise default to "sql"
SQLCL_OPTS="-nolog -noupdates -S"
FORMATTER_EXT="sql,prc,fnc,pks,pkb,trg,vw,tps,tpb,tbp,plb,pls,rcv,spc,typ,aqt,aqp,ctx,dbl,tab,dim,snp,con,collt,seq,syn,grt,sp,spb,sps,pck"
FORMATTER_XML=$(cygpath -w "$SCRIPT_DIR/formatter/trivadis_advanced_format.xml" 2>/dev/null || echo "$SCRIPT_DIR/formatter/trivadis_advanced_format.xml")
FORMAT_ERRORS=0  # Track if any file was modified

# Function to get the list of files to format
get_files_to_format() {
    if [ "$#" -gt 0 ]; then
        # Files passed as arguments (from pre-commit)
        echo "$@"
    else
        # Find files matching extensions if no arguments passed (e.g., with --force mode)
        find . -type f | grep -E "\.($(echo $FORMATTER_EXT | tr ',' '|'))$"
    fi
}

# Function to create a temporary JSON file for the list of files to be formatted
create_json_file() {
    JSONFILE=$(cygpath -w "$(mktemp --tmpdir="${TEMP:-/tmp}")".json)

    # Create JSON array with files to be formatted
    echo "$FILES_TO_FORMAT" | awk 'BEGIN { ORS = ""; print "[\n"; }
        { printf "%s", (NR>1 ? ",\n" : ""); print "  \"" $1 "\""; }
        END { print "\n]\n"; }' > "$JSONFILE"
    echo "JSON file created at: $JSONFILE"
}

# Function to format files using format.js via SQLcl
format_via_format_js() {
    "$SQL_PROGRAM" $SQLCL_OPTS <<EOF
script $FORMATTER_JS "$JSONFILE" ext=$FORMATTER_EXT xml=$FORMATTER_XML
EXIT
EOF
}

# Main script execution
FILES_TO_FORMAT=$(get_files_to_format "$@")
if [ -z "$FILES_TO_FORMAT" ]; then
    echo "No files to format."
    exit 0
fi

# Create JSON file and format files
create_json_file
format_via_format_js

# Clean up JSON file
rm -f "$JSONFILE"

# If any files were formatted, exit with error for pre-commit to handle
echo "Some files were reformatted. Please review and re-stage changes."
exit 1
