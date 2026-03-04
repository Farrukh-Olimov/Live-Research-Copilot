import os

from statsd import StatsClient

_stats_d_client = None


def get_client() -> StatsClient:
    """Returns a StatsClient instance, creating one if not already initialized."""
    global _stats_d_client
    if _stats_d_client is None:
        _stats_d_client = StatsClient(
            host=os.getenv("STATSD_HOST", "localhost"),
            port=int(os.getenv("STATSD_PORT", 8125)),
        )
    return _stats_d_client
