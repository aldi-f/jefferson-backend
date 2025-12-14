import aiohttp

_session: aiohttp.ClientSession | None = None


def get_shared_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession()
    return _session


async def close_shared_session():
    global _session
    if _session and not _session.closed:
        await _session.close()
        _session = None
