"""Cliente base para la API de Sportmonks Football."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

import httpx


class SportmonksClient:
    """Cliente HTTP base para Sportmonks, sin métodos de dominio todavía."""

    BASE_URL = "https://api.sportmonks.com/v3/football"

    def __init__(self, *, timeout: float = 30.0) -> None:
        """Inicializa el cliente usando SPORTMONKS_API_TOKEN."""
        token = os.getenv("SPORTMONKS_API_TOKEN")
        if not token:
            raise ValueError(
                "La variable de entorno SPORTMONKS_API_TOKEN es obligatoria."
            )

        self._token = token
        self._http_client = httpx.Client(base_url=self.BASE_URL, timeout=timeout)

    def _get(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Realiza una solicitud GET autenticada y devuelve su JSON."""
        request_params = dict(params or {})
        request_params["api_token"] = self._token

        response = self._http_client.get(path, params=request_params)
        response.raise_for_status()
        return response.json()

    def get_league(self, league_id: int) -> dict[str, Any]:
        """Devuelve los datos de una liga por su ID."""
        response = self._get(f"/leagues/{league_id}")
        return response["data"]

    def close(self) -> None:
        """Cierra la conexión HTTP del cliente."""
        self._http_client.close()

    def __enter__(self) -> SportmonksClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
