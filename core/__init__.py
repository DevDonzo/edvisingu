"""EdVisingU core — shared offline-first building blocks.

Everything in this package defaults to a zero-cost mock mode so the entire
system runs locally with no API keys. Set ARCH_BACKEND=live (and provide the
relevant keys) to use real cloud providers.
"""

__all__ = ["llm", "store"]
