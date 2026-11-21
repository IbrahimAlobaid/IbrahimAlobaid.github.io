# Voice AI Engineering — Obsidian Pack

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
3. افتح `00-Series-Roadmap.md`، ثم اتبع روابط المقالات الخمس الأولى باللغتين.
4. افتح المقالات في **Reading view** لعرض الصور ومخططات Mermaid وCallouts.
5. للتعديل على المخططات، حرّر الكتل التي تبدأ بـ Mermaid داخل ملفات Markdown.

**مهم:** أبقِ مجلد `assets/` بجانب ملفات المقالات حتى تعمل الصور المضمنة بصيغة روابط Obsidian الداخلية للصور.

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
