"""Regenerate article 13 educational figures (illustrative, not benchmarks)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)
NAVY="#0c1932"; SKY="#4fd8f3"; PURPLE="#a59aff"; WHITE="#eaf2ff"; MUTED="#a7bdd8"; AMBER="#f5bc66"

def start(title, subtitle=""):
    fig, ax = plt.subplots(figsize=(14, 6.5), dpi=150)
    fig.patch.set_facecolor(NAVY); ax.set_facecolor(NAVY)
    ax.set(xlim=(0,14),ylim=(0,6.5)); ax.axis("off")
    ax.text(.6,6,title,color=WHITE,fontsize=18,weight="bold",va="top")
    if subtitle: ax.text(.6,5.52,subtitle,color=MUTED,fontsize=10)
    return fig,ax

def box(ax,x,y,w,h,t,sub="",color=SKY):
    rect=FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.14,rounding_size=.2",linewidth=1.7,edgecolor=color,facecolor="#142541")
    ax.add_patch(rect);ax.text(x+w/2,y+h*.63,t,color=WHITE,ha="center",va="center",fontsize=11,weight="bold")
    if sub: ax.text(x+w/2,y+h*.27,sub,color=MUTED,ha="center",va="center",fontsize=8.4)

def arrow(ax,p1,p2,col=SKY,label=None):
    ax.add_patch(FancyArrowPatch(p1,p2,arrowstyle="-|>",mutation_scale=16,lw=2,color=col))
    if label: ax.text((p1[0]+p2[0])/2,(p1[1]+p2[1])/2+.12,label,color=col,ha="center",fontsize=8)

fig,ax=start("Two different capabilities: knowledge vs actions", "RAG returns grounded evidence. A tool can change the external world.")
box(ax,.65,2.3,2,1.2,"User voice","STT + intent")
box(ax,3.7,2.3,2.2,1.2,"Orchestrator","LLM + policy",PURPLE)
arrow(ax,(2.72,2.9),(3.57,2.9))
box(ax,7.1,4.0,2.1,1.1,"RAG search","read-only evidence",SKY)
box(ax,10.45,4.0,2.5,1.1,"Knowledge","tenant-scoped docs",SKY)
arrow(ax,(5.98,3.2),(6.97,4.45));arrow(ax,(9.31,4.55),(10.3,4.55))

box(ax,7.1,1.15,2.1,1.1,"Action tools","validated inputs",AMBER)
box(ax,10.45,1.15,2.5,1.1,"Business API","write + audit log",AMBER)
arrow(ax,(5.98,2.65),(6.97,1.7),AMBER)
arrow(ax,(9.33,1.7),(10.3,1.7),AMBER)
ax.text(7.65,.4,"Sensitive actions require identity, confirmation and idempotency.",color=MUTED,fontsize=10)
fig.savefig(OUT/"tools-rag-vs-actions.png",bbox_inches="tight",facecolor=NAVY);plt.close(fig)

fig,ax=start("Booking workflow: approval before effect", "A spoken proposal is not the same as a committed transaction.")
steps=[(.6,2.85,"Lookup","read-only",SKY),(3.4,2.85,"Prepare","intent only",SKY),(6.25,2.85,"Confirm","final + authorized",AMBER),(9.15,2.85,"Commit","idempotent write",PURPLE),(11.95,2.85,"Report","verified result",SKY)]
for x,y,top,sub,c in steps: box(ax,x,y,1.6,1.1,top,sub,c)
for left,right in zip(steps,steps[1:]): arrow(ax,(left[0]+1.75,3.4),(right[0]-.15,3.4),left[4])
box(ax,4.3,.65,3.1,.95,"Cancel / stale session","no write, re-confirm",AMBER)
arrow(ax,(7.1,2.75),(6.35,1.74),AMBER,"decline / disconnect")
ax.text(.7,.27,"Never confirm on partial STT or an untrusted retrieved instruction.",color=MUTED,fontsize=10)
fig.savefig(OUT/"tools-approval-state-machine.png",bbox_inches="tight",facecolor=NAVY);plt.close(fig)

fig,ax=start("Voice UX: tool latency is part of the answer", "Illustrative timeline only — not measurements or vendor benchmarks.")
labels=[("User finishes",.7,1.6,SKY),( "STT final",2.4,3.1,SKY),("RAG / lookup",3.35,5.2,PURPLE),("Confirmation",5.5,8.25,AMBER),("Action commit",8.55,10.3,AMBER),("TTS playback",10.55,13.1,SKY)]
for i,(name,s,e,c) in enumerate(labels):
    y=4.6-i*.63
    ax.text(.6,y-.10,name,color=WHITE,fontsize=10,va="center")
    ax.plot([4.1 + s*.65,4.1 + e*.65],[y,y],lw=12,solid_capstyle="round",color=c)
ax.set_xlim(0,14)
ax.text(6.0,.45,"Use short progress messages during slow reads; never announce success before commit.",color=MUTED,fontsize=10)
fig.savefig(OUT/"tools-voice-ux-timeline.png",bbox_inches="tight",facecolor=NAVY);plt.close(fig)
print("Generated", [p.name for p in OUT.glob("tools-*.png")])
