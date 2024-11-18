#!/bin/sh

# Define paths for SQLcl and formatter configurations
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORMATTER_JS=$(cygpath -w "$SCRIPT_DIR/formatter/format.js" 2>/dev/null || echo "$SCRIPT_DIR/formatter/format.js")
SQL_PROGRAM="${SQL_PROGRAM:-sql}"  # Default to "sql" if SQL_PROGRAM is not set
SQLCL_OPTS="-nolog -noupdates -S"
FORMATTER_EXT="sql,prc,fnc,pks,pkb,trg,vw,tps,tpb,tbp,plb,pls,rcv,spc,typ,aqt,aqp,ctx,dbl,tab,dim,snp,con,collt,seq,syn,grt,sp,spb,sps,pck"
FORMATTER_XML=$(cygpath -w "$SCRIPT_DIR/formatter/trivadis_advanced_format.xml" 2>/dev/null || echo "$SCRIPT_DIR/formatter/trivadis_advanced_format.xml")

# Temporary JSON file for SQLcl
JSONFILE=$(mktemp --tmpdir="${TEMP:-/tmp}" formatter_files_XXXX.json)

# Function to get files for formatting
get_files_to_format() {
    if [ "$#" -gt 0 ]; then
        # Use files passed as arguments (e.g., by pre-commit)
        echo "$@"
    else
        # Find files matching extensions if no arguments provided
        find . -type f | grep -E "\.($(echo "$FORMATTER_EXT" | tr ',' '|'))$"
    fi
}

# Format files using format.js via SQLcl
format_files() {
    "$SQL_PROGRAM" $SQLCL_OPTS <<EOF
script $FORMATTER_JS "$JSONFILE" ext=$FORMATTER_EXT xml=$FORMATTER_XML
EXIT
EOF
}

# Main script logic
FILES_TO_FORMAT=$(get_files_to_format "$@")
if [ -z "$FILES_TO_FORMAT" ]; then
    echo "No files to format."
    exit 0
fi

# Create JSON file with files to format
echo "$FILES_TO_FORMAT" | awk 'BEGIN { ORS = ""; print "[\n"; }
    { printf "%s", (NR>1 ? ",\n" : ""); print "  \"" $1 "\""; }
    END { print "\n]\n"; }' > "$JSONFILE"

# Format the files
format_files

# Check for any changes in staged files
git diff --exit-code --quiet --staged
if [ $? -eq 0 ]; then
    echo "Files were reformatted but no changes detected by Git."
    rm -f "$JSONFILE"
    exit 0
fi

# Clean up temporary JSON file
rm -f "$JSONFILE"

# Exit with an error code for pre-commit to handle
echo "Some files were reformatted. Please review and re-stage changes."
exit 1
