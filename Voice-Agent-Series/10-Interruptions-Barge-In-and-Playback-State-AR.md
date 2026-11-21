---
title: "عندما يقاطعنا المستخدم: هندسة المقاطعات ومزامنة الصوت في الوكلاء الصوتيين"
aliases:
  - "المقالة العاشرة — Interruption & Barge-In"
  - "Voice AI Engineering Article 10 AR"
author: "Ibrahim Alobaid"
date: 2026-11-21
series: "Voice AI Engineering — From Zero to Production"
article: 10
level: "Intermediate / Advanced"
language: ar
tags:
  - voice-ai
  - voice-agents
  - interruptions
  - barge-in
  - playback-tracking
  - conversation-state
  - audio-streaming
  - real-time
  - python
status: draft
cover: "assets/barge-in-playback-cover.png"
---

# عندما يقاطعنا المستخدم: هندسة المقاطعات ومزامنة الصوت في الوكلاء الصوتيين

**Interruptions, Barge-In & Playback State — المقالة 10 / 16**  
**المستوى:** متوسط → متقدم | **القراءة:** نحو 25–35 دقيقة + مختبر Python  
**English:** [[10-Interruptions-Barge-In-and-Playback-State-EN|Read in English]]  
**السابقة:** [[09-VAD-Endpointing-and-Turn-Detection-AR|VAD وEndpointing وTurn Detection]]  
**الفهرس:** [[00-Series-Roadmap|سلسلة هندسة الوكلاء الصوتيين]]

![[assets/barge-in-playback-cover.png]]

> [!abstract] السؤال الرئيسي
> ما الذي يجب أن يحدث عندما يبدأ المستخدم الكلام **بينما الوكيل لا يزال يتحدث**؟ التحدي ليس مجرد استدعاء `stop()` على مشغل الصوت؛ بل إيقاف عدة عمليات غير متزامنة، ومنع ظهور صوت قديم، وضبط ذاكرة الوكيل وفق ما **شُغّل** فعلياً، ثم متابعة المحادثة دون تناقض.

## 1. من الديمو إلى المحادثة الحقيقية

تخيّل وكيلاً يساعد مستخدماً على إكمال التحقق من الهوية:

> **الوكيل:** «يمكنك إتمام العملية باستخدام جواز السفر أو بطاقة الهوية، ثم...»  
> **المستخدم، مقاطعاً:** «لحظة، جواز سفري منتهي الصلاحية. هل هناك طريقة أخرى؟»  
> **الوكيل الجيد:** يوقف الصوت بسرعة، يسمع التصحيح، ويفهم أن المستخدم ربما لم يسمع بقية الجملة.

في النظام الساذج، قد يستمر الصوت حتى نهاية الجملة، أو تُرسَل دفعات TTS القديمة بعد المقاطعة، أو يحتفظ LLM في سجل المحادثة بجواب كامل لم يسمعه المستخدم. **هذه أخطاء تنسيق بين المكونات، وليست بالضرورة أخطاء في ذكاء النموذج.**

سبق أن فرّقنا في [[09-VAD-Endpointing-and-Turn-Detection-AR|المقالة التاسعة]] بين اكتشاف الكلام ونهاية دور المستخدم. الآن نضيف مساراً آخر: **ما الذي نفعله عند اكتشاف كلام المستخدم أثناء إخراج الوكيل؟**

## 2. ما معنى Barge-In؟ ولماذا لا يكفي VAD؟

**Barge-In** هو أن يتدخل المستخدم في دور كلام الوكيل فيؤدي تدخله إلى إيقاف الوكيل أو تحويل الدور إليه. ليست كل إشارة صوتية مقاطعة حقيقية:

| الموقف | الإشارة | القرار المحتمل |
|---|---|---|
| «توقف، الموعد يوم الخميس وليس الثلاثاء» | طلب واضح لتغيير المعلومة | إيقاف الوكيل ومعالجة التصحيح |
| «مم»، «آها» أثناء الشرح | Backchannel: إشارة متابعة | الاستمرار غالباً إذا كانت سياسة النظام واثقة |
| ارتداد صوت السماعة إلى الميكروفون | Echo | لا ينبغي اعتباره مستخدماً يقاطع نفسه |
| ضوضاء أو سعال | احتمال صوتي دون نية واضحة | قد يلزم التحقق قبل إلغاء الإجابة |

يستطيع **VAD** اكتشاف كلام محتمل، لكنه لا يثبت *نية* المقاطعة؛ ويمكن استخدام STT أو المصنفات الصوتية أو سياسات التوقف التكيفية للحد من الأخطاء. يتضمن LiveKit مثالاً على التعامل التكيفي مع المقاطعات، والاستئناف بعد الإيقاف الخاطئ.[^livekit-turns][^livekit-adaptive]

> [!tip] سياسة من مرحلتين
> **مرحلة سريعة:** أوقف أو علّق التشغيل فور ظهور مؤشر مقاطعة موثوق حتى لا «يتكلم النظام فوق المستخدم».  
> **مرحلة تأكيد:** قرر هل كانت مقاطعة فعلية؛ إن لم تكن، استأنف بأمان من موضع محفوظ عندما يكون الاستئناف مدعوماً. هذه *معمارية مقترحة*؛ التطبيق الفعلي يختلف بين المكتبات.

## 3. لم نعد نملك مساراً صوتياً واحداً

```mermaid
flowchart LR
  U[User microphone] --> V[VAD and interruption gate]
  V -->|Barge-in candidate| C[Player pause request]
  V -->|Confirmed user turn| S[STT and conversation state]
  S --> L[LLM generation]
  L --> T[TTS audio chunks]
  T --> N[Network transport]
  N --> B[Client output buffer]
  B --> P[Audio actually played]
  P -->|Playback acknowledgement| R[Context reconciliation]
  C --> X[Cancel stale generation and flush queue]
  X --> R
  R --> S
```

**الشكل 1.** الصوت الذي تنتجه النماذج يمر بمخازن ومسارات غير متزامنة؛ مسار تأكيد التشغيل يجب أن يعود إلى مدير السياق.

عندما تأتي مقاطعة، لا يكفي إيقاف TTS؛ قد تكون دفعات إضافية قد وصلت إلى المتصفح. ولا يكفي إيقاف المتصفح؛ قد ينتج LLM رسالة صوتية جديدة قديمة المنطق بعد لحظات. ينبغي معالجة المرحلتين معاً.

## 4. Generated ≠ Synthesized ≠ Transmitted ≠ Buffered ≠ Played

هذه أكثر فكرة تستحق أن تبني حولها اختباراً عملياً:

| المؤشر | ماذا يعني؟ | هل يثبت أن المستخدم سمعه؟ |
|---|---|---|
| **Generated text** | LLM كتب نص الاستجابة | لا |
| **Synthesized audio** | TTS حوّل بعض النص إلى عينات صوتية | لا |
| **Transmitted audio** | الخادم أرسل البيانات | لا |
| **Buffered audio** | العميل خزّن الصوت في قائمة التشغيل | لا |
| **Played audio** | المشغّل أبلغ عن تقدم التشغيل | أفضل تقدير متاح، وليس إثباتاً أن الأذن سمعته |

![[assets/barge-in-playback-cursors.png]]

*الشكل 2 — أرقام اصطناعية للتوضيح: تم توليد 3600 ms، وتجهيز 3100، وإرسال 2600، وتخزين 2400، بينما يؤكد المشغل تشغيل 1500 ms فقط. ليست نتائج Benchmark.*

**لماذا هذا التفريق مهم؟** إذا حفظنا النص الكامل ضمن سياق LLM بعد سماع 1.5 ثانية فقط، فربما سيقول الوكيل لاحقاً: «كما أخبرتك، يمكنك استخدام البطاقة» رغم أن تلك المعلومة لم تُشغّل بعد.

> [!warning] قيد مهم على «ما سمعه المستخدم»
> `played_ms` هو **مؤشر مشغّل** وليس قياساً مباشراً للإدراك البشري. قد توجد فروق بسبب مخزن الأجهزة والتأخير وإعدادات الصوت. يمكن استخدام `AudioContext.getOutputTimestamp()` و`outputLatency` في المتصفح لفهم الحدود والتقديرات، لكن لا ينبغي الادعاء أننا نعرف بدقة ما وصل إلى أذن المستخدم.[^mdn-output]

## 5. ما الذي يحدث أثناء المقاطعة خطوة بخطوة؟

1. **Detect:** رصد كلام المستخدم أثناء استجابة الوكيل، مع محاولة عدم الخلط بين Echo أو Backchannel وبين مقاطعة حقيقية.
2. **Pause quickly:** تعليق/إيقاف مشغّل العميل وتقليل استمرار الصوت قبل انتظار اكتمال STT أو انتهاء طلب LLM.
3. **Confirm:** تحديد إن كانت مقاطعة حقيقية أم إشارة قصيرة عابرة؛ قد تعود الاستجابة للتشغيل في حالة الإنذار الكاذب.
4. **Stop and cancel:** عند التأكيد، إيقاف تشغيل الصوت، وإلغاء/تجاهل عمليات LLM وTTS الجارية ودفعاتها القادمة.
5. **Flush:** تفريغ طابور التشغيل القديم ومنع خلطه مع صوت الرد الجديد.
6. **Reconcile context:** تحديث سجل المحادثة وفق تقدم التشغيل المؤكد، وعدم إدراج الجمل غير المسموعة بوصفها كلاماً موجهاً للمستخدم.
7. **Continue:** التعامل مع سؤال المستخدم الجديد ثم إنشاء استجابة جديدة مرتبطة بجيل جديد من الأحداث.

![[assets/barge-in-cancellation-flow.png]]

*الشكل 3 — هناك فرق بين مقاطعة مؤكدة تستلزم الإلغاء، ومقاطعة خاطئة يمكن الاستئناف بعدها؛ القواعد المعروضة تصميم تعليمي لا تنفيذ حرفي لإطار عمل محدد.*

```mermaid
sequenceDiagram
    participant User
    participant Client as Browser/player
    participant Server as Session coordinator
    participant Model as LLM/TTS
    User->>Client: Starts interrupting
    Client->>Client: Pause output immediately
    Client->>Server: interruption_candidate + playback cursor
    Server->>Server: Confirm interruption policy
    alt Genuine barge-in
        Server-->>Model: Cancel old generation / TTS
        Server-->>Client: Clear old queued output
        Client-->>Server: Final playback stop acknowledgement
        Server->>Server: Truncate unheard context / bump epoch
        User->>Server: New turn via STT
        Server->>Model: Generate updated response
    else False positive
        Server-->>Client: Resume retained output if safe
    end
```

**الشكل 4 — ترتيب الأحداث توضيحي.** في التطبيق الحقيقي ينبغي استخدام معرفات رسائل وأجيال وربط الإقرارات بالرد الصحيح؛ وقد تتبادل عمليات التحقق والإلغاء مواقعها بحسب واجهة النقل.

## 6. المشكلة الخفية: Late Chunks وRace Conditions

افترض أنك أرسلت `cancel()`، لكن هناك دفعة صوت قديمة كانت بالفعل في الطريق عبر الشبكة. إن أضافها العميل مباشرة إلى طابور التشغيل فستسمع جزءاً من الاستجابة السابقة **بعد** بدء المستخدم كلامه.

حل هندسي شائع هو إعطاء كل استجابة **معرّفاً فريداً** أو `generation_id`، مع رقم جيل `epoch` يتغير عند المقاطعة. يقبل المشغّل الدفعات التي تحمل الجيل النشط فقط، ويرفض الدفعات المتأخرة من الجيل الملغى.

```python
# Pseudocode: run this guard before enqueueing audio.
if chunk.generation_id != session.active_generation_id:
    return  # Discard stale audio
player.enqueue(chunk)
```

يجب كذلك حماية أحداث `playback_ack` من التكرار أو الوصول بترتيب مختلف: لا تسمح بتراجع مؤشر التشغيل، ولا تنقل إقرار جيل سابق إلى رد جديد.

**ملاحظة خاصة بالأدوات:** إلغاء استجابة LLM لا يعني التراجع تلقائياً عن طلب API خارجي نُفّذ بالفعل (مثل حجز موعد). عمليات الكتابة تحتاج idempotency keys وتأكيداً واضحاً وسياسة تعويض مستقلة. لا تخلط بين **إيقاف الكلام** و**إلغاء الفعل التجاري**.

## 7. Synchronizing Conversation State: ما الذي ندخله إلى ذاكرة النموذج؟

فكّر في سجلين منفصلين:

- **السجل الداخلي (Internal state):** ما طلبه المستخدم، نتائج الأدوات، نصوص تولدها النماذج، والمعرّفات والأحداث التقنية.
- **السجل الحواري (User-visible context):** ماذا قال المستخدم؟ وما الذي أمكن تشغيله فعلياً من كلام الوكيل؟

إذا توقفت الاستجابة عند 1500 ms فلا ينبغي نقل نص الـLLM الكامل تلقائياً إلى سجل الحوار. وإذا كانت لدينا مزامنة صوت/كلمات دقيقة يمكن الاحتفاظ بالكلمات التي انتهى تشغيلها فقط؛ أما إذا كانت المزامنة غير موثوقة، فالأفضل تمثيل آخر رسالة بأنها **انقطعت** بدلاً من اختراع قصّة عن الجملة المسموعة.

### مثال موثّق: OpenAI Realtime عبر WebSocket

في اتصال **WebSocket** الذي يدير فيه العميل الصوت، يوجّه توثيق OpenAI إلى إيقاف التشغيل ومتابعة الزمن المشغّل ثم إرسال `conversation.item.truncate` لقص الجزء غير المشغّل:[^openai-realtime]

```json
{
  "type": "conversation.item.truncate",
  "item_id": "item_1234",
  "content_index": 0,
  "audio_end_ms": 1500
}
```

هذا **مثال خاص بواجهة OpenAI Realtime** وليس رسالة قياسية لـPipecat أوWebRTC. ويشير التوثيق إلى أنه عند القص تزال الكتابة المقابلة للجزء غير المسموع من السياق؛ لا تضمن الواجهة إنتاج Transcript مقصوص متزامن بدقة كلمةً بكلمة. أما اتصال **WebRTC/SIP** المُدار من الخدمة فيختلف في آلية إدارة مخزن الصوت والقص.[^openai-realtime]

### ماذا عن LiveKit؟

يوضح توثيق LiveKit أن مقاطعة الوكيل توقف كلامه وتقص سجل المحادثة إلى الجزء المشغّل، مع خيارات للتعامل مع المقاطعات الخاطئة؛ التفاصيل تعتمد على وضع الـTurn Detection ونمط الوكيل.[^livekit-turns] الفكرة ليست نقل نفس أحداث OpenAI إلى كل إطار عمل، بل **فهم المسؤوليات** ثم استخدام APIs المناسبة لذلك التنفيذ.

## 8. مختبر Python: محاكاة مقاطعة مع مزامنة السياق

**الهدف:** اختبار منطق إدارة الاستجابة دون نموذج LLM أو TTS حقيقي ودون ميكروفون.

**الملفات داخل المجلد نفسه:**

- `examples/interruption_playback_lab.py` — مدير تشغيل وسجل أحداث ومقاطعة.
- `examples/test_interruption_playback_lab.py` — حالات اختبار تلقائية.
- `examples/make_interruption_figures.py` — توليد الشكلين التعليميين.
- `examples/10-BARGE-IN-LAB-README.md` — خطوات التشغيل والحدود.

### نموذج البيانات

يتتبع المختبر `generated_ms`, `synthesized_ms`, `transmitted_ms`, `buffered_ms`, و`played_ms`. يسمح برفع مؤشر `played_ms` فقط بإقرار مشغّل صريح، وبشرط ألا يزيد عن الصوت المخزّن وألا يتراجع.

```python
from interruption_playback_lab import PlaybackController

controller = PlaybackController()
epoch = controller.start("assistant_item_1", total_ms=3000)
for stage, ms in [
    ("generated", 3000),
    ("synthesized", 2600),
    ("transmitted", 2400),
    ("buffered", 2100),
]:
    controller.advance(stage, ms, epoch)

controller.acknowledge_playback(1000, epoch)
controller.pause_for_candidate(epoch)
plan = controller.confirm_interruption(epoch, final_played_ms=1200)
print(plan)
```

**مخرج مختصر متوقع:**

```text
played_ms = 1200
unheard_buffered_ms = 900
unheard_generated_ms = 1800
```

ثم يمكن ربط `item_id` و`audio_end_ms` برسالة القص الخاصة بمزوّد يدعم ذلك، مثل OpenAI Realtime WebSocket، **فقط في موضع الربط مع الـSDK الحقيقي**.

### تشغيل المختبر والاختبارات

```bash
cd Voice-Agent-Series/examples
python interruption_playback_lab.py
python -m unittest test_interruption_playback_lab -v
```

> [!important] ما الذي اختبرناه؟
> اختبارات منطقية محلية تشمل: الترتيب الصحيح للمراحل، منع الإقرار المتراجع، إيقاف المقاطعة الخاطئة واستئنافها، قطع الرسالة وفق `played_ms`، رفض Late Chunks وإقرارات الجيل القديم، وتجنّب اعتبار «أُرسِل» مرادفاً لـ«سُمِع». **لم نختبر زمناً حقيقياً أو اتصال WebRTC أو صوتاً يصل إلى سماعة فعلية.**

## 9. ماذا تقيس عند الاختبار الحقيقي؟

| المقياس | كيفية القياس | لماذا يهم؟ |
|---|---|---|
| Interruption-stop latency | من ظهور كلام المستخدم الذي اعتُبر مقاطعة حتى تأكيد توقف صوت المشغّل | هل الوكيل يواصل الكلام فوق المستخدم؟ |
| False interruption rate | إيقافات غير مقصودة / فرص المقاطعة المقاسة وفق مجموعة اختبار معرفة | هل «آها» أو ضوضاء بسيطة تسبب إيقافاً؟ |
| Stale-audio leak rate | حالات وصل فيها صوت جيل ملغى إلى التشغيل / مجموع حالات المقاطعة | هل تظهر بقايا الرد القديم؟ |
| Context mismatch rate | حالات احتوى فيها الحوار على ادعاءات صوتية غير مشغّلة / الحالات المراجعة | هل يفترض النظام أن المستخدم سمع ما لم يُشغّل؟ |
| Resume quality | عدد وتوقيت حالات الاستئناف الخاطئ أو المكرر | هل يتكرر الصوت بعد إنذار كاذب؟ |

لا تضع هدفاً رقمياً ثابتاً دون اختبار نوع الجهاز والشبكة واللغة وسياسة المقاطعة. استخدم P50 وP95 وحالات الضجيج والصدى والمستخدم المتردد، وليس تسجيلات مثالية فقط.

## 10. أخطاء متكررة وحلولها

| الخطأ | أثره | التصحيح |
|---|---|---|
| تأخير إيقاف الصوت إلى أن ينتهي STT | كلام متداخل | أوقف المشغّل مبكراً ثم أكد النية |
| إلغاء LLM دون مسح طابور العميل | صوت قديم بعد المقاطعة | Flush / Clear / Generation IDs |
| اعتبار النص المولّد كلاماً مسموعاً | سياق غير صحيح | Playback acknowledgements + آلية قص آمنة |
| قبول الإقرارات المتأخرة | ارتباك حالة المحادثة | Epoch ومؤشر monotonic مرتبط بـitem_id |
| عدّ كل صوت مقاطعة | تجمد الصوت باستمرار | Echo cancellation وAdaptive interruption |
| افتراض أن إلغاء الرد يلغي حجزاً | آثار جانبية غير قابلة للاسترجاع | فصل إجراءات الأدوات عن دورة الصوت |

## 11. مشروع تطبيقي صغير

وسّع مختبرك ليجتاز خمسة سيناريوهات: (1) مقاطعة حقيقية عند 1200ms، (2) Backchannel لا يوقف الإجابة نهائياً، (3) وصول TTS متأخر بعد الإلغاء، (4) إقرار تشغيل مكرر، (5) تصحيح مستخدم يستلزم إعادة صياغة الرد. بعد ذلك صِل المختبر بمشغّل صوت فعلي واستخدم أحداث إقرار حقيقية بدلاً من القيم الاصطناعية.

> [!success] الخلاصة
> **المقاطعة ليست حدثاً صوتياً واحداً؛ إنها عملية مزامنة موزعة.** يبدأ النجاح من استشعار الكلام، لكنه لا يكتمل إلا عندما تتوقف مخازن التشغيل والعمل الجاري، ويُهمل الصوت المتأخر، وتصبح ذاكرة الوكيل متسقة مع ما أمكن تشغيله فعلياً.

### أسئلة للتأكد من الفهم

1. لماذا لا يكفي حدث `response.done` لإثبات اكتمال تشغيل الكلام؟
2. كيف تتعامل مع `audio_chunk` يصل بعد تأكيد الإلغاء؟
3. لماذا يحتاج النظام إلى `item_id` و`generation_id` معاً؟
4. ما الفرق بين مقاطعة خاطئة وإيقاف مؤكد؟
5. متى يكون قص النص كلمة بكلمة غير موثوق؟

**التالي:** [[11-Latency-and-Streaming-Optimization-AR|المقالة الحادية عشرة — Latency & Streaming Optimization]]: كيف نخفض زمن التفاعل من دون التضحية باستقرار المحادثة؟

## المراجع والمصادر

[^openai-realtime]: [OpenAI API — Realtime conversations, Interruption and Truncation](https://developers.openai.com/api/docs/guides/realtime-conversations) — توثيق التعامل مع المقاطعات وقص الصوت في WebSocket، والفروق مع WebRTC/SIP (تم الاطلاع: 2026-11-21).
[^livekit-turns]: [LiveKit Docs — Turn handling and Interruptions](https://docs.livekit.io/agents/logic/turns/) — سياسات المقاطعة والقص والاستئناف.
[^livekit-adaptive]: [LiveKit Docs — Adaptive interruption handling](https://docs.livekit.io/agents/logic/turns/adaptive-interruption-handling/) — التمييز بين المقاطعة الحقيقية وBackchannel.
[^mdn-output]: [MDN — AudioContext.getOutputTimestamp()](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/getOutputTimestamp) و[AudioContext.outputLatency](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/outputLatency) — تقديرات تقدم الإخراج وتأخيره.

---
*هذه المقالة مادة تعليمية، وليست وصفاً مضموناً لسلوك جميع إصدارات المكتبات أو لجميع الشبكات والأجهزة. اختبر واجهات مزودك الفعلية قبل النشر.*
