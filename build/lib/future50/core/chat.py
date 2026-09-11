"""A minimal chat and response object for the FUTURE-50 core."""

from dataclasses import dataclass
from typing import Optional

from .model_router import LocalModel


@dataclass
class ChatMessage:
    role: str
    text: str


class Future50Chat:
    """Simple model-independent chat layer that can be replaced later."""

    def __init__(self):
        self.history: list[ChatMessage] = []

    def generate(self, role: str, text: str, model: Optional[LocalModel] = None) -> ChatMessage:
        if model is not None:
            output = model.infer(text)
        else:
            output = text
        # Keep the answer as a clean assistant reply object, and never echo
        # the prompt back into the model message stream as a route artifact.
        message = ChatMessage(role="assistant", text=output)
        self.history.append(message)
        return message
