import os
import re
import sys

DANGEROUS_PATTERNS = [
    (r'\bstrcpy\s*\(', "CWE-120: Buffer Copy without Checking Size of Input (strcpy)"),
    (r'\bsprintf\s*\(', "CWE-134: Use of Externally-Controlled Format String / Buffer Overflow (sprintf)"),
    (r'\bstrcat\s*\(', "CWE-120: Buffer Copy without Checking Size of Input (strcat)"),
    (r'\bgets\s*\(', "CWE-242: Use of Inherently Dangerous Function (gets)"),
    (r'\bcong_suat_kw\s*\*\s*1000000000', "CWE-190: Integer Overflow or Wraparound"),
]

def scan_file(filepath):
    findings = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines, 1):
            for pattern, desc in DANGEROUS_PATTERNS:
                if re.search(pattern, line):
                    findings.append((idx, line.strip(), desc))
    return findings

def scan_dir(directory):
    total = 0
    print(f"\n==================================================")
    print(f" SCANNING DIRECTORY: {directory}")
    print(f"==================================================")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.c', '.h')):
                p = os.path.join(root, file)
                res = scan_file(p)
                if res:
                    print(f"\n[!] FILE: {file}")
                    for line_num, code, desc in res:
                        print(f"  Line {line_num}: {desc}")
                        print(f"    Code: {code}")
                        total += 1
                else:
                    print(f"[+] FILE: {file} -> CLEAN (0 issues)")
    print(f"Total vulnerabilities found: {total}")
    return total

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    sys.exit(scan_dir(target))
