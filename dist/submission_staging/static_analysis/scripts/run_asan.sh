#!/bin/bash
echo "=== RUNNING ASan ==="
gcc -fsanitize=address -g static_analysis/vulnerable/loi_id_xe.c -o /tmp/loi_id_xe && /tmp/loi_id_xe || true
gcc -fsanitize=address -g static_analysis/fixed/sua_id_xe.c -o /tmp/sua_id_xe && /tmp/sua_id_xe
