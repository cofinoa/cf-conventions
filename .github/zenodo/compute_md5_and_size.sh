#!/bin/bash

# Check if the user provided a directory
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <directory>"
  exit 1
fi

# Directory to process
DIR="$1"

# Check if the directory exists
if [ ! -d "$DIR" ]; then
  echo "Error: Directory $DIR does not exist."
  exit 1
fi

# Gather .html and .pdf files and compute max lengths for alignment
FILES=()
MAX_FILENAME=0
MAX_SIZE=0
for FILE in "$DIR"/*; do
  if [ -f "$FILE" ] && ([[ "$FILE" == *.pdf ]] || [[ "$FILE" == *.html ]]); then
    BASENAME=$(basename "$FILE")
    SIZE=$(stat --printf="%s" "$FILE")
    MD5=$(md5sum "$FILE" | awk '{print $1}')
    FILES+=("$BASENAME:$SIZE:$MD5")
    MAX_FILENAME=$(( MAX_FILENAME > ${#BASENAME} ? MAX_FILENAME : ${#BASENAME} ))
    MAX_SIZE=$(( MAX_SIZE > ${#SIZE} ? MAX_SIZE : ${#SIZE} ))
  fi
done

# Generate JSON output
#echo "["  # Begin JSON array
FIRST=true
for ENTRY in "${FILES[@]}"; do
  IFS=":" read -r BASENAME SIZE MD5 <<< "$ENTRY"

  # Add a comma before the entry if it's not the first
  if [ "$FIRST" = false ]; then
    echo ","
  fi
  FIRST=false

  # Print JSON object with aligned filename (quoted value aligned to the right)
  printf "  {\"filename\": %*s, \"size\": %${MAX_SIZE}s, \"checksum\": \"md5:%s\"}" $((MAX_FILENAME + 2)) "\"$BASENAME\"" "$SIZE" "$MD5"
done
echo ""  # Final newline
#echo "]"  # End JSON array

