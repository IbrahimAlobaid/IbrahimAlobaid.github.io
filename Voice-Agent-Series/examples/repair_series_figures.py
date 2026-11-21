"""Re-create educational diagrams referenced by the original 01–12 notes.
Each diagram is a synthetic explanatory illustration, never measured results.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
OUT=Path(__file__).resolve().parent.parent/'assets'
BG='#0c1932'; FG='#e6f0ff'; CY='#47c7df'; PUR='#a58df1'; AM='#ffd078'
def fig(title,subtitle=''):
 f,ax=plt.subplots(figsize=(12,5),dpi=140);f.patch.set_facecolor(BG);ax.set_facecolor(BG)
 ax.set_xlim(0,12);ax.set_ylim(0,5);ax.axis('off')
 ax.text(.4,4.7,title,fontsize=17,weight='bold',color=FG,va='top')
 if subtitle: ax.text(.4,4.25,subtitle,fontsize=10,color='#a4bada')
 return f,ax
def save(f,name): f.savefig(OUT/name,facecolor=BG,bbox_inches='tight');plt.close(f)
def box(ax,x,y,w,h,label,color=CY):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.12,rounding_size=.12',facecolor='#1d3150',edgecolor=color,lw=2))
 ax.text(x+w/2,y+h/2,label,ha='center',va='center',color=FG,fontsize=11,weight='bold')
def arr(ax,x1,y1,x2,y2,color=CY):
 ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=17,color=color,lw=2))
# 1 quantization
f,ax=fig('Quantization: continuous amplitude into discrete levels','Illustrative 4-bit-like levels; not an audio encoder benchmark')
x=np.linspace(0,2*np.pi,350); y=np.sin(x)
ax.plot(1.2+9.6*x/(2*np.pi),2.3+1.1*y,color=CY,lw=2.3,label='analog amplitude')
ax.step(1.2+9.6*x/(2*np.pi),2.3+1.1*(np.round(y*3)/3),where='mid',color=PUR,lw=2,alpha=.9,label='quantized')
ax.set_xlim(0,12);ax.legend(loc='lower center',facecolor='#132643',edgecolor='#4a6382',labelcolor=FG,ncol=2);save(f,'quantization.png')
# 2 synthetic spectrogram
f,ax=fig('STT front-end: time–frequency representation','Synthetic tone sweeps; speech features are more complex')
rng=np.random.default_rng(3); n=5120;t=np.arange(n)/8000
s=np.sin(2*np.pi*(270*t+1200*t*t))+0.30*np.sin(2*np.pi*(950*t))+0.06*rng.standard_normal(n)
from matplotlib.mlab import specgram
P,freq,bins=specgram(s,NFFT=256,Fs=8000,noverlap=200)
ax.imshow(10*np.log10(np.maximum(P,1e-12)),origin='lower',aspect='auto',extent=(1,11.5,0.75,3.8),cmap='viridis')
ax.text(1,.37,'Time →',color=FG,fontsize=11);ax.text(.1,2.4,'Frequency',color=FG,rotation=90,fontsize=9);save(f,'stt-spectrogram-example.png')
# 3 pipecat lifecycle
f,ax=fig('Voice agent session lifecycle','Simplified conceptual state flow')
ls=[('Created',.45),('Connecting',2.8),('Listening',5.15),('Responding',7.5),('Closed',9.85)]
for i,(label,x) in enumerate(ls):
 box(ax,x,2.0,1.65,.95,label,PUR if i==3 else CY)
 if i: arr(ax,x-.55,2.5,x-.08,2.5)
ax.text(5.7,1.1,'Interruption: responding → listening',color=AM,fontsize=12)
save(f,'pipecat-session-lifecycle.png')
# 4 turn detection tradeoff
f,ax=fig('Endpointing: delay vs premature cutoff','Illustrative trade-off; not evaluated on real speech')
x=np.linspace(.1,1,100);a=1/(1+np.exp(12*(x-.42)));b=.10+.87*x
ax.plot(.8+10*x,1.0+2.8*a,color=PUR,lw=3,label='false early cutoff risk')
ax.plot(.8+10*x,1.0+2.8*b,color=CY,lw=3,label='response delay')
ax.legend(loc='lower right',facecolor='#1e3656',edgecolor='#52688d',labelcolor=FG)
ax.text(1,0.35,'Shorter silence threshold',color=FG);ax.text(8.2,0.35,'Longer threshold',color=FG);save(f,'turn-detection-tradeoff.png')
# 5 recovery timeline
f,ax=fig('Network recovery and state reconciliation','Do not replay an uncertain write blindly')
seg=[('Connected',.7,3.2,CY),('Lost',3.5,5.0,AM),('Reconnected',5.3,7.8,PUR),('Reconciled',8.1,11.2,CY)]
for t,x1,x2,c in seg:
 ax.plot([x1,x2],[2.8,2.8],color=c,lw=14,solid_capstyle='round');ax.text((x1+x2)/2,3.2,t,ha='center',color=FG,fontsize=11)
ax.text(.7,1.5,'generation=1',color=CY,fontsize=11);ax.text(5.3,1.5,'generation=2',color=PUR,fontsize=11)
ax.text(8.1,.75,'Query commit status by idempotency key',color=AM,fontsize=10);save(f,'robustness-recovery-timeline.png')
# 6 three architectures
f,ax=fig('Three voice agent architectures','The right choice depends on control, latency and product requirements')
for y,title,tokens,c in [(3.55,'Cascaded',['STT','LLM','TTS'],CY),(2.55,'Speech-to-Speech',['Audio','Model','Audio'],PUR),(1.55,'Hybrid',['STT','LLM / Realtime','TTS'],AM)]:
 ax.text(.3,y+.12,title,color=c,fontsize=11,weight='bold')
 for i,(token,x) in enumerate(zip(tokens,[4.3,6.8,9.3])):
  box(ax,x,y-.14,1.7,.5,token,c)
  if i: arr(ax,x-.66,y+.13,x-.18,y+.13,c)
save(f,'voice-architecture-comparison.png')
# 7 illustrative architecture timelines
f,ax=fig('Illustrative response timelines','Synthetic offsets only; not comparative provider benchmarks')
series=[('Cascaded',3.7,[(.6,1.8,CY),(1.8,2.9,PUR),(2.9,4.1,AM)]),('Speech-to-Speech',2.5,[(.6,2.0,PUR),(2.0,3.1,CY)]),('Hybrid',1.3,[(.6,1.6,CY),(1.6,2.45,PUR),(2.45,3.45,AM)])]
for label,y,bars in series:
 ax.text(.3,y+.05,label,color=FG,fontsize=11)
 for a,b,c in bars: ax.plot([3+2*a,3+2*b],[y,y],color=c,lw=13,solid_capstyle='round')
ax.text(3,.35,'Synthetic stage spans →',color=FG,fontsize=10);save(f,'voice-architecture-latency.png')
print('Generated repaired figures')
