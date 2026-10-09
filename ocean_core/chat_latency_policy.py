from __future__ import annotations

from typing import Optional


def clamp_specialized_tokens(
    requested_tokens: Optional[int],
    long_response: bool = False,
    elastic: bool = False,
) -> int:
    """Keep non-streaming specialized answers interactive by default."""
    if elastic:
        if isinstance(requested_tokens, int) and requested_tokens > 0:
            return max(256, int(requested_tokens))
        return -1

    if not isinstance(requested_tokens, int) or requested_tokens <= 0:
        return -1

    return max(256, int(requested_tokens))



def resolve_specialized_timeout_seconds(
    prompt_chars: int,
    long_response: bool = False,
    elastic: bool = False,
) -> Optional[float]:
    """Favor quick turnarounds for specialized non-streaming requests."""
    if elastic:
        return None

    prompt_size = max(0, int(prompt_chars or 0))
    base = 7.5 if prompt_size <= 300 else 9.0 if prompt_size <= 2000 else 11.0
    if long_response:
        base += 6.0

    size_bump = min(prompt_size / 2500.0, 4.0)
    ceiling = 30.0 if long_response else 12.0
    return min(base + size_bump, ceiling)
