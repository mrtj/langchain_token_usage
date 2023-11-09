"""OpenAI token usage callback handler for LangChain."""

import datetime
import os
import time
import uuid
from typing import Any
from typing import Dict
from typing import List

import openai
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.openai_info import get_openai_token_cost_for_model
from langchain.callbacks.openai_info import standardize_model_name
from langchain.schema.output import ChatGenerationChunk
from langchain.schema.output import GenerationChunk
from langchain.schema.output import LLMResult

from ..reporters import TokenUsageReport
from ..reporters import TokenUsageReporter


def _get_caller_id(val: str | None) -> str | None:
    return val[-4:] if val is not None and len(val) >= 4 else None


class OpenAITokenUsageCallbackHandler(BaseCallbackHandler):
    """Collects metrics about the token usage of OpenAI LLM runs."""

    reporter: TokenUsageReporter
    _first_token_timing: Dict[uuid.UUID, List[float]]
    _completion_timing: Dict[uuid.UUID, float]
    _caller_id: str | None = None

    def __init__(self, reporter: TokenUsageReporter) -> None:
        """Collects metrics about the token usage of OpenAI LLM runs.

        Args:
            reporter (TokenUsageReporter): The reporter that will be used to send the metrics
                to the metrics repository.
        """
        self.reporter = reporter
        self._first_token_timing = {}
        self._completion_timing = {}

        self._caller_id = _get_caller_id(openai.api_key)
        if self._caller_id is None:
            self._caller_id = _get_caller_id(os.environ.get("OPENAI_API_KEY"))

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: uuid.UUID,
        parent_run_id: uuid.UUID | None = None,
        tags: List[str] | None = None,
        metadata: Dict[str, Any] | None = None,
        **kwargs: Any
    ) -> None:
        """Called when the LLM starts processing the request."""
        start = time.perf_counter()
        self._first_token_timing[run_id] = [start]
        self._completion_timing[run_id] = start

    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: GenerationChunk | ChatGenerationChunk | None = None,
        run_id: uuid.UUID,
        parent_run_id: uuid.UUID | None = None,
        **kwargs: Any
    ) -> Any:
        """Called when the LLM emits a new token."""
        stop = time.perf_counter()
        if run_id in self._first_token_timing and len(self._first_token_timing[run_id]) < 2:
            self._first_token_timing[run_id].append(stop)

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: uuid.UUID,
        parent_run_id: uuid.UUID | None = None,
        **kwargs: Any
    ) -> None:
        """Called when the LLM finishes processing the request."""
        stop = time.perf_counter()
        timestamp = datetime.datetime.now()

        # get stats
        if response.llm_output is None:
            return None
        if "token_usage" not in response.llm_output:
            return None
        token_usage = response.llm_output["token_usage"]
        completion_tokens = token_usage.get("completion_tokens")
        prompt_tokens = token_usage.get("prompt_tokens")
        model_name = standardize_model_name(response.llm_output.get("model_name", ""))
        total_cost: float | None = None
        try:
            completion_cost = (
                get_openai_token_cost_for_model(model_name, completion_tokens, is_completion=True)
                if completion_tokens is not None
                else 0.0
            )
            prompt_cost = (
                get_openai_token_cost_for_model(model_name, prompt_tokens)
                if prompt_tokens is not None
                else 0.0
            )
            total_cost = prompt_cost + completion_cost
        except ValueError:
            pass
        total_tokens: int | None = token_usage.get("total_tokens")

        # timing
        first_token_time: float | None = None
        completion_time: float | None = None
        if run_id in self._first_token_timing:
            ftt_data = self._first_token_timing[run_id]
            if len(ftt_data) == 2:
                first_token_time = ftt_data[1] - ftt_data[0]
            del self._first_token_timing[run_id]
        if run_id in self._completion_timing:
            completion_time = stop - self._completion_timing[run_id]
            del self._completion_timing[run_id]

        self.reporter.send_report(
            TokenUsageReport(
                timestamp=timestamp,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                total_cost=total_cost,
                first_token_time=first_token_time,
                completion_time=completion_time,
                model_name=model_name,
                caller_id=self._caller_id,
            )
        )
