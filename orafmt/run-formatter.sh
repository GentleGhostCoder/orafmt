#!/usr/bin/env sh

# Define paths for SQLcl and formatter configurations
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORMATTER_JS=$(cygpath -w "$SCRIPT_DIR/formatter/format.js" 2>/dev/null || echo "$SCRIPT_DIR/formatter/format.js")
SQL_PROGRAM="${SQL_PROGRAM:-sql}"  # Default to "sql" if SQL_PROGRAM is not set
SQLCL_OPTS="-nolog -noupdates -S"
FORMATTER_EXT="sql,prc,fnc,pks,pkb,trg,vw,tps,tpb,tbp,plb,pls,rcv,spc,typ,aqt,aqp,ctx,dbl,tab,dim,snp,con,collt,seq,syn,grt,sp,spb,sps,pck"
FORMATTER_XML=$(cygpath -w "$SCRIPT_DIR/formatter/trivadis_advanced_format.xml" 2>/dev/null || echo "$SCRIPT_DIR/formatter/trivadis_advanced_format.xml")

# Check if files are passed as arguments
if [ "$#" -eq 0 ]; then
    echo "No files provided to the formatter. Exiting."
    exit 0
fi

# Format files passed by pre-commit
for file in "$@"; do
    echo "Formatting file: $file"
    "$SQL_PROGRAM" $SQLCL_OPTS <<EOF
script $FORMATTER_JS "$file" ext=$FORMATTER_EXT xml=$FORMATTER_XML
EXIT
EOF
done

# Check for any changes in staged files
git diff --exit-code --quiet --staged
if [ $? -eq 0 ]; then
    echo "Files were reformatted but no changes detected by Git."
    exit 0
fi

# Exit with an error code for pre-commit to handle
echo "Some files were reformatted. Please review and re-stage changes."
exit 1
