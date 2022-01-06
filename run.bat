@echo off

set INFILE=%~1

if not exist "%INFILE%" (set INFILE=inputs\%~1)
if not exist "%INFILE%" (set INFILE=inputs\%~1.hsp)
if not exist "%INFILE%" (
    echo ERROR: '%~1' not found>&2
    exit /B 1
)

echo INFILE: %INFILE%>&2

poetry run python -m python3_hsp_tiny_parser "%INFILE%"
