#!/bin/bash

function error() {
	echo "$@" 1>&2
	exit 1
}

DEBUG=0
if [[ "$1" == "-d" ]]; then
	DEBUG=1
	shift
fi

INFILE="$1"

if [[ ! -f "$INFILE" ]]; then
	INFILE="inputs/$1"
fi

if [[ ! -f "$INFILE" ]]; then
	INFILE="inputs/$1.hsp"
fi

if [[ ! -f "$INFILE" ]]; then
	error "ERROR: '$1' not found"
fi

echo "INFILE: $INFILE" 1>&2

if [[ "$DEBUG" == "1" ]]; then
	poetry run python -m pdb -c continue -m python3_hsp_tiny_parser "$INFILE"
else
	poetry run python -m python3_hsp_tiny_parser "$INFILE"
fi

