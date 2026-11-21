"""Article 07: a minimal browser voice agent for Pipecat 1.x.

Reference: https://github.com/pipecat-ai/pipecat/blob/main/examples/getting-started/06-voice-agent.py
Requires compatible Pipecat extras and three configured provider accounts.
This application is a teaching example, not a production deployment template.
"""

import os

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.workers.runner import WorkerRunner

load_dotenv()

# This first exercise uses the built-in browser-facing WebRTC runner only.
TRANSPORT_PARAMS = {
    "webrtc": lambda: TransportParams(audio_in_enabled=True, audio_out_enabled=True),
}


def require_keys() -> None:
    """Fail early without printing any secret values."""
    required = ("DEEPGRAM_API_KEY", "OPENAI_API_KEY", "CARTESIA_API_KEY")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError("Missing environment variables: " + ", ".join(missing))


async def run_bot(transport: BaseTransport, args: RunnerArguments) -> None:
    require_keys()

    stt = DeepgramSTTService(api_key=os.environ["DEEPGRAM_API_KEY"])
    llm = OpenAILLMService(
        api_key=os.environ["OPENAI_API_KEY"],
        settings=OpenAILLMService.Settings(
            system_instruction=(
                "You are a concise English-speaking learning assistant. "
                "Your responses are spoken aloud. Use short sentences, "
                "avoid markdown and lists, and ask at most one question at a time. "
                "Never claim to have taken an external action."
            ),
        ),
    )
    tts = CartesiaTTSService(
        api_key=os.environ["CARTESIA_API_KEY"],
        settings=CartesiaTTSService.Settings(
            # Demonstration voice from the official example; replace as needed.
            voice=os.getenv("CARTESIA_VOICE_ID", "86e30c1d-714b-4074-a1f2-1cb6b552fb49"),
        ),
    )

    context = LLMContext()
    user_aggr, assistant_aggr = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()),
    )
    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggr,
            llm,
            tts,
            transport.output(),
            assistant_aggr,
        ]
    )
    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(enable_metrics=True, enable_usage_metrics=True),
        idle_timeout_secs=args.pipeline_idle_timeout_secs,
    )
    runner = WorkerRunner(handle_sigint=args.handle_sigint)
    await runner.add_workers(worker)

    @transport.event_handler("on_client_connected")
    async def on_connected(_transport, _client):
        logger.info("Browser client connected")
        context.add_message({"role": "developer", "content": "Greet the user briefly."})
        await worker.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_disconnected(_transport, _client):
        logger.info("Browser client disconnected")
        await runner.cancel()

    await runner.run()


async def bot(runner_args: RunnerArguments) -> None:
    require_keys()
    transport = await create_transport(runner_args, TRANSPORT_PARAMS)
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
