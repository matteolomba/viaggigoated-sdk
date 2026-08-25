"""Client tipato per viaggigoated backend — single source, versionato."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict


class ApiError(RuntimeError):
    def __init__(self, status: int, data: Any) -> None:
        self.status = status
        self.data = data
        msg = data.get("user_message") if isinstance(data, dict) else str(data)
        super().__init__(f"HTTP {status}: {msg or data}")
        self.code: str = data.get("code", "UNKNOWN") if isinstance(data, dict) else "UNKNOWN"
        self.retryable: bool = bool(data.get("retryable")) if isinstance(data, dict) else False


class ViaggigoatedClient:
    def __init__(self, base_url: str, token: str | None = None, timeout: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        h: dict[str, str] = {"Accept": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _request(self, method: str, path: str, params: dict[str, Any] | None = None, json_body: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=self.timeout, headers=self._headers(), follow_redirects=True) as c:
            r = c.request(method, url, params=params, json=json_body)
            if "gpx" in r.headers.get("content-type", "") or path.endswith("/gpx"):
                if r.status_code >= 400:
                    raise ApiError(r.status_code, r.text)
                return r.text
            try:
                data = r.json()
            except ValueError:
                data = r.text
            if r.status_code >= 400:
                raise ApiError(r.status_code, data)
            return data

    # Generali — non per provider, ogni risultato linka la fonte
    def health(self) -> Any:
        return self._request("GET", "/health")

    def trails_search(self, *, lat: float, lon: float, radius_m: int = 10000, limit: int = 12) -> Any:
        return self._request("GET", "/trails/search", params={"lat": lat, "lon": lon, "radius_m": radius_m, "limit": limit})

    def trails_gpx(self, provider: str, trail_id: str) -> str:
        return self._request("GET", f"/trails/{provider}/{trail_id}/gpx")  # type: ignore[return-value]

    def weather_forecast(self, *, lat: float, lon: float, start_date: str, end_date: str) -> Any:
        return self._request("GET", "/weather/forecast", params={"lat": lat, "lon": lon, "start_date": start_date, "end_date": end_date})

    def iris_departures(self, station: str) -> Any:
        return self._request("GET", "/iris/departures", params={"station": station})

    def itinerary_plan(self, body: dict[str, Any]) -> Any:
        return self._request("POST", "/itinerary/plan", json_body=body)

    def car_estimate(self, body: dict[str, Any]) -> Any:
        return self._request("POST", "/estimate/car", json_body=body)

    def fuel_stations(self, *, lat: float, lon: float, radius_km: float = 10, fuel: str = "gpl") -> Any:
        return self._request("GET", "/fuel/stations", params={"lat": lat, "lon": lon, "radius_km": radius_km, "fuel": fuel})

    def trips_openjaw(self, *, from_home: str, area: str, window: str, nights: int, travelers: int = 4) -> Any:
        return self._request("GET", "/trips/openjaw", params={"from_home": from_home, "area": area, "window": window, "nights": nights, "travelers": travelers})

    def trips_loop(self, body: dict[str, Any]) -> Any:
        return self._request("POST", "/trips/loop", json_body=body)
