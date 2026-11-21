"""Recreate the 3 article-14 figures (requires matplotlib)."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

HERE = Path(__file__).resolve().parent.parent / 'assets'
HERE.mkdir(parents=True, exist_ok=True)
BG='#0C1630'; CARD='#142542'; CYAN='#45D8EF'; PURPLE='#AD8FFF'; TEXT='#EAF3FF'; MUTED='#A7B7D6'; ORANGE='#FFB264'; GREEN='#70DBB0'

def create_canvas(title, subtitle):
    fig, ax=plt.subplots(figsize=(14,6.7), dpi=180)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0,14);ax.set_ylim(0,7);ax.axis('off')
    ax.text(.55,6.55,title,fontsize=20,fontweight='bold',color=TEXT)
    ax.text(.55,6.13,subtitle,fontsize=10.5,color=MUTED)
    return fig,ax

def card(ax,x,y,w,h,title,desc,border=CYAN,small=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.11,rounding_size=.18',facecolor=CARD,edgecolor=border,linewidth=1.7))
    ax.text(x+.17,y+h-.4,title,fontsize=13 if not small else 10.5,fontweight='bold',color=TEXT,va='center')
    for j,line in enumerate(desc): ax.text(x+.17,y+h-.86-.34*j,line,fontsize=10 if not small else 8.6,color=MUTED)

def arrow(ax,a,b,col=CYAN):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=17,color=col,linewidth=2))

fig,ax=create_canvas('Voice AI: Trust Boundaries','Encryption in transit is not a substitute for authorization, data controls, or retention limits')
card(ax,.55,3.1,2.6,2.25,'User / Browser',['Microphone permission','Notice + UI choice','Secure channel'])
card(ax,3.85,3.1,2.6,2.25,'Transport',['HTTPS / WSS','DTLS-SRTP (WebRTC)','Authenticated signaling'],PURPLE)
card(ax,7.15,3.1,2.6,2.25,'AI Runtime',['STT / LLM / TTS','Transient context','No privileged authority'],ORANGE)
card(ax,10.45,3.1,2.9,2.25,'Trusted Backend',['Identity + tenant scope','Policy + approvals','Storage + deletion'],GREEN)
for x in (3.15,6.45,9.75): arrow(ax,(x,4.15),(x+.68,4.15))
ax.plot([7,7],[2.95,5.6],linestyle='--',lw=1.8,color=ORANGE)
ax.text(7.11,5.55,'Model input is untrusted',fontsize=9,color=ORANGE)
ax.text(.65,2.1,'Failure to avoid:',color=ORANGE,fontweight='bold',fontsize=12)
ax.text(.65,1.64,'"The LLM requested this tool call" is not authentication or authorization.',color=TEXT,fontsize=11)
ax.text(.65,1.1,'Guard every read/write at the backend and audit only necessary, minimized metadata.',color=MUTED,fontsize=10)
fig.savefig(HERE/'security-trust-boundaries.png',bbox_inches='tight',facecolor=BG); plt.close(fig)

fig,ax=create_canvas('Privacy by Design','Mic access, recording permission, processing grounds, and retention are distinct controls')
items=[(.6, 'Access mic',['Browser permission','Does not grant recording']), (3.9,'Live processing',['Purpose + lawful basis','Limit processor access']), (7.2,'Optional storage',['Separate recording choice','Explicit retention purpose']), (10.5,'Deletion',['Scheduled purge','Backups + processors too'])]
for i,(x,title,desc) in enumerate(items):
    card(ax,x,3.2,2.6,2.25,title,desc,[CYAN,PURPLE,ORANGE,GREEN][i],True)
    if i<3:arrow(ax,(x+2.65,4.2),(x+3.23,4.2),[CYAN,PURPLE,ORANGE][i])
ax.plot([.9,13.1],[2.15,2.15],lw=4,color='#28436A')
ax.plot([.9,5.3],[2.15,2.15],lw=4,color=CYAN)
ax.plot([5.3,9.3],[2.15,2.15],lw=4,color=PURPLE)
ax.scatter([.9,5.3,9.3,13.1],[2.15]*4,s=135,c=[CYAN,PURPLE,ORANGE,GREEN],zorder=5)
for x,lab in zip([.9,5.3,9.3,13.1],['start','process','retention end','purge verified']):ax.text(x,1.7,lab,ha='center',fontsize=9,color=MUTED)
ax.text(.6,.75,'Illustrative lifecycle — legal bases and retention periods depend on use case and jurisdiction.',fontsize=10,color=TEXT)
fig.savefig(HERE/'security-privacy-lifecycle.png',bbox_inches='tight',facecolor=BG);plt.close(fig)

fig,ax=create_canvas('Secure Tool Execution','Untrusted text can propose a request, but only application policy may authorize side effects')
card(ax,.6,3.35,2.35,2,'Final user request',['Direct user origin','Confirmed transcript'],CYAN,True)
card(ax,3.45,3.35,2.35,2,'Policy checks',['Tenant + role + schema','Operation allowlist'],PURPLE,True)
card(ax,6.3,3.35,2.35,2,'Explicit approval',['One session + action','Short expiration'],ORANGE,True)
card(ax,9.15,3.35,2.35,2,'Backend commit',['Idempotency key','Durable validation'],GREEN,True)
card(ax,11.75,3.35,1.6,2,'Receipt',['Confirm','result'],GREEN,True)
for st,en in [((2.95,4.3),(3.45,4.3)),((5.8,4.3),(6.3,4.3)),((8.65,4.3),(9.15,4.3)),((11.5,4.3),(11.75,4.3))]:arrow(ax,st,en)
card(ax,3.1,1.3,3.5,1.25,'Untrusted sources',['RAG documents / tool outputs'],ORANGE,True)
arrow(ax,(4.85,2.55),(4.7,3.34),ORANGE)
ax.plot([6.0,6.1],[2.95,3.2],color=ORANGE,lw=3)
ax.text(7.75,2.25,'Reject cross-tenant access, stale session,',color=MUTED,fontsize=10)
ax.text(7.75,1.85,'interim transcript, and unapproved writes.',color=MUTED,fontsize=10)
fig.savefig(HERE/'security-tool-policy.png',bbox_inches='tight',facecolor=BG);plt.close(fig)
print('Wrote figures to', HERE)
