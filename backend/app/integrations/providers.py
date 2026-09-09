"""Pinned provider adapters that expose canonical facts and never domain objects."""

import os
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Protocol

import httpx

from app.platform.errors import DomainError


@dataclass(frozen=True)
class ProviderFact:
    metric_date: date
    external_campaign_id: str
    campaign_name: str
    impressions: int
    clicks: int
    spend: Decimal
    conversions: Decimal | None
    conversion_value: Decimal | None
    currency: str | None


@dataclass(frozen=True)
class ProviderPage:
    facts: tuple[ProviderFact, ...]
    cursor: str | None
    raw_payload: bytes


class AdsProvider(Protocol):
    api_version: str

    def fetch(self, account_id: str, access_token: str, cursor: str | None) -> ProviderPage: ...


def resolve_secret(reference: str) -> str:
    prefix = "env:GP_PROVIDER_"
    if not reference.startswith(prefix):
        raise DomainError("Unsupported provider secret reference")
    name = reference.removeprefix("env:")
    value = os.environ.get(name)
    if not value:
        raise DomainError("Provider credential is unavailable", 409)
    return value


def _decimal(value: object, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise DomainError(f"Provider returned invalid {field}", 502) from error
    if result < 0:
        raise DomainError(f"Provider returned negative {field}", 502)
    return result


def _integer(value: object, field: str) -> int:
    result = int(_decimal(value, field))
    if Decimal(result) != _decimal(value, field):
        raise DomainError(f"Provider returned non-integral {field}", 502)
    return result


class MetaAdsAdapter:
    api_version = "v25.0"
    base_url = "https://graph.facebook.com"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(timeout=20, follow_redirects=False)

    def fetch(self, account_id: str, access_token: str, cursor: str | None) -> ProviderPage:
        parameters = {
            "fields": (
                "campaign_id,campaign_name,date_start,impressions,clicks,spend,"
                "actions,action_values,account_currency"
            ),
            "level": "campaign",
            "time_increment": "1",
            "limit": "500",
        }
        if cursor:
            parameters["after"] = cursor
        response = self.client.get(
            f"{self.base_url}/{self.api_version}/act_{account_id}/insights",
            params=parameters,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        facts = tuple(self._normalize(row) for row in payload.get("data", []))
        next_cursor = payload.get("paging", {}).get("cursors", {}).get("after")
        return ProviderPage(facts, next_cursor, response.content)

    @staticmethod
    def _normalize(row: dict[str, Any]) -> ProviderFact:
        actions = {item.get("action_type"): item.get("value") for item in row.get("actions", [])}
        values = {
            item.get("action_type"): item.get("value") for item in row.get("action_values", [])
        }
        conversion = actions.get("purchase")
        conversion_value = values.get("purchase")
        return ProviderFact(
            metric_date=date.fromisoformat(str(row["date_start"])),
            external_campaign_id=str(row["campaign_id"]),
            campaign_name=str(row.get("campaign_name", "Unnamed provider campaign"))[:300],
            impressions=_integer(row.get("impressions", 0), "impressions"),
            clicks=_integer(row.get("clicks", 0), "clicks"),
            spend=_decimal(row.get("spend", 0), "spend"),
            conversions=_decimal(conversion, "conversions") if conversion is not None else None,
            conversion_value=_decimal(conversion_value, "conversion value")
            if conversion_value is not None
            else None,
            currency=str(row["account_currency"])[:3] if row.get("account_currency") else None,
        )


class GoogleAdsAdapter:
    api_version = "v25"
    base_url = "https://googleads.googleapis.com"

    def __init__(
        self,
        developer_token: str,
        login_customer_id: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.developer_token = developer_token
        self.login_customer_id = login_customer_id
        self.client = client or httpx.Client(timeout=20, follow_redirects=False)

    def fetch(self, account_id: str, access_token: str, cursor: str | None) -> ProviderPage:
        if cursor:
            raise DomainError("Google searchStream does not accept a cursor", 409)
        query = (
            "SELECT segments.date, campaign.id, campaign.name, metrics.impressions, "
            "metrics.clicks, metrics.cost_micros, metrics.conversions, "
            "metrics.conversions_value, customer.currency_code FROM campaign "
            "WHERE segments.date DURING LAST_30_DAYS"
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "developer-token": self.developer_token,
        }
        if self.login_customer_id:
            headers["login-customer-id"] = self.login_customer_id
        response = self.client.post(
            f"{self.base_url}/{self.api_version}/customers/{account_id}/googleAds:searchStream",
            json={"query": query},
            headers=headers,
        )
        response.raise_for_status()
        payload: list[dict[str, Any]] = response.json()
        rows = [row for batch in payload for row in batch.get("results", [])]
        return ProviderPage(tuple(self._normalize(row) for row in rows), None, response.content)

    @staticmethod
    def _normalize(row: dict[str, Any]) -> ProviderFact:
        metric = row.get("metrics", {})
        campaign = row.get("campaign", {})
        customer = row.get("customer", {})
        return ProviderFact(
            metric_date=date.fromisoformat(str(row["segments"]["date"])),
            external_campaign_id=str(campaign["id"]),
            campaign_name=str(campaign.get("name", "Unnamed provider campaign"))[:300],
            impressions=_integer(metric.get("impressions", 0), "impressions"),
            clicks=_integer(metric.get("clicks", 0), "clicks"),
            spend=_decimal(metric.get("costMicros", 0), "cost") / Decimal(1_000_000),
            conversions=_decimal(metric["conversions"], "conversions")
            if "conversions" in metric
            else None,
            conversion_value=_decimal(metric["conversionsValue"], "conversion value")
            if "conversionsValue" in metric
            else None,
            currency=str(customer["currencyCode"])[:3] if customer.get("currencyCode") else None,
        )


def provider_for(name: str) -> AdsProvider:
    if name == "meta_ads":
        return MetaAdsAdapter()
    if name == "google_ads":
        developer_token = os.environ.get("GP_PROVIDER_GOOGLE_DEVELOPER_TOKEN")
        if not developer_token:
            raise DomainError("Google Ads developer token is unavailable", 409)
        return GoogleAdsAdapter(
            developer_token,
            os.environ.get("GP_PROVIDER_GOOGLE_LOGIN_CUSTOMER_ID"),
        )
    raise DomainError("Unsupported advertising provider")
