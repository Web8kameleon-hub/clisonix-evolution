from dataclasses import dataclass

from xlc_chat_gate import should_intercept_with_xlc


@dataclass
class Result:
    matched: bool
    route_name: str | None


class FakeRouter:
    def __init__(self, threshold=0.9999, max_extra_window=2):
        self.commands = []
        self.threshold = threshold
        self.max_extra_window = max_extra_window

    def register_many(self, commands):
        self.commands = list(commands)

    def route(self, prompt):
        normalized = prompt.strip().upper()
        matched = normalized in {item.upper() for item in self.commands}
        return Result(matched=matched, route_name=normalized if matched else None)


class BrokenRouter(FakeRouter):
    def route(self, prompt):
        raise RuntimeError("router unavailable")


def test_registered_command_is_intercepted():
    assert should_intercept_with_xlc(
        FakeRouter(),
        "START",
        commands=["START", "RESET", "MODE"],
        threshold=0.9999,
        max_extra_window=2,
    )


def test_normal_question_falls_through_to_model():
    assert not should_intercept_with_xlc(
        FakeRouter(),
        "Pse qielli është blu?",
        commands=["START", "RESET", "MODE"],
        threshold=0.9999,
        max_extra_window=2,
    )


def test_router_failure_falls_through_to_model():
    assert not should_intercept_with_xlc(
        BrokenRouter(),
        "Explain neural synthesis",
        commands=["START"],
        threshold=0.9999,
        max_extra_window=2,
    )
