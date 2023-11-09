import time


class TokenUsageTimer:
    start_timestamp: float | None = None
    first_token_timestamp: float | None = None
    end_timestamp: float | None = None

    def start(self) -> None:
        self.start_timestamp = time.perf_counter()

    def new_token(self) -> None:
        if self.first_token_timestamp is None:
            self.first_token_timestamp = time.perf_counter()

    def end(self) -> None:
        self.end_timestamp = time.perf_counter()

    @property
    def first_token_elapsed(self) -> float | None:
        if self.first_token_timestamp is None or self.start_timestamp is None:
            return None
        return self.first_token_timestamp - self.start_timestamp

    @property
    def completion_elapsed(self) -> float | None:
        if self.end_timestamp is None or self.start_timestamp is None:
            return None
        return self.end_timestamp - self.start_timestamp
