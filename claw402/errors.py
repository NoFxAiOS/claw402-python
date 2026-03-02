class Claw402Error(Exception):
    """Raised when the claw402 API returns a non-2xx response."""

    def __init__(self, status: int, body: str):
        self.status = status
        self.body = body
        super().__init__(f"Claw402 API error {status}: {body}")
