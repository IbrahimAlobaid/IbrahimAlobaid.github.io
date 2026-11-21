"""Article 16 figures use abstract/synthetic content, not measured results."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

DIR = Path(__file__).resolve().parent.parent / 'assets'
DIR.mkdir(exist_ok=True)
BG='#08182C'; CARD='#102D48'; BORDER='#4FD7EF'; VIOLET='#C28DFF'; WHITE='#EAF7FF'; MUTED='#A8C6D9'; GREEN='#66E2C5'; GOLD='#FFCE7E'

def setup():
    fig, ax = plt.subplots(figsize=(13.8, 6.2), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 100); ax.set_ylim(0, 55); ax.axis('off')
    return fig, ax

def box(ax, x, y, w, h, title, subtitle='', color=BORDER, fs=13):
    p = FancyBboxPatch((x,y), w,h, boxstyle="round,pad=0.6,rounding_size=2", ec=color, fc=CARD, lw=2)
    ax.add_patch(p)
    ax.text(x+w/2,y+h*.62,title,ha='center',va='center',color=WHITE,fontsize=fs,fontweight='bold')
    if subtitle: ax.text(x+w/2,y+h*.25,subtitle,ha='center',va='center',color=MUTED,fontsize=9)

def arrow(ax,x1,y1,x2,y2,color=BORDER):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>', mutation_scale=16,linewidth=2,color=color,connectionstyle='arc3,rad=0'))

def save(fig, fn):
    fig.savefig(DIR/fn,dpi=145,bbox_inches='tight',facecolor=BG); plt.close(fig)

f,a=setup();a.text(50,51,'CAPSTONE  |  END-TO-END VOICE AGENT',fontsize=22,fontweight='bold',ha='center',color=WHITE)
box(a,3,29,17,12,'Browser','Microphone + playback');box(a,27,29,16,12,'WebRTC','Secure media')
box(a,50,29,20,12,'Pipecat Pipeline','STT  /  LLM  /  TTS',VIOLET);box(a,77,29,19,12,'User Response','Spoken audio')
arrow(a,20,35,27,35);arrow(a,43,35,50,35);arrow(a,70,35,77,35)
box(a,25,8,21,11,'Read-only Tools','FAQ / demo slot search',GREEN)
box(a,56,8,21,11,'Proposal Service','No LLM writes',GOLD)
arrow(a,60,29,37,20,GREEN);arrow(a,45,14,55,14,GOLD)
a.text(50,4,'Trust boundary: authentication + explicit confirmation live outside the LLM',ha='center',fontsize=11,color=GOLD)
save(f,'capstone-architecture.png')

f,a=setup();a.text(50,51,'SAFE ACTION LIFECYCLE (SIMULATED)',fontsize=22,fontweight='bold',ha='center',color=WHITE)
points=[(5,'Search','Read only'),(28,'Propose','Pending / TTL'),(51,'Trusted UI','External auth'),(74,'Commit','Idempotent')]
for x,t,s in points:box(a,x,27,19,12,t,s, color=GREEN if x==5 else BORDER)
for x in [24,47,70]:arrow(a,x,33,x+4,33)
box(a,25,5,22,10,'Cancel / change','Invalidate proposal',GOLD)
box(a,56,5,22,10,'Reconnect','New generation',VIOLET)
arrow(a,38,27,36,15,GOLD);arrow(a,64,27,67,15,VIOLET)
a.text(50,47,'The model never receives the approval secret and cannot execute a commit.',color=GOLD,ha='center',fontsize=11)
save(f,'capstone-safe-actions.png')

f,a=setup();a.text(50,51,'RELEASE READINESS  |  NO SINGLE GREEN CHECKMARK',fontsize=19,fontweight='bold',ha='center',color=WHITE)
for i,(x,t,s,c) in enumerate([(6,'Code Tests','Deterministic domain checks',GREEN),(36,'Voice E2E','Mic / ASR / VAD / TTS',GOLD),(66,'Production','Auth / tracing / rollout',VIOLET)]):
    box(a,x,24,27,15,t,s,c)
    a.text(x+13.5,13,'TESTED' if i==0 else 'NOT VERIFIED',fontsize=13,color=c,ha='center',fontweight='bold')
a.text(50,5,'Offline unit tests are evidence for code paths, not production certification.',fontsize=12,color=MUTED,ha='center')
save(f,'capstone-release-readiness.png')
print('created 3 diagrams')
