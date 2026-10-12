"""Export model evidence from the C transition table, not a second hand-written graph."""
import re
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / 'formal/kripke/kripke_sac.c').read_text(encoding='utf-8-sig')
table = text.split('static const int TRANSITIONS')[1].split('};')[0]
edges = []
for source, destinations in re.findall(r'/\*\s*(\w+)\s*\*/\s*\{([^}]+)', table):
    edges.extend((source, target) for target in re.findall(r'S_(\w+)', destinations))
positions = {'WAITING': (0, 3), 'CONNECTED': (0, 2), 'AUTH_OK': (0, 1),
             'AUTH_FAIL': (2, 2), 'CHARGING': (0, 0), 'STOPPED': (-2, -1),
             'FAULT': (0, -1), 'EMERGENCY': (2, -1)}
out = ROOT / 'evidence/01_model'
out.mkdir(parents=True, exist_ok=True)
(out/'state_list.txt').write_text('\n'.join(positions)+'\n', encoding='utf-8')
(out/'transitions.txt').write_text('\n'.join(a+' -> '+b for a,b in edges)+'\n', encoding='utf-8')
fig, ax = plt.subplots(figsize=(10, 7))
for a,b in edges:
    ax.annotate('', xy=positions[b], xytext=positions[a],
                arrowprops={'arrowstyle': '->', 'color': '#64748b', 'shrinkA': 26, 'shrinkB': 26,
                            'connectionstyle': 'arc3,rad=0.22' if b == 'WAITING' else 'arc3,rad=0'})
for label,(x,y) in positions.items():
    ax.text(x,y,label, ha='center',va='center',bbox={'boxstyle':'round,pad=0.6','fc':'#dbeafe','ec':'#2563eb'})
ax.set(xlim=(-3,3), ylim=(-1.7,3.7), title='Abstract charging state machine')
ax.axis('off')
fig.savefig(out/'state_machine.png', dpi=160, bbox_inches='tight')
plt.close(fig)
