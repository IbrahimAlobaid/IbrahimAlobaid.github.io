---
title: "Voice AI Engineering — Series Roadmap"
aliases:
  - "خارطة سلسلة الوكلاء الصوتيين"
  - "Voice Agent Engineering Roadmap"
tags:
  - voice-ai
  - voice-agents
  - ai-engineering
  - learning-roadmap
status: published
updated: 2026-11-21
---

# Voice AI Engineering — From Zero to Production

![[assets/voice-agent-cover.png]]

> [!abstract] فكرة السلسلة | Series mission
> **AR:** رحلة هندسية لبناء وكيل صوتي يفهم الكلام، يستجيب طبيعياً، ويتعامل مع المقاطعات، ثم يتحول من تجربة إلى نظام جاهز للإنتاج.
>
> **EN:** A progressive engineering journey from understanding speech to building natural, interruption-aware, production-ready voice agents.

**الجمهور:** الطلاب، ومطورو Python، ومهندسو الذكاء الاصطناعي الراغبون في دخول هندسة الوكلاء الصوتيين.

**أسلوب كل مقالة:** سؤال عملي → شرح المفهوم → مخطط → مثال → أخطاء شائعة → تجربة صغيرة → مصادر.

**اللغتان:** المقالات الخمس الأولى متاحة بالعربية والإنجليزية؛ وتُستخدم المصطلحات التقنية الإنجليزية عند أول ظهور لها في النسخة العربية.

## المستوى الأول | Foundations

| # | المقالة / Article | ما ستتعلمه | المخرج العملي |
|---|---|---|---|
| 01 | **What Is a Voice AI Agent?** ما هو الوكيل الصوتي الذكي؟ | الصورة الكبرى والمكونات ومفهوم المحادثة الطبيعية | وصف معماري لأول وكيل صوتي |
| 02 | **Digital Audio for Developers** الصوت الرقمي للمطورين | Samples، PCM، Sample Rate، Chunks، Codecs | قراءة ملف صوتي وتحليل خصائصه |
| 03 | **Speech Recognition (STT)** تحويل الكلام إلى نص | Streaming STT، partial/final transcripts، اللغات واللهجات | تجربة تعرف كلام مباشر |
| 04 | **Text to Speech (TTS)** تحويل النص إلى كلام | تهيئة النص، طبيعية النطق، Prosody، Streaming، RTF | تجربة Piper محلية وقياس أول دفعة صوتية |

## المستوى الثاني | Build the Agent

| # | المقالة / Article | ما ستتعلمه | المخرج العملي |
|---|---|---|---|
| 05 | **LLM & Conversation State** | الذاكرة القصيرة، السياق، التعليمات، تصحيح المعلومات والمقاطعات | مدير سياق مع اختبارات Python |
| 06 | **Cascaded vs. Speech-to-Speech** | STT→LLM→TTS مقابل النماذج الصوتية المباشرة؛ المفاضلات | اختيار معماري مدروس |
| 07 | **Your First Voice Agent with Python & Pipecat** | بناء Pipeline بسيط وتشغيله | وكيل صوتي محلي يعمل |
| 08 | **Real-Time Transport: WebRTC & WebSockets** | الصوت المتدفق، Jitter، WebRTC، NAT/STUN/TURN | اتصال صوتي مباشر من المتصفح |

## المستوى الثالث | Natural, Real-Time Conversation

| # | المقالة / Article | ما ستتعلمه | المخرج العملي |
|---|---|---|---|
| 09 | **VAD, Endpointing & Turn Detection** | متى بدأ المستخدم الكلام؟ متى انتهى؟ | تحسين قرارات تبادل الأدوار |
| 10 | **Interruptions, Barge-In & Playback State** | إيقاف الصوت، إلغاء العمل الجاري، ضبط السياق | محادثة تقبل المقاطعة |
| 11 | **Latency & Streaming Optimization** | TTFT/TTFB، التداخل بين المراحل، P50/P95 | لوحة قياس التأخير |
| 12 | **Robust Voice AI in the Wild** | الضجيج، تردد الكلام، اللهجات، التصحيح، Echo | مجموعة اختبارات واقعية |

## المستوى الرابع | Production & Advanced Systems

| # | المقالة / Article | ما ستتعلمه | المخرج العملي |
|---|---|---|---|
| 13 | **Tools, RAG & Agent Workflows** | الاستعلامات الخارجية، تأكيد الأفعال، إدارة الأخطاء | وكيل ينفذ مهمة مفيدة |
| 14 | **Safety, Privacy & Security** | الموافقة، بيانات الصوت، PII، الحماية، ضوابط المجال | قائمة جاهزية أمنية |
| 15 | **Evaluation, Observability & Deployment** | سيناريوهات التقييم، السجلات، التنبيهات، النشر | حزمة اختبارات ومراقبة |
| 16 | **Capstone: Production-Grade Multimodal Agent** | تصميم Voice/Video Agent متعدد المكونات، الفشل والاستعادة | مخطط ونموذج مشروع متكامل |

> [!tip] تسلسل التنفيذ
> تتدرج المقالات من **الفهم → التنفيذ → تحسين التفاعل → الإنتاج**. الأدوات أمثلة قابلة للاستبدال؛ الأساس هو فهم المسؤولية الهندسية لكل مكوّن.

## ابدأ من هنا | Start here

- [[01-What-is-a-Voice-Agent-AR|المقالة الأولى — العربية]]
- [[01-What-is-a-Voice-Agent-EN|Article 01 — English]]
- [[02-Digital-Audio-for-Developers-AR|المقالة الثانية — الصوت الرقمي للمطورين]]
- [[02-Digital-Audio-for-Developers-EN|Article 02 — Digital Audio for Developers]]
- [[03-Speech-to-Text-AR|المقالة الثالثة — التعرف على الكلام وتحويله إلى نص]]
- [[03-Speech-to-Text-EN|Article 03 — Speech-to-Text]]
- [[04-Text-to-Speech-AR|المقالة الرابعة — تحويل النص إلى صوت طبيعي]]
- [[04-Text-to-Speech-EN|Article 04 — Text-to-Speech & Streaming]]
- [[05-LLM-and-Conversation-State-AR|المقالة الخامسة — عقل الوكيل الصوتي وإدارة سياق المحادثة]]
- [[05-LLM-and-Conversation-State-EN|Article 05 — LLM & Conversation State]]

## مصادر تأسيسية | Foundational sources

1. [LiveKit Agents documentation](https://docs.livekit.io/agents/) — architectures, pipelines, turn taking and deployment.
2. [Pipecat documentation](https://docs.pipecat.ai/) — real-time audio pipelines and orchestration.
3. [OpenAI Realtime conversations](https://developers.openai.com/api/docs/guides/realtime-conversations) — audio sessions, interruption and truncation behavior.
4. [MDN WebRTC API](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API) — browser-side real-time communication fundamentals.

---

*Editorial note: This roadmap is a learning plan, not a claim that all technologies or model offerings are permanent; consult current official documentation when implementing.*
