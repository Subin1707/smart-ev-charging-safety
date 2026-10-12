import pathlib
p = pathlib.Path('verification/gd123_build_v4_spec.py')
txt = p.read_text(encoding='utf-8')
old = '"precondition":'
new = '"preconditions":'
count = txt.count(old)
txt2 = txt.replace(old, new)
p.write_text(txt2, encoding='utf-8')
print(f'Fixed {count} occurrences in generator')
