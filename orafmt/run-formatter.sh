#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Use the SQL_PROGRAM environment variable if set, otherwise default to "sql"
SQL_PROGRAM="${SQL_PROGRAM:-sql}"

# Configuration for SQLcl and formatter paths, relative to the script's directory
FORMATTER_JS=$(cygpath -w "$SCRIPT_DIR/formatter/format.js" 2>/dev/null || echo "$SCRIPT_DIR/formatter/format.js")
SQLCL_OPTS="-nolog -noupdates -S"
FORMATTER_XML=$(cygpath -w "$SCRIPT_DIR/formatter/trivadis_advanced_format.xml" 2>/dev/null || echo "$SCRIPT_DIR/formatter/trivadis_advanced_format.xml")

# Create JSON file for SQLcl input
create_json_file() {
    JSONFILE=$(cygpath -w "$(mktemp --tmpdir="${TEMP:-/tmp}")".json)

    # Create JSON array with files to be formatted
    echo "$@" | awk 'BEGIN { ORS = ""; print "[\n"; }
        { printf "%s", (NR>1 ? ",\n" : ""); print "  \"" $1 "\""; }
        END { print "\n]\n"; }' > "$JSONFILE"
    echo "JSON file created at: $JSONFILE"
}

# Format files using format.js via SQLcl
format_via_format_js() {
    "$SQL_PROGRAM" $SQLCL_OPTS <<EOF
script $FORMATTER_JS "$JSONFILE" ext=$FORMATTER_EXT xml=$FORMATTER_XML
EXIT
EOF
}

# Main execution
if [ "$#" -eq 0 ]; then
    echo "No files to format."
    exit 0
fi

# Execute functions to create JSON file and format files
create_json_file "$@"
format_via_format_js

# Cleanup
rm -f "$JSONFILE"

exit 0
