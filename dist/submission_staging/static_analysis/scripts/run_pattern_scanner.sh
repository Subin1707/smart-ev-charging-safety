#!/bin/bash
echo "=== RUNNING PATTERN SCANNER ==="
python3 static_analysis/scripts/pattern_scanner.py static_analysis/vulnerable
python3 static_analysis/scripts/pattern_scanner.py static_analysis/fixed
