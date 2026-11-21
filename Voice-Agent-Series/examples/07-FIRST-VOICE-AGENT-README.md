# Article 07 — First Voice Agent with Pipecat

This folder is part of **Voice AI Engineering — From Zero to Production**.

## Files

- `pipecat_first_agent.py`: illustrative live browser voice agent based on modern Pipecat 1.x APIs. Needs compatible installed Pipecat extras, Internet, and Deepgram/OpenAI/Cartesia API keys. It was syntax-checked but **not exercised in a live browser session here**.
- `pipecat-first-agent.env.example`: names of environment variables. **Do not commit or share your real credentials.**
- `pipecat_pipeline_lab.py`: independent, deterministic timestamp lab; uses no Pipecat packages, services, or network.
- `test_pipecat_pipeline_lab.py`: tests for the timestamp lab.
- `make_first_agent_figures.py`: rebuilds the original lesson figures, using `numpy`, `matplotlib`, and `pillow`.

## Recommended live application setup

Follow the official [Pipecat Quickstart](https://docs.pipecat.ai/pipecat/get-started/quickstart):

```bash
uv tool install "pipecat-ai[cli]"
pipecat init quickstart
cd pipecat-quickstart
cp .env.example .env
# Edit .env with the three API keys on your own machine.
uv sync
uv run bot.py
```

Connect at `http://localhost:7860/client`. The quickstart project is separate from this notes folder.

After confirming that quickstart works, you may copy `pipecat_first_agent.py` into its project and launch it with:

```bash
uv run pipecat_first_agent.py
```

The companion code is a learning example. Check your installed Pipecat version and dependencies before running it; no end-to-end API/audio test was performed when preparing this pack. The default teaching voice and prompt are English-oriented. Arabic speech requires confirming both STT language support and an appropriate TTS voice.

## Offline lab (no API keys)

From the **Voice-Agent-Series** folder:

```bash
python examples/pipecat_pipeline_lab.py
python -m unittest discover -s examples -p "test_*.py" -v
```

The numbers output by the script are synthetic and are **not** benchmarks.
