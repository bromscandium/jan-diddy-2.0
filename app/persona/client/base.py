import aiohttp

from app.core.http import HttpClient
from app.core.llm import llm_settings
from app.core.logger import logger


def _engine_headers() -> dict[str, str]:
    if llm_settings.PERSONA_ENGINE_SECRET:
        return {"X-Engine-Secret": llm_settings.PERSONA_ENGINE_SECRET}
    return {}


async def request(
    method: str,
    path: str,
    *,
    timeout: float,
    json: dict | None = None,
    key: str | None = None,
    retries: int = 1,
):
    url = f"{llm_settings.PERSONA_ENGINE_URL}{path}"
    for attempt in range(retries):
        try:
            if not HttpClient.session:
                logger.error("HttpClient session is not initialized")
                return None
            
            client_timeout = aiohttp.ClientTimeout(total=timeout)
            async with HttpClient.session.request(
                method, url, json=json, headers=_engine_headers(), timeout=client_timeout
            ) as resp:
                if resp.status == 502 and attempt < retries - 1:
                    continue
                resp.raise_for_status()
                if key is None:
                    return True
                data = await resp.json()
                return (data.get(key, "") or "").strip() or None
        except Exception as exc:
            logger.warning(f"{path} failed (attempt {attempt}): {exc}")
    return None
