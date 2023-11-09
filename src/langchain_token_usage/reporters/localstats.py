"""This module contains a reporter that counts the total token usage in the local memory."""

from . import TokenUsageReport
from . import TokenUsageReporter


class LocalStatsReporter(TokenUsageReporter):
    """A reporter implementation that counts the token usage in the local memory.

    Example usage:

        from langchain.chains import LLMChain

        reporter = LocalStatsReporter()
        handler = OpenAITokenUsageCallbackHandler(reporter)

        llm = AnyLLM(..., callbacks=[handler])
        prompt = ...
        chain = LLMChain(llm=llm, prompt=prompt)
        chain.run(...)

        assert reporter.total_tokens > 0
    """

    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    successful_requests: int = 0
    total_cost: float = 0.0

    def send_report(self, report: TokenUsageReport) -> None:
        """Adds the token usage statistics of a single LLM run to the local counters.

        Args:
            report (TokenUsageReport): The report of the token usage.
        """
        self.successful_requests += 1
        self.prompt_tokens += report.prompt_tokens or 0
        self.completion_tokens += report.completion_tokens or 0
        self.total_tokens += report.total_tokens or 0
        self.total_cost += report.total_cost or 0.0
