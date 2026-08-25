"""Client tipato per viaggigoated backend — single source, versionato."""

from __future__ import annotations

from typing import Any

import httpx


class ApiError(RuntimeError):
    def __init__(self, status: int, data: Any) -> None:
        self.status = status
        self.data = data
        msg = data.get("user_message") if isinstance(data, dict) else str(data)  # type: ignore
        super().__init__(f"HTTP {status}: {msg or data}")
        self.code: str = data.get("code", "UNKNOWN") if isinstance(data, dict) else "UNKNOWN"  # type: ignore
        self.retryable: bool = bool(data.get("retryable")) if isinstance(data, dict) else False  # type: ignore

class ViaggigoatedClient:
    def __init__(self, base_url: str, token: str | None = None, timeout: float = 45.0) -> None:
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

    # health
    def health(self) -> Any:
        return self._request("GET", "/health")

    # auth
    def auth_login(self, email: str, password: str) -> Any:
        return self._request("POST", "/auth/token", json_body={"email": email, "password": password})

    def auth_register(self, email: str, password: str, invite_code: str) -> Any:
        return self._request("POST", "/auth/register", json_body={"email": email, "password": password, "invite_code": invite_code})

    # trails — generale, aggregato, link fonte
    def trails_search(self, *, lat: float, lon: float, radius_m: int = 10000, limit: int = 12) -> Any:
        return self._request("GET", "/trails/search", params={"lat": lat, "lon": lon, "radius_m": radius_m, "limit": limit})

    def trails_gpx(self, provider: str, trail_id: str) -> str:
        return self._request("GET", f"/trails/{provider}/{trail_id}/gpx")  # type: ignore[return-value]

    # weather — Open-Meteo + Met Norway aggregato
    def weather_forecast(self, *, lat: float, lon: float, start_date: str, end_date: str) -> Any:
        return self._request("GET", "/weather/forecast", params={"lat": lat, "lon": lon, "start_date": start_date, "end_date": end_date})

    # iris
    def iris_departures(self, station: str, date: str | None = None) -> Any:
        p: dict[str, Any] = {"station": station}
        if date:
            p["date"] = date
        return self._request("GET", "/iris/departures", params=p)

    # itinerary — generale
    def itinerary_plan(self, body: dict[str, Any]) -> Any:
        return self._request("POST", "/itinerary/plan", json_body=body)

    def itinerary_places(self, city: str, tags: str | None = None, radius_m: int = 8000) -> Any:
        p: dict[str, Any] = {"city": city, "radius_m": radius_m}
        if tags:
            p["tags"] = tags
        return self._request("GET", "/itinerary/places", params=p)

    # car / fuel — generali
    def car_estimate(self, body: dict[str, Any]) -> Any:
        return self._request("POST", "/estimate/car", json_body=body)

    def fuel_stations(self, *, lat: float, lon: float, radius_km: float = 10, fuel: str = "gpl") -> Any:
        return self._request("GET", "/fuel/stations", params={"lat": lat, "lon": lon, "radius_km": radius_km, "fuel": fuel})

    # trips — generali
    def trips_openjaw(self, *, from_home: str, area: str, window: str, nights: int, travelers: int = 4) -> Any:
        return self._request("GET", "/trips/openjaw", params={"from_home": from_home, "area": area, "window": window, "nights": nights, "travelers": travelers})

    def trips_loop(self, body: dict[str, Any]) -> Any:
        return self._request("POST", "/trips/loop", json_body=body)

    # destinations — generale voli
    def destinations_list(self, *, from_iata: str, window: str, nights: int, travelers: int = 1) -> Any:
        return self._request("GET", "/destinations", params={"from": from_iata, "window": window, "nights": nights, "travelers": travelers})

    # local-hop — generale
    def local_hop(self, *, from_city: str, to_city: str, mode: str = "train") -> Any:
        return self._request("GET", "/local-hop", params={"from": from_city, "to": to_city, "mode": mode})

    # airports — generale
    def airports_nearby(self, *, from_city: str, radius_km: float = 250) -> Any:
        return self._request("GET", "/airports/nearby", params={"from": from_city, "radius_km": radius_km})

    # diagnostics — generale
    def diagnostics_metrics(self) -> Any:
        return self._request("GET", "/diagnostics/metrics")

    # alerts
    def alerts_list(self) -> Any:
        return self._request("GET", "/alerts")

    def alerts_create(self, body: dict[str, Any]) -> Any:
        return self._request("POST", "/alerts", json_body=body)

    def alerts_delete(self, alert_id: str) -> Any:
        return self._request("DELETE", f"/alerts/{alert_id}")

    # saved trips
    def saved_list(self) -> Any:
        return self._request("GET", "/trips/saved")

    def saved_get(self, trip_id: str) -> Any:
        return self._request("GET", f"/trips/saved/{trip_id}")

    def saved_prompt(self, trip_id: str) -> Any:
        return self._request("GET", f"/trips/saved/{trip_id}/prompt")

    # admin
    def admin_links(self, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", "/admin/links", params=params)

    # omio / bus / trains / hafas / flights — generali
    def omio_positions(self, q: str, limit: int = 8) -> Any:
        return self._request("GET", "/omio/positions", params={"q": q, "limit": limit})

    def omio_search(self, params: dict[str, Any]) -> Any:
        return self._request("GET", "/omio/search", params=params)

    def bus_cities(self, q: str) -> Any:
        return self._request("GET", "/bus/cities", params={"q": q})

    def bus_search(self, params: dict[str, Any]) -> Any:
        return self._request("GET", "/bus/search", params=params)

    def trains_stations(self, q: str, limit: int = 20) -> Any:
        return self._request("GET", "/trains/stations", params={"q": q, "limit": limit})

    def trains_search(self, params: dict[str, Any]) -> Any:
        return self._request("GET", "/trains/search", params=params)

    def hafas_positions(self, q: str) -> Any:
        return self._request("GET", "/hafas/positions", params={"q": q})

    def hafas_search(self, params: dict[str, Any]) -> Any:
        return self._request("GET", "/hafas/search", params=params)

    def flights_roundtrip(self, params: dict[str, Any]) -> Any:
        return self._request("GET", "/flights/roundtrip", params=params)

    def flights_aggregated(self, params: dict[str, Any]) -> Any:
        return self._request("GET", "/flights/aggregated", params=params)

    # search — generali con link fonte (Omio/Hafas + anywhere)
    def anywhere(self, params: dict[str, Any]) -> Any:
        return self._request("GET", "/anywhere", params=params)

    def roundtrip_stream(self, params: dict[str, Any]) -> Any:
        return self._request("GET", "/roundtrip/stream", params=params)
