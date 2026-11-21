# Voice AI Engineering — Obsidian Pack

## Article 16 — Production-Grade Voice Agent Capstone (SERIES FINALE)

- `16-Production-Grade-Voice-Agent-Capstone-AR.md` — المشروع النهائي بالعربية: بناء وكيل صوتي تجريبي، أدوات آمنة، وإدارة الموافقات والنشر.
- `16-Production-Grade-Voice-Agent-Capstone-EN.md` — English capstone article: complete voice pipeline, tools, security boundaries, and evaluation.
- `assets/capstone-voice-agent-cover.png` — AI-generated capstone cover.
- `assets/capstone-architecture.png` — Pipecat/browser/domain architecture.
- `assets/capstone-safe-actions.png` — proposal, separate authorization, simulated commit.
- `assets/capstone-release-readiness.png` — verified offline tests vs unverified real-audio/prod requirements.
- `examples/capstone_domain.py` — offline domain with synthetic FAQ, slots, state isolation and simulated authorization.
- `examples/capstone_voice_agent.py` — actual Pipecat-style voice pipeline with STT+LLM+TTS and non-committing tools (voice runtime requires keys and independent verification).
- `examples/capstone_demo_cli.py` — no-network walkthrough.
- `examples/test_capstone_domain.py` — 38 domain tests.
- `examples/capstone-agent.env.example` — environment variable names, without credentials.
- `examples/make_capstone_figures.py` — regenerate three schematic diagrams.
- `examples/16-CAPSTONE-README.md` — step-by-step setup, test results and production gaps.

**Series status:** All 16 articles are supplied in Arabic and English. The capstone voice runtime was not exercised with real provider credentials; the local domain tests were run.


## Article 15 — Evaluation, Observability & Deployment (NEW)

- `15-Evaluation-Observability-and-Deployment-AR.md` — المقالة الخامسة عشرة بالعربية: Quality Gates، Tracing، SLOs، Docker وCI/CD.
- `15-Evaluation-Observability-and-Deployment-EN.md` — English article: evaluating and operating voice agents with measured releases.
- `assets/evaluation-observability-cover.png` — article cover matching the series identity.
- `assets/evaluation-trace-waterfall.png` — synthetic overlapping timeline, first audible output.
- `assets/evaluation-quality-gates.png` — passing baseline vs blocked regression, synthetic.
- `assets/evaluation-private-observability.png` — allowlisted telemetry and privacy boundary.
- `examples/voice_eval_observability_lab.py` — offline evaluation metrics, failure checks and release gate.
- `examples/test_voice_eval_observability_lab.py` — 30 tests for article 15.
- `examples/15-synthetic-evaluation-cases.jsonl` — 24 baseline and 8 intentionally regressed cases.
- `examples/15-baseline-report.json` and `examples/15-regression-report.json` — reproducible reports.
- `examples/make_evaluation_observability_figures.py` — rebuild the article figures.
- `examples/15-deployment-demo/` — standalone diagnostic HTTP service, Docker Compose and CI workflow example (NOT a voice agent).
- `examples/15-EVALUATION-OBSERVABILITY-DEPLOYMENT-README.md` — setup, expected exits and limitations.


## المحتويات

- `00-Series-Roadmap.md` — خارطة سلسلة مؤلفة من 16 مقالة، مرتبة من المستوى المبتدئ إلى الإنتاج.
- `01-What-is-a-Voice-Agent-AR.md` — المقالة الأولى بالعربية.
- `01-What-is-a-Voice-Agent-EN.md` — English edition of Article 01.
- `02-Digital-Audio-for-Developers-AR.md` — المقالة الثانية بالعربية: أساسيات الصوت الرقمي.
- `02-Digital-Audio-for-Developers-EN.md` — Article 02 in English: digital audio fundamentals.
- `03-Speech-to-Text-AR.md` — المقالة الثالثة بالعربية: التعرف الآلي على الكلام، Streaming STT، وWER.
- `03-Speech-to-Text-EN.md` — Article 03 in English: Speech-to-Text fundamentals.
- `04-Text-to-Speech-AR.md` — المقالة الرابعة بالعربية: تحويل النص إلى كلام، Prosody، Streaming TTS، وقياسات الأداء.
- `04-Text-to-Speech-EN.md` — Article 04 in English: natural speech synthesis, streaming, and measurement.
- `05-LLM-and-Conversation-State-AR.md` — المقالة الخامسة بالعربية: LLM، إدارة السياق، التصحيح، وحالة المحادثة.
- `05-LLM-and-Conversation-State-EN.md` — Article 05 in English: LLM and Conversation State.
- `06-Cascaded-vs-Speech-to-Speech-AR.md` — المقالة السادسة بالعربية: مقارنة Cascaded وRealtime Speech-to-Speech وHybrid.
- `06-Cascaded-vs-Speech-to-Speech-EN.md` — Article 06 in English: architecture tradeoffs, interruption handling, and latency.
- `07-Build-First-Voice-Agent-with-Pipecat-AR.md` — المقالة السابعة بالعربية: بناء أول وكيل صوتي باستخدام Pipecat، مع Quickstart موثّق ومخططات واختبارات.
- `07-Build-First-Voice-Agent-with-Pipecat-EN.md` — Article 07 in English: implementing a browser-based Pipecat voice agent.
- `09-VAD-Endpointing-and-Turn-Detection-AR.md` — المقالة التاسعة بالعربية: VAD وEndpointing وتحديد نهاية دور المستخدم.
- `09-VAD-Endpointing-and-Turn-Detection-EN.md` — Article 09 in English: acoustic segmentation versus conversational turn completion.
- `10-Interruptions-Barge-In-and-Playback-State-AR.md` — المقالة العاشرة: هندسة المقاطعات ومؤشرات الصوت المشغّل ومزامنة سياق الحوار.
- `10-Interruptions-Barge-In-and-Playback-State-EN.md` — Article 10 in English: interruption, playback reconciliation and context safety.
- `12-Robust-Voice-AI-in-the-Wild-AR.md` — المقالة الثانية عشرة بالعربية: متانة الوكلاء الصوتيين في الضجيج والصدى وتداخل الأصوات واللهجات والتعافي.
- `12-Robust-Voice-AI-in-the-Wild-EN.md` — Article 12 in English: noise, echo, accents, code-switching and safe network recovery.

- `13-Tools-RAG-and-Agent-Workflows-AR.md` — المقالة الثالثة عشرة: RAG، أدوات الوكيل الصوتي، MCP، الصلاحيات، والتأكيد الآمن.
- `13-Tools-RAG-and-Agent-Workflows-EN.md` — Article 13: tools, retrieval, agent workflows, authorization, and safe execution.
- `assets/tools-rag-workflows-cover.png` — غلاف المقالة الثالثة عشرة.
- `assets/tools-rag-vs-actions.png` — مخطط البحث المعرفي مقابل تنفيذ الأوامر.
- `assets/tools-approval-state-machine.png` — دورة حياة الموافقة على إجراء.
- `assets/tools-voice-ux-timeline.png` — مخطط زمني تعليمي لتجربة المستخدم.
- `examples/voice_tools_rag_workflow_lab.py` — مختبر مستقل لاستدعاء الأدوات ومحاكاة الحجوزات مع Idempotency.
- `examples/test_voice_tools_rag_workflow_lab.py` — 26 اختباراً للمقالة الثالثة عشرة.
- `examples/make_tools_rag_figures.py` — إعادة توليد الرسومات التعليمية.
- `examples/13-TOOLS-RAG-WORKFLOW-README.md` — تعليمات تشغيل المختبر وحدوده.
- `assets/robust-voice-ai-cover.png` — غلاف المقالة الثانية عشرة.
- `assets/robustness-noise-mixture.png` — الإشارة الصوتية والتشويش (مثال اصطناعي).
- `assets/robustness-decision-policy.png` — سياسة اتخاذ قرار تعليمية عند عدم اليقين.
- `assets/robustness-recovery-timeline.png` — مخطط إعادة الاتصال ومنع إعادة الحزم القديمة.
- `examples/voice_robustness_lab.py` — مختبر سياسة قرار محلي مستقل عن APIs.
- `examples/12-synthetic-resilience-cases.jsonl` — 18 حالة اصطناعية متنوّعة.
- `examples/test_voice_robustness_lab.py` — 36 اختباراً للمقالة الثانية عشرة.
- `examples/make_robustness_figures.py` — إعادة توليد 3 رسوم تعليمية.
- `examples/12-ROBUSTNESS-LAB-README.md` — دليل التشغيل والحدود.
- `11-Latency-and-Streaming-Optimization-AR.md` — المقالة الحادية عشرة: هندسة Latency وStreaming وقياس أول صوت مسموع وP50/P95.
- `11-Latency-and-Streaming-Optimization-EN.md` — Article 11 in English: latency engineering, tracing, and streaming optimization.
- `assets/latency-streaming-cover.png` — غلاف المقالة الحادية عشرة.
- `assets/latency-stage-overlap.png` — مخطط أزمنة المراحل المتداخلة (اصطناعي).
- `assets/latency-p50-p95.png` — مقارنة الذيل البطيء والنسب المئوية (36 عينة اصطناعية).
- `assets/latency-streaming-overlap.png` — مثال على التداخل بين التنفيذ المتسلسل وStreaming.
- `examples/latency_streaming_lab.py` — أداة محلية لحساب E2E وP50/P95/P99 من أحداث اصطناعية.
- `examples/11-synthetic-traces.jsonl` — 36 دوراً اصطناعياً موزعة على ثلاث بيئات.
- `examples/test_latency_streaming_lab.py` — 27 اختباراً للمقالة الحادية عشرة.
- `examples/make_latency_figures.py` — سكربت توليد المخططات الثلاثة.
- `examples/11-LATENCY-LAB-README.md` — دليل التشغيل وحدود المختبر.
- `assets/barge-in-playback-cover.png` — غلاف المقالة العاشرة.
- `assets/barge-in-playback-cursors.png` — مؤشر تقدم المراحل الخمس (أرقام صناعية).
- `assets/barge-in-cancellation-flow.png` — استئناف المقاطعة الخاطئة أو إيقاف المقاطعة المؤكدة.
- `examples/interruption_playback_lab.py` — مختبر Python مستقل لإدارة الحالة والمقاطعات.
- `examples/test_interruption_playback_lab.py` — 21 اختبار وحدة للمقالة العاشرة.
- `examples/make_interruption_figures.py` — إعادة توليد رسمين تعليميين.
- `examples/10-BARGE-IN-LAB-README.md` — دليل التجربة وحدودها.
- `assets/turn-detection-cover.png` — غلاف المقالة التاسعة.
- `assets/turn-detection-timeline.png` — رسم تعليمي لمقاطع الكلام والصمت (بيانات اصطناعية).
- `assets/turn-detection-tradeoff.png` — رسم يوضح موازنة التأخير والإغلاق المبكر (أرقام توضيحية غير مقاسة).
- `examples/turn_detection_lab.py` — آلة حالات Python لتجربة VAD الاحتمالي الاصطناعي وEndpointing.
- `examples/test_turn_detection_lab.py` — 18 اختباراً للمختبر التاسع.
- `examples/make_turn_detection_figures.py` — سكربت إعادة توليد الرسمين.
- `examples/09-TURN-DETECTION-LAB-README.md` — دليل المختبر التاسع وإجراءاته وحدوده.
- `08-Real-Time-Audio-Transport-AR.md` — المقالة الثامنة بالعربية: WebRTC وWebSockets، وICE/STUN/TURN، والتشخيص ومختبر نقل الصوت.
- `08-Real-Time-Audio-Transport-EN.md` — Article 08 in English: real-time audio transport, WebRTC diagnostics, and a local WebSocket lab.
- `assets/real-time-transports-cover.png` — غلاف المقالة الثامنة.
- `assets/transport-architecture.png` — مقارنة مرئية بين WebRTC وWebSockets.
- `assets/transport-jitter-timeline.png` — مخطط تعليمي لتفاوت وصول الحزم والفقد (أرقام اصطناعية).
- `examples/transport_network_lab.py` — مختبر Python بدون شبكة يشرح Jitter والفقد والتأخير.
- `examples/test_transport_network_lab.py` — 16 اختباراً للمختبر الثامن.
- `examples/make_transport_figures.py` — مولّد الرسوم باستخدام matplotlib.
- `examples/ws_voice_demo/` — تجربة تشغيل صوت محلي من المتصفح عبر WebSocket وAudioWorklet.
- `examples/08-TRANSPORT-LAB-README.md` — طريقة تشغيل الأمثلة وحدودها الأمنية والتقنية.
- `assets/first-pipecat-agent-cover.png` — غلاف المقالة السابعة.
- `assets/pipecat-first-agent-pipeline.png` — مسار المعالجة من الميكروفون إلى السماعة.
- `assets/pipecat-session-lifecycle.png` — دورة حياة الجلسة والمقاطعات.
- `examples/pipecat_first_agent.py` — كود وكيل صوتي تجريبي باستخدام Pipecat 1.x.
- `examples/pipecat_pipeline_lab.py` — مختبر زمني محلي دون APIs.
- `examples/test_pipecat_pipeline_lab.py` — اختبارات المختبر السابع.
- `examples/make_first_agent_figures.py` — مولّد الرسومات باستخدام Pillow وmatplotlib.
- `examples/07-FIRST-VOICE-AGENT-README.md` — تعليمات التشغيل التفصيلية.
- `examples/pipecat-first-agent.env.example` — مثال آمن لأسماء متغيرات البيئة.
- `assets/voice-architectures-cover.png` — غلاف المقالة السادسة.
- `assets/voice-architecture-comparison.png` — رسم ثلاث معماريات صوتية مقارنة.
- `assets/voice-architecture-latency.png` — مخطط زمني تعليمي بأرقام اصطناعية لا تمثل Benchmark.
- `examples/architecture_tradeoff_lab.py` — مختبر Python لتتبع التأخير والمقاطعات وتلخيص P50/P95 دون API.
- `examples/test_architecture_tradeoff_lab.py` — 12 اختباراً للمختبر السادس.
- `examples/make_architecture_figures.py` — إعادة توليد الرسوم التعليمية باستخدام matplotlib.
- `assets/llm-conversation-cover.png` — غلاف المقالة الخامسة.
- `assets/llm-context-layers.png` — أربع طبقات لسياق الوكيل الصوتي.
- `assets/llm-correction-timeline.png` — تصحيح بيانات المحادثة بعد المقاطعة.
- `examples/voice_context_lab.py` — مدير حالة deterministic مستقل عن أي LLM أو API.
- `examples/test_voice_context_lab.py` — خمسة عشر اختباراً لسلوك مدير السياق.
- `examples/make_context_figures.py` — سكربت اختياري لإعادة توليد الرسومات باستخدام matplotlib.
- `assets/tts-cover.png` — غلاف المقالة الرابعة.
- `assets/tts-prosody.png` — رسم توضيحي للتنغيم (بيانات اصطناعية تعليمية).
- `assets/tts-streaming-timeline.png` — رسم مراحل توليد الصوت وإرساله وتشغيله (أرقام توضيحية لا تمثل Benchmark).
- `examples/tts_metrics_lab.py` — قياس خصائص PCM/WAV وحساب RTF دون مكتبات خارجية.
- `examples/test_tts_metrics_lab.py` — تسعة اختبارات للمختبر الرابع.
- `examples/tts_piper_demo.py` — مثال اختياري لتوليد صوت حقيقي محلياً باستخدام Piper.
- `examples/stt_event_lab.py` — محاكي مستقل لأحداث Partial/Final مع حساب WER؛ لا يحتاج اتصالاً خارجياً.
- `examples/test_stt_event_lab.py` — سبعة اختبارات لمنطق STT.
- `examples/stt_microphone_demo.py` — تجربة محلية اختيارية باستخدام faster-whisper وميكروفون/ملف صوتي؛ ليست Streaming STT حقيقياً.
- `assets/stt-cover.png` — غلاف المقالة الثالثة.
- `assets/stt-partial-final.png` — رسم يوضح تطور التفريغ من Partial إلى Final ثم Turn End.
- `assets/stt-spectrogram-example.png` — رسم خصائص موجة اصطناعية وطيفها الترددي الزمني.
- `examples/digital_audio_lab.py` — تجربة Python عملية لتوليد WAV وتحليل PCM.
- `examples/test_digital_audio_lab.py` — اختبارات وحدة للمثال العملي (4 اختبارات).
- `examples/demo_16k_mono.wav` — نغمة تعليمية لمدة ثانية واحدة؛ ليست كلاماً.
- `assets/voice-agent-cover.png` — صورة الغلاف الأصلية.
- `assets/playback-state-ar.png` — رسم عربي يوضح الفرق بين الصوت المُنشأ والمسموع.
- `assets/playback-state-en.png` — English illustration of generated vs. played audio.
- `assets/digital-audio-cover.png` — صورة غلاف المقالة الثانية.
- `assets/sampling-explained.png` — رسم أخذ العينات من الإشارة المستمرة.
- `assets/quantization.png` — رسم توضيحي للتكميم.
- `assets/audio-chunks.png` — مخطط تقسيم الصوت إلى دفعات 20 ms.

## الاستخدام في Obsidian

1. فك ضغط الحزمة.
2. انسخ مجلد `Voice-Agent-Series` بالكامل إلى مجلد الـ Vault لديك (أو افتح المجلد Vault جديداً).
3. افتح `00-Series-Roadmap.md`، ثم اتبع روابط المقالات الاثنتي عشرة الأولى باللغتين.
4. افتح المقالات في **Reading view** لعرض الصور ومخططات Mermaid وCallouts.
5. للتعديل على المخططات، حرّر الكتل التي تبدأ بـ Mermaid داخل ملفات Markdown.

**مهم:** أبقِ مجلد `assets/` بجانب ملفات المقالات حتى تعمل الصور المضمنة بصيغة روابط Obsidian الداخلية للصور.

## تجربة المقالة الحادية عشرة — Latency & Streaming Optimization

من جذر المجلد:

```bash
python examples/latency_streaming_lab.py
python -m unittest discover -s examples -p 'test_latency_streaming_lab.py' -v
```

يعالج المختبر 36 دوراً صوتياً اصطناعياً، ويعرض P50/P95/P99 لكل سيناريو، ويوضح لماذا لا نُجمّع أزمنة STT وEndpointing والـLLM والصوت مباشرةً. **ليس Benchmark ولا اختبار ميكروفون/متصفح فعلياً**. راجع `examples/11-LATENCY-LAB-README.md`.

## تجربة المقالة العاشرة — Interruptions, Barge-In & Playback State

شغّل مختبر المزامنة من داخل `Voice-Agent-Series/examples`:

```bash
python interruption_playback_lab.py
python -m unittest test_interruption_playback_lab -v
```

المختبر لا يتصل بأي API ولا ينتج صوتاً حقيقياً. يعتمد على أزمنة اصطناعية ويبرهن على عدم الخلط بين `generated_ms` و`played_ms`، وقص السياق وفق إقرارات التشغيل، ومنع وصول بيانات أجيال ملغاة. انظر `examples/10-BARGE-IN-LAB-README.md` قبل الدمج في تطبيق فعلي.

## تجربة المقالة التاسعة — VAD & Turn Detection

شغّل المختبر المحلي من جذر `Voice-Agent-Series`:

```bash
python examples/turn_detection_lab.py
python -m unittest discover -s examples -p 'test_turn_detection_lab.py' -v
```

يعرض المختبر أحداث `speech_started` و`speech_stopped` و`turn_ended` و`interrupted_assistant` من احتمالات اصطناعية، ولا يستخدم ميكروفوناً أو نموذج VAD أو STT. انظر `examples/09-TURN-DETECTION-LAB-README.md` للاختبارات والحدود.

## تجربة المقالة الثامنة — WebRTC and WebSockets

الملفان `08-Real-Time-Audio-Transport-AR.md` و`08-Real-Time-Audio-Transport-EN.md` يتضمنان شرح ICE/STUN/TURN وجداول مقارنة وصوراً ومخططات Mermaid قابلة للتعديل. ابدأ بمختبر دون شبكة:

```bash
python examples/transport_network_lab.py
python -m unittest discover -s examples -p "test_*.py" -v
```

لتشغيل تجربة WebSocket الصوتية على جهازك، راجع `examples/08-TRANSPORT-LAB-README.md`. التجربة محلية ولا توفر خادم WebRTC أو STT/LLM/TTS؛ كما يجب استخدام سماعات رأس لتجنب الصدى. **لم يُختبر الميكروفون وتفاعل المتصفح في بيئة إنشاء الحزمة، لكن خادم WebSocket اجتاز اختبار اتصال ثنائي حقيقي محلي.**

## تجربة المقالة السابعة — First Voice Agent with Pipecat

اتبع [دليل Pipecat الرسمي](https://docs.pipecat.ai/pipecat/get-started/quickstart) لإنشاء تطبيق مستقل وتشغيله من المتصفح، مع إعداد مفاتيح Deepgram وOpenAI وCartesia داخل `.env` محلي غير منشور. بعد نجاح Quickstart يمكنك نقل `examples/pipecat_first_agent.py` إلى مشروع Pipecat وتشغيله هناك. **لم يُختبر الاتصال الصوتي الحقيقي داخل بيئة إعداد الحزمة؛ جرى فحص صياغة الملف فقط.**

اختبر منطق الأحداث والتأخير دون أي خدمة سحابية:

```bash
python examples/pipecat_pipeline_lab.py
python -m unittest discover -s examples -p "test_*.py" -v
```

القيم الزمنية في المختبر مصطنعة وليست قياسات لمزود أو إطار عمل. ارجع إلى `examples/07-FIRST-VOICE-AGENT-README.md` لمزيد من التفاصيل.

## تجربة المقالة السادسة — Voice Architectures

من داخل جذر المجلد `Voice-Agent-Series`:

```bash
python examples/architecture_tradeoff_lab.py
python -m unittest discover -s examples -p "test_*.py" -v
```

الأرقام داخل المختبر السادس **مصطنعة لأغراض تعليمية فقط**. لا يتصل المختبر بأي مزود ولا يقيس جودة نموذج حقيقي، لذا لا يجوز استخدامها لمقارنة منتجات أو أسعار.

## تجربة المقالة الرابعة — TTS

من جذر مجلد `Voice-Agent-Series`، يمكن تشغيل المختبر المحلي دون تثبيت نموذج صوتي:

```bash
python examples/tts_metrics_lab.py examples/demo_16k_mono.wav --compute-seconds 0.2
python -m unittest discover -s examples -p "test_*.py" -v
```

هذا الملف WAV نغمة اختبار لا صوت بشري، و`0.2` مثال زمن مدخل وليس قياساً فعلياً. للحصول على صوت ناطق حقيقي استخدم Piper بعد تحميل نموذج الصوت:

```bash
python -m pip install piper-tts
python -m piper.download_voices en_US-lessac-medium
python examples/tts_piper_demo.py --model en_US-lessac-medium.onnx --output examples/tts_piper_output.wav
```

يتطلب المثال الأخير نموذجاً قابلاً للتنزيل، ولم يُنفَّذ التوليد الصوتي بواسطة Piper داخل بيئة إعداد الحزمة. يسجّل زمن *أول دفعة صوتية مولدة* وليس أول صوت يسمعه المستخدم. تحقّق من تراخيص نماذج الصوت قبل الاستخدام الخارجي.

## تجربة المقالة الثالثة

نفّذ من داخل مجلد `Voice-Agent-Series`:

```bash
python examples/stt_event_lab.py
python -m unittest discover -s examples -p "test_*.py" -v
```

المختبر السابق يعمل بالكامل بدون إنترنت أو API أو ميكروفون. للتعرف الفعلي على الكلام عبر ملف صوتي أو الميكروفون، ثبّت المتطلبات الاختيارية:

```bash
python -m pip install faster-whisper sounddevice numpy
python examples/stt_microphone_demo.py --input path/to/speech.wav --language ar --model base
python examples/stt_microphone_demo.py --microphone --language ar --model base --windows 3 --window-seconds 4
```

**حدود مهمة:** يقوم تطبيق الميكروفون على نوافذ ثابتة ثم يفرغ كل نافذة. لا ينتج `interim transcripts` ولا يمثّل Streaming STT إنتاجياً، ولم يُختبر مع عتاد ميكروفون فعلي في هذه البيئة. قد يحتاج التشغيل الأول تنزيل أوزان النموذج، وقد تتطلب المكتبات تعريفات صوت خاصة بالنظام.

## التحرير والنشر

- ملفات المقالات تحتوي على YAML frontmatter وObsidian internal links وMermaid diagrams وfootnotes.
- غيّر `status: draft` إلى `published` بعد المراجعة والتحرير النهائي.
- روابط روابط Obsidian الداخلية للصفحات والصور مخصصة لـ Obsidian؛ عند النشر على مدونة أو LinkedIn Articles قد تحتاج تحويلها إلى Markdown/HTML عادي وروابط صور مطلقة.
- المراجع وروابطها مرفقة في نهاية كل مقالة؛ راجع إصدارات المكتبات قبل تنفيذ أمثلة الكود في المقالات التالية.

## Attributions

All artwork and diagram assets in this pack are original illustrations generated for this learning series. The technical references are credited and linked at the end of each article.

## تشغيل مختبر المقالة الثانية

شغّل من جذر `Voice-Agent-Series`:

```bash
python examples/digital_audio_lab.py
python examples/digital_audio_lab.py --input examples/demo_16k_mono.wav --chunk-ms 40
python -m unittest discover -s examples -p "test_*.py" -v
```

المثال يستخدم مكتبات Python القياسية فقط ولا يتصل بأي خدمة خارجية.

## تجربة المقالة الخامسة — Conversation State

من مجلد `Voice-Agent-Series` شغّل دون أي مكتبات خارجية أو اتصال بالإنترنت:

```bash
python examples/voice_context_lab.py
python -m unittest discover -s examples -p 'test_voice_context_lab.py' -v
```

الاختبارات تغطي النصوص المؤقتة والنهائية، تحديث الموعد، إبطال الموافقة عند التصحيح، تسجيل المقاطع المسموعة فقط، ومنع ترتيب خاطئ لتأكيد تشغيل الصوت. لا يجري المثال اتصالاً بنموذج LLM أو إجراء حجز حقيقي، بل يوضح إدارة الحالة القابلة للاختبار.

لإعادة توليد الشكلين التوضيحيين: `python -m pip install matplotlib` ثم `python examples/make_context_figures.py`.

## تجربة المقالة الثانية عشرة — Real-World Robustness

لتجربة سياسة التعافي وإدارة عدم اليقين دون ميكروفون أو API، نفّذ:

```bash
python examples/voice_robustness_lab.py
python examples/voice_robustness_lab.py --json
python -m unittest discover -s examples -p 'test_voice_robustness_lab.py' -v
```

يعالج المختبر **18 حالة اصطناعية**، ويختبر استقرار النص وتأكيد التفاصيل الحساسة ومنع حزم الصوت القديمة بعد إعادة الاتصال. يختبر ملف `test_voice_robustness_lab.py` **36 حالة وحدة**. ليس نموذج VAD/STT حقيقياً ولا Benchmark للصوت. اطلع على `examples/12-ROBUSTNESS-LAB-README.md` للإرشادات ومحددات الاستنتاج.


## تجربة المقالة الرابعة عشرة — Security, Privacy & Safety

المقالة متاحة باللغتين:

- [[14-Voice-AI-Security-Privacy-and-Safety-AR|الأمان والخصوصية والسلامة — العربية]]
- [[14-Voice-AI-Security-Privacy-and-Safety-EN|Security, Privacy & Safety — English]]

مختبر Python تعليمي يعمل دون API أو ميكروفون أو مكتبات إضافية:

```bash
python examples/voice_security_privacy_lab.py
python -m unittest discover -s examples -p 'test_voice_security_privacy_lab.py' -v
python -m unittest discover -s examples -p 'test_*.py'
```

يغطي الاختبار عزل المستأجرين، نطاق الصلاحيات، النصوص المؤقتة من STT، النصوص المسترجعة غير الموثوقة، الموافقة على الإجراء، انتهاء المهلة، واستئناف الجلسة ومنع التكرار، إضافة إلى الموافقة المستقلة على التسجيل والحذف الاصطناعي لبيانات وصفية فقط. **لا يمثل نظام أمن إنتاجياً ولا يخزّن أو يحذف تسجيلات حقيقية.** يرجى مراجعة `examples/14-SECURITY-PRIVACY-LAB-README.md` للحصول على الحدود والمراجع.
