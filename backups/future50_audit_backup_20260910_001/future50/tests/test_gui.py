from future50.core.chat import ChatMessage
from future50.core.model_router import LocalModel, ModelRole
from future50.interface.gui import Future50DesktopGUI


class FakeChatLog:
    def __init__(self):
        self.lines = []
        self.state = "normal"

    def configure(self, state=None):
        if state:
            self.state = state

    def insert(self, index, text):
        self.lines.append(text)

    def see(self, index):
        return None


class FakeInputBox:
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value

    def delete(self, *args):
        return None


class FakeStatus:
    def __init__(self):
        self.text = ""

    def configure(self, text):
        self.text = text


def test_gui_can_create_instance_without_launching():
    gui = Future50DesktopGUI()
    assert gui is not None
    assert gui.router is not None


def test_gui_on_send_logs_user_prompt_and_model_reply(monkeypatch):
    gui = Future50DesktopGUI()
    gui.chat_log = FakeChatLog()
    gui.input_box = FakeInputBox("debug python bug")
    gui.status = FakeStatus()

    def fake_route(task):
        return LocalModel("future50-coding", ModelRole.CODING)

    def fake_generate(role, text, model=None):
        return ChatMessage(role="assistant", text="Python issue fixed locally.")

    monkeypatch.setattr(gui.router, "route", fake_route)
    monkeypatch.setattr(gui.chat, "generate", fake_generate)

    gui.on_send()

    assert any("user:" in line for line in gui.chat_log.lines)
    assert any("assistant" in line.lower() for line in gui.chat_log.lines)
