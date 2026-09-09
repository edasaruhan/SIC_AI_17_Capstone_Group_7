import json
from decimal import Decimal

import httpx
import pytest
from app.integrations.providers import GoogleAdsAdapter, MetaAdsAdapter
from app.platform.errors import DomainError


def test_meta_adapter_keeps_token_out_of_url_and_normalizes() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer secret-token"
        assert "secret-token" not in str(request.url)
        assert "/v25.0/act_123/insights" in str(request.url)
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "campaign_id": "c1",
                        "campaign_name": "Grounded",
                        "date_start": "2026-09-01",
                        "impressions": "100",
                        "clicks": "4",
                        "spend": "12.50",
                        "actions": [{"action_type": "purchase", "value": "2"}],
                        "action_values": [{"action_type": "purchase", "value": "40"}],
                        "account_currency": "TRY",
                    }
                ],
                "paging": {"cursors": {"after": "next"}},
            },
        )

    adapter = MetaAdsAdapter(httpx.Client(transport=httpx.MockTransport(handler)))
    page = adapter.fetch("123", "secret-token", None)
    assert page.cursor == "next" and page.facts[0].spend == Decimal("12.50")
    assert page.facts[0].conversions == 2


def test_google_adapter_uses_required_headers_and_converts_micros() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer oauth-token"
        assert request.headers["developer-token"] == "developer-token"
        assert request.headers["login-customer-id"] == "999"
        assert b"LAST_30_DAYS" in request.content
        payload = [
            {
                "results": [
                    {
                        "segments": {"date": "2026-09-01"},
                        "campaign": {"id": "7", "name": "Search"},
                        "metrics": {
                            "impressions": "50",
                            "clicks": "5",
                            "costMicros": "1250000",
                            "conversions": 1.5,
                            "conversionsValue": 10,
                        },
                        "customer": {"currencyCode": "TRY"},
                    }
                ]
            }
        ]
        return httpx.Response(200, content=json.dumps(payload).encode())

    adapter = GoogleAdsAdapter(
        "developer-token", "999", httpx.Client(transport=httpx.MockTransport(handler))
    )
    page = adapter.fetch("123", "oauth-token", None)
    assert page.facts[0].spend == Decimal("1.25")
    assert page.facts[0].conversions == Decimal("1.5")


def test_provider_negative_metrics_fail_closed() -> None:
    with pytest.raises(DomainError, match="negative"):
        MetaAdsAdapter._normalize({"campaign_id": "1", "date_start": "2026-09-01", "spend": "-1"})
