"""Generates original educational diagrams for article 05. Optional matplotlib."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT=Path(__file__).resolve().parents[1] / 'assets'
ROOT.mkdir(parents=True,exist_ok=True)
BG='#071629'; WHITE='#edf7ff'; PALE='#a9c3dc'; CYAN='#48d4e5'; PURPLE='#a9a3ff'; GOLD='#f7bf76'; GREEN='#65d3ae'; RED='#ff8585'

def config(ax):
    ax.set_facecolor(BG); ax.set_xlim(0,14); ax.set_ylim(0,7.4); ax.axis('off')
def box(ax,x,y,w,h,label,sub,border=CYAN,fill='#102b42'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.12,rounding_size=0.18',linewidth=1.6,edgecolor=border,facecolor=fill))
    ax.text(x+w/2,y+h*.66,label,ha='center',va='center',color=WHITE,weight='bold',fontsize=13)
    ax.text(x+w/2,y+h*.28,sub,ha='center',va='center',color=PALE,fontsize=9.3)
def arrow(ax,x,y,X,Y,color=CYAN):
    ax.add_patch(FancyArrowPatch((x,y),(X,Y),arrowstyle='-|>',mutation_scale=14,color=color,linewidth=1.6))

fig,ax=plt.subplots(figsize=(13,6.8),facecolor=BG);config(ax)
ax.text(7,6.95,'The 4 layers of voice-agent context',ha='center',color=WHITE,fontsize=21,weight='bold')
ax.text(7,6.52,'Conversation text is only one part of what the model needs to answer safely.',ha='center',color=PALE,fontsize=11)
box(ax,.45,4.25,5.65,1.25,'Instructions','Role, tone, boundaries',CYAN)
box(ax,7.93,4.25,5.65,1.25,'Recent turns','Committed user/assistant messages',PURPLE)
box(ax,.45,1.9,5.65,1.25,'Structured task state','Validated details, explicit approval',GREEN)
box(ax,7.93,1.9,5.65,1.25,'External verified facts','Tool results, policy, availability',GOLD)
for a,b,c,d,color in [(3.3,4.15,6.1,3.7,CYAN),(10.73,4.15,7.9,3.7,PURPLE),(3.3,3.25,6.1,3.7,GREEN),(10.73,3.25,7.9,3.7,GOLD)]:arrow(ax,a,b,c,d,color)
box(ax,6.17,3.15,1.66,1.0,'LLM','Reply',CYAN,fill='#19344a')
ax.text(7,.75,'Data is not an instruction. A model response is not a confirmed external action.',ha='center',fontsize=11,color=PALE)
fig.savefig(ROOT/'llm-context-layers.png',dpi=180,bbox_inches='tight',facecolor=BG);plt.close(fig)

fig,ax=plt.subplots(figsize=(13,6.7),facecolor=BG);config(ax)
ax.text(7,7.0,'Correction + interruption: state transitions',ha='center',color=WHITE,fontsize=20,weight='bold')
steps=[('1','User says','10:00','10:00',CYAN),('2','Assistant speaks','segment 1 heard','10:00',PURPLE),('3','User interrupts','"Make it 15:00"','10:00',GOLD),('4','App updates state','Approval reset','15:00',GREEN),('5','Agent replies','"15:00, correct?"','15:00',CYAN)]
for i,(n,header,event,state,color) in enumerate(steps):
    x=.38+i*2.70
    ax.add_patch(FancyBboxPatch((x,3.25),2.45,2.15,boxstyle='round,pad=.09,rounding_size=.17',edgecolor=color,facecolor='#102b42',linewidth=1.5))
    ax.text(x+.2,5.07,n,color=color,weight='bold',fontsize=16)
    ax.text(x+1.22,4.66,header,ha='center',color=WHITE,fontsize=10.5,weight='bold')
    ax.text(x+1.22,4.18,event,ha='center',color=PALE,fontsize=9.5)
    ax.text(x+1.22,3.58,f'Time = {state}',ha='center',color=WHITE,fontsize=9.5)
    if i<4: arrow(ax,x+2.45,4.32,x+2.62,4.32,color=CYAN)
ax.text(7,2.35,'Never treat generated-but-unheard text as delivered conversation.',ha='center',color=WHITE,fontsize=12,weight='bold')
ax.text(7,1.83,'Do not trigger booking until a confirmed request and authorized tool result exist.',ha='center',color=PALE,fontsize=11)
ax.text(7,1.1,'Illustrative sequence, not a timing benchmark or a word-level audio alignment algorithm.',ha='center',color=PALE,fontsize=9.5)
fig.savefig(ROOT/'llm-correction-timeline.png',dpi=180,bbox_inches='tight',facecolor=BG);plt.close(fig)
