#!/bin/bash
echo "=== RUNNING UBSan ==="
gcc -fsanitize=undefined -g static_analysis/vulnerable/loi_tinh_nang_luong.c -o /tmp/loi_int && /tmp/loi_int || true
gcc -fsanitize=undefined -g static_analysis/fixed/sua_tinh_nang_luong.c -o /tmp/sua_int && /tmp/sua_int
