#!/bin/bash
echo "=== RUNNING CPPCHECK ==="
cppcheck --enable=all --inconclusive --quiet static_analysis/vulnerable
cppcheck --enable=all --inconclusive --quiet static_analysis/fixed
