# Article 11 — Latency & Streaming Optimization Lab

## العربية | تشغيل مختبر قياس التأخير

المختبر تعليمي ويعتمد على **36 دوراً صوتياً اصطناعياً**؛ ليس Benchmark، ولا يقيس مزود STT/LLM/TTS أو تشغيل متصفح فعلي.

من جذر المجلد `Voice-Agent-Series` شغّل:

```bash
python examples/latency_streaming_lab.py
python examples/latency_streaming_lab.py --json
python -m unittest discover -s examples -p 'test_latency_streaming_lab.py' -v
python -m unittest discover -s examples -p 'test_*.py' -q
```

لإعادة توليد الرسومات (اختياري، يتطلب Matplotlib):

```bash
python -m pip install matplotlib
python examples/make_latency_figures.py
```

يحتوي `11-synthetic-traces.jsonl` على حالات `quiet-room` و`noisy-room` و`high-jitter`، وكل منها 12 دوراً. النسبة المئوية تستخدم **nearest-rank**، ولذلك تكون P95 مع 12 عينة مساوية للعينة الأكبر. ليست هذه عينة كافية لاستنتاج أداء منتج حقيقي.

### بنية الأحداث

أدخل لكل دور الحقول التالية ضمن **خط زمني واحد محسوب من ساعة monotonic مشتركة أو محاذاة صحيحة**:

- `user_speech_end_ms`, `turn_committed_ms`, `transcript_final_ms`
- `llm_request_ms`, `llm_first_token_ms`, `text_ready_for_tts_ms`
- `tts_request_ms`, `tts_first_chunk_ms`
- `client_audio_arrived_ms`, `client_first_audible_ms`
- `turn_id`, `scenario`, واختيارياً `clock_id`

الملف `latency_streaming_lab.py` يحسب `e2e_to_first_audible_ms` ويعرض فترات مستقلة للمراحل. **لا تجمع أزمنة المراحل للحصول على E2E**، فقد تعمل STT وEndpointing بالتزامن. العلامة `client_first_audible_ms` هي **تقدير يبدأ مع أول تشغيل لمحتوى صوتي غير صامت** على العميل؛ لا تثبت سماعه فعلاً لدى الإنسان.

في الإنتاج لا يمكن طرح ساعة الخادم من ساعة المتصفح مباشرةً. استخدم tracing موزعاً واضحاً، وقياسات محلية، ومحاذاة/تقدير فروق الساعة عند الحاجة. تجنب حفظ صوت المستخدم أو محتوى المحادثة في Telemetry دون أساس قانوني وموافقة ملائمة.

## English | Run the lab

This is a **provider-neutral synthetic telemetry exercise**, not a real audio benchmark. Python 3.10+ and the standard library are sufficient to run the lab and tests; Matplotlib is needed only to regenerate images.

```bash
cd Voice-Agent-Series
python examples/latency_streaming_lab.py
python examples/latency_streaming_lab.py --json
python -m unittest discover -s examples -p 'test_latency_streaming_lab.py' -v
```

Optional:

```bash
python -m pip install matplotlib
python examples/make_latency_figures.py
```

The bundled JSONL trace has 36 generated turns, grouped into three scenarios. Nearest-rank p50/p95/p99 describe the *sample distribution*; they are not population guarantees. With only 12 values per scenario, p95 is the maximum value.

**Important timing caveat:** All timestamps *within each row* are expressed on one synthetic aligned monotonic timeline. Real client and server timestamps require an explicit correlation/alignment strategy. Do not subtract raw clocks from independent machines.

### Expected sample output

```text
Synthetic example only — NOT a voice-provider benchmark
Scenario                n    p50 (ms)    p95 (ms)    p99 (ms)
high-jitter            12         730        1900        1900
noisy-room             12         710        1400        1400
quiet-room             12         540         670         670
```

### What this lab does NOT do

- No Pipecat, WebRTC, Deepgram, OpenAI, Cartesia, Piper, or LiveKit API calls.
- No live microphone capture or browser audio playback measurement.
- No realistic speech quality or tool-correctness benchmarks.
- No guarantee that p95 from a tiny sample predicts production behavior.

Official background references: [LiveKit session traces](https://docs.livekit.io/reference/agents/session-traces/), [LiveKit benchmarking](https://docs.livekit.io/reference/agents/benchmarking/), [Pipecat metrics](https://reference-server.pipecat.ai/en/latest/api/pipecat.metrics.metrics.html), and [MDN high precision timing](https://developer.mozilla.org/en-US/docs/Web/API/Performance_API/High_precision_timing).
