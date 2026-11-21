"""Generate Article 15 visual figures; synthetic educational data only."""
from pathlib import Path
import sys, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(Path(__file__).parent))
from voice_eval_observability_lab import evaluate,load_jsonl,release_gate
DATA=Path(__file__).with_name('15-synthetic-evaluation-cases.jsonl')
b=evaluate(load_jsonl(DATA,'baseline'))
r=evaluate(load_jsonl(DATA,'regression'))

# High-resolution custom cover, matching the prior dark-neon visual identity.
w,h=1600,900
img=Image.new('RGB',(w,h),(5,17,42))
p=img.load()
for y in range(h):
 for x in range(w):
  d1=((x-430)/830)**2+((y-350)/520)**2
  d2=((x-1180)/740)**2+((y-465)/560)**2
  glow1=math.exp(-3*d1); glow2=math.exp(-4*d2)
  p[x,y]=(min(255,int(4+6*glow1+15*glow2)),min(255,int(16+38*glow1+14*glow2)),min(255,int(40+52*glow1+67*glow2)))
glow=Image.new('RGBA',(w,h),(0,0,0,0));g=ImageDraw.Draw(glow)
# floor grid
for xx in range(-200,1801,115):
 g.line((800,575,xx,900),fill=(34,128,205,25),width=2)
for yy in (630,680,745,820,890):
 g.line((0,yy,1600,yy),fill=(40,144,230,35),width=2)
# data route and arrows
coords=[(200,390),(430,390),(670,390),(920,390),(1150,390),(1385,390)]
for k in range(5):
 g.line((*coords[k],*coords[k+1]),fill=(15,215,252,155) if k<3 else (164,102,254,160),width=10)
 g.polygon([(coords[k+1][0]-17,coords[k+1][1]-15),(coords[k+1][0],coords[k+1][1]),(coords[k+1][0]-17,coords[k+1][1]+15)],fill=(77,212,253,240) if k<3 else (182,119,253,240))
# center cards and diagrams
cards=[(140,290,310,490,(5,183,255)),(415,290,580,490,(26,227,224)),(692,270,865,510,(108,134,250)),(975,290,1140,490,(167,105,253)),(1250,290,1430,490,(196,82,244))]
for x1,y1,x2,y2,col in cards:
 g.rounded_rectangle((x1,y1,x2,y2),radius=32,fill=(*col,33),outline=(*col,220),width=6)
 g.rounded_rectangle((x1+8,y1+8,x2-8,y2-8),radius=25,outline=(*col,85),width=2)
# microphone icon
m=(224,365);g.rounded_rectangle((m[0]-25,m[1]-60,m[0]+25,m[1]+14),radius=22,outline=(68,224,255,255),width=8)
g.arc((m[0]-44,m[1]-19,m[0]+44,m[1]+45),0,180,fill=(68,224,255,255),width=7)
g.line((m[0],m[1]+45,m[0],m[1]+74),fill=(68,224,255,255),width=7)
g.line((m[0]-32,m[1]+74,m[0]+32,m[1]+74),fill=(68,224,255,255),width=7)
# waveform icon
for j in range(8):
 x=470+j*8
 g.line((x,390-int(19*math.sin(j+.7)**2+13),x,390+int(19*math.sin(j+.7)**2+13)),fill=(25,250,231,255),width=5)
# brain represented by neural nodes
nodes=[(748,345),(793,325),(815,378),(770,399),(738,422),(826,431),(785,470)]
for i,pt in enumerate(nodes):
 for other in nodes[i+1:i+4]:g.line((*pt,*other),fill=(135,169,255,170),width=3)
for x,y in nodes:g.ellipse((x-9,y-9,x+9,y+9),fill=(67,225,255,255))
# stop watch
cx,cy=1057,387
g.ellipse((cx-45,cy-45,cx+45,cy+45),outline=(183,131,255,255),width=8)
g.line((cx,cy,cx+21,cy-18),fill=(202,164,255,255),width=7)
g.line((cx,cy,cx,cy-30),fill=(202,164,255,255),width=7)
g.rounded_rectangle((cx-14,cy-65,cx+14,cy-49),radius=5,fill=(202,164,255,255))
# dashboard bars
for j,v in enumerate((55,89,70,110,96)):
 x=1298+j*22
 g.rounded_rectangle((x,455-v,x+12,455),radius=5,fill=(199,118,255,245))
# lower quality gate and monitoring panels
for k,(x,cl) in enumerate(((350,(25,210,248)),(790,(109,145,252)),(1230,(175,106,251)))):
 g.rounded_rectangle((x-170,615,x+170,770),radius=22,fill=(*cl,30),outline=(*cl,170),width=4)
 for j in range(4):
  xx=x-130+j*65
  hh=35+(j*21+k*13)%55
  g.rounded_rectangle((xx,725-hh,xx+28,725),radius=6,fill=(*cl,120+j*24),outline=(*cl,235),width=1)
# decorative rings
for rad in (105,146,190):
 g.arc((774-rad,395-rad,774+rad,395+rad),200,320,fill=(55,174,242,80),width=4)
img=Image.alpha_composite(img.convert('RGBA'),glow.filter(ImageFilter.GaussianBlur(3)))
img=Image.alpha_composite(img,glow)
img.convert('RGB').save(OUT/'evaluation-observability-cover.png',quality=95)

plt.rcParams.update({'font.size': 12, 'axes.titleweight':'bold','font.family':'DejaVu Sans'})
BG='#0b1630'; FG='#e5f1ff'; MUTED='#9db2d8'; CYAN='#35d9ed'; VIOLET='#a18cff'
fig,ax=plt.subplots(figsize=(13.5,5.1));fig.patch.set_facecolor(BG);ax.set_facecolor(BG)
intervals=[('Speech / endpoint',0,200,CYAN),('STT final',170,380,'#32b8d9'),('LLM first token',300,595,VIOLET),('TTS first audio',490,790,'#9677ff'),('Network + player',735,920,'#e28cff')]
for i,(label,sta,stop,col) in enumerate(intervals):
 y=4-i
 ax.barh(y,stop-sta,left=sta,height=.53,color=col,alpha=.88)
 ax.text(sta+7,y,label,va='center',ha='left',color=BG if i<2 else '#ffffff',weight='bold',fontsize=11)
ax.axvline(920,color='#f8c76a',linestyle='--',linewidth=2)
ax.text(925,4.53,'First audible response: 920 ms',color='#f8c76a',fontsize=11)
ax.set_yticks([]);ax.set_xlim(-30,1140);ax.set_ylim(-.8,5);ax.set_xlabel('Milliseconds relative to user turn end (illustrative)',color=FG)
ax.tick_params(colors=MUTED);ax.grid(axis='x',color='#23456e',alpha=.45);ax.set_title('Overlapping stages: the end-to-end path, not a sum of every bar',color=FG,pad=18)
for spine in ax.spines.values():spine.set_visible(False)
fig.tight_layout();fig.savefig(OUT/'evaluation-trace-waterfall.png',dpi=160,facecolor=BG,bbox_inches='tight');plt.close(fig)

fig,ax=plt.subplots(figsize=(13.2,5.1));fig.patch.set_facecolor(BG);ax.set_facecolor(BG)
cols=[CYAN,VIOLET]
labels=['TTFA P95 (ms)','Interruption P95 (ms)','Exact intent/tool match (%)']
base=[b['ttfa_p95_ms'],b['interruption_p95_ms'],b['intent_and_tool_exact_match_rate']*100]
reg=[r['ttfa_p95_ms'],r['interruption_p95_ms'],r['intent_and_tool_exact_match_rate']*100]
# Normalize units into ratios to illustrative gates (values beside bar remain original units)
limits=[1800,250,95]
for n,label in enumerate(labels):
 yy=4.9-1.7*n
 ax.text(-.03,yy+.5,label,color=FG,fontsize=12,weight='bold')
 for j,vals in enumerate((base,reg)):
  val=vals[n]; ratio=val/limits[n]; y=yy-j*.57
  ax.barh(y,ratio,height=.35,color=cols[j],alpha=.9)
  ax.text(ratio+.04,y,f'{val:.0f}' + ('%' if n==2 else ' ms'),va='center',color=FG)
ax.axvline(1,color='#f5bb61',linewidth=2,linestyle='--')
ax.text(1.02,6.1,'illustrative gate threshold',color='#f5bb61',fontsize=10)
ax.text(0.03,-.68,'Cyan = baseline (24 cases)   •   Purple = regression (8 cases)   •   Synthetic data, not benchmarks',color=MUTED,fontsize=11)
ax.set_yticks([]);ax.set_xticks([]);ax.set_xlim(0,2.35);ax.set_ylim(-.9,6.6)
ax.set_title('Release gates reveal regressions beyond unit-test success',color=FG,pad=14)
for spine in ax.spines.values():spine.set_visible(False)
fig.tight_layout();fig.savefig(OUT/'evaluation-quality-gates.png',dpi=160,facecolor=BG,bbox_inches='tight');plt.close(fig)

# Privacy-safe telemetry flow
fig,ax=plt.subplots(figsize=(13.5,5.2));fig.patch.set_facecolor(BG);ax.set_facecolor(BG);ax.set_xlim(0,12);ax.set_ylim(0,5);ax.axis('off')
nodes=[(.45,1.9,2.5,1.35,'Voice session\n(audio / transcript)',CYAN),(3.53,1.9,2.5,1.35,'Allowlist +\nredaction gate','#f5bb61'),(6.65,1.9,2.5,1.35,'Safe telemetry\ntrace / metrics',VIOLET),(9.77,1.9,2,1.35,'Monitor &\nrelease gate','#53d9aa')]
for x,y,wid,hei,label,col in nodes:
 rect=FancyBboxPatch((x,y),wid,hei,boxstyle='round,pad=0.08,rounding_size=.2',facecolor='#15284d',edgecolor=col,linewidth=2.5)
 ax.add_patch(rect);ax.text(x+wid/2,y+hei/2,label,ha='center',va='center',color=FG,fontsize=12,weight='bold')
for st,en in ((2.95,3.53),(6.03,6.65),(9.15,9.77)):
 ax.add_patch(FancyArrowPatch((st,2.58),(en,2.58),arrowstyle='-|>',mutation_scale=22,color=CYAN,linewidth=3))
ax.annotate('Never emit recordings, raw transcripts, tokens or personal identifiers into routine logs',xy=(4.73,1.78),xytext=(1,0.5),color='#f5c08a',fontsize=11,arrowprops={'arrowstyle':'->','color':'#f5bb61'},weight='medium')
ax.set_title('Observability without copying sensitive conversations into logs',color=FG,fontsize=15,pad=14)
fig.tight_layout();fig.savefig(OUT/'evaluation-private-observability.png',dpi=160,facecolor=BG,bbox_inches='tight');plt.close(fig)
print('created 4 images');print('baseline',b);print('regression',r)
