import random
import asyncio
from abc import ABC, abstractmethod
from typing import Optional
from httpx import AsyncClient, HTTPError
from app.core.config import get_settings

settings = get_settings()


class BaseIntegrationService(ABC):
    def __init__(self):
        self.mock_seed = settings.MOCK_DATA_SEED
        random.seed(self.mock_seed)
        self._client: Optional[AsyncClient] = None

    @property
    @abstractmethod
    def base_url(self) -> str: ...

    @abstractmethod
    def _get_headers(self) -> dict[str, str]: ...

    async def _get_client(self) -> AsyncClient:
        if self._client is None:
            self._client = AsyncClient(timeout=30.0)
        return self._client

    async def _simulate_delay(self):
        delay = random.uniform(
            settings.SIMULATED_API_DELAY_MIN,
            settings.SIMULATED_API_DELAY_MAX,
        )
        await asyncio.sleep(delay)

    async def _request(self, method: str, path: str, **kwargs) -> dict | list:
        client = await self._get_client()
        url = f"{self.base_url}{path}"
        headers = self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        response = await client.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
