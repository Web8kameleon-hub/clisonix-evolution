"""Pure routing gate for Ocean chat.

XLC may intercept registered control commands, but an unmatched natural-language
prompt must always fall through to the language-model chat path.
"""

from __future__ import annotations

from typing import Any, Iterable


def should_intercept_with_xlc(
    router: Any,
    prompt: str,
    *,
    commands: Iterable[str],
    threshold: float,
    max_extra_window: int,
) -> bool:
    command_list = [str(item).strip() for item in commands if str(item).strip()]
    if router is None or not prompt.strip() or not command_list:
        return False

    probe = router
    router_type = type(router)
    try:
        probe = router_type(
            threshold=threshold,
            max_extra_window=max_extra_window,
        )
        probe.register_many(command_list)
    except Exception:
        # Some router implementations are not reconstructable. Use the active
        # router for a read-only match probe rather than failing normal chat.
        probe = router

    try:
        result = probe.route(prompt)
    except Exception:
        return False

    return bool(
        getattr(result, "matched", False)
        and getattr(result, "route_name", None)
    )
