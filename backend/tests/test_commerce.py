from concurrent.futures import ThreadPoolExecutor

import pytest
from conftest import auth_headers
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def setup_sale(client: TestClient, tenant: dict, stock: int = 3) -> tuple[str, str]:
    headers = auth_headers(tenant)
    customer = client.post("/api/v1/customers", headers=headers, json={"name": "Synthetic buyer"})
    assert customer.status_code == 201, customer.text
    product = client.post(
        "/api/v1/products",
        headers=headers,
        json={"name": "Synthetic product", "sku": "SKU-TEST", "unit_price": "12.50"},
    )
    assert product.status_code == 201, product.text
    product_id = product.json()["id"]
    adjusted = client.post(
        f"/api/v1/products/{product_id}/stock",
        headers=headers,
        json={"quantity_delta": stock, "reason": "Synthetic stock", "idempotency_key": "initial"},
    )
    assert adjusted.status_code == 200, adjusted.text
    return customer.json()["id"], product_id


def test_sale_return_and_idempotency(client: TestClient, tenants: dict) -> None:
    headers = auth_headers(tenants["a"])
    customer, product = setup_sale(client, tenants["a"])
    cart = {
        "customer_id": customer,
        "items": [{"product_id": product, "quantity": 2, "unit_discount": "0.50"}],
        "idempotency_key": "sale-1",
    }
    order = client.post("/api/v1/orders", headers=headers, json=cart)
    assert order.status_code == 201, order.text
    data = order.json()
    assert data["total"] == "24.00"
    repeated = client.post("/api/v1/orders", headers=headers, json=cart)
    assert repeated.status_code == 201 and repeated.json()["id"] == data["id"]
    stock = client.get("/api/v1/products", headers=headers).json()[0]["stock_on_hand"]
    assert stock == 1
    returned = {
        "order_item_id": data["items"][0]["id"],
        "quantity": 1,
        "restock": True,
        "reason": "Synthetic return",
        "idempotency_key": "return-1",
    }
    path = f"/api/v1/orders/{data['id']}/refunds"
    first_refund = client.post(path, headers=headers, json=returned)
    assert first_refund.status_code == 201, first_refund.text
    assert first_refund.json()["amount"] == "12.00"
    assert (
        client.post(path, headers=headers, json=returned).json()["id"] == first_refund.json()["id"]
    )
    updated = client.get(f"/api/v1/orders/{data['id']}", headers=headers).json()
    assert updated["status"] == "partially_refunded"
    assert updated["refunded_total"] == "12.00"
    assert client.get("/api/v1/products", headers=headers).json()[0]["stock_on_hand"] == 2
    too_many = {**returned, "quantity": 2, "idempotency_key": "return-overflow"}
    assert client.post(path, headers=headers, json=too_many).status_code == 409
    final_return = {**returned, "idempotency_key": "return-2"}
    assert client.post(path, headers=headers, json=final_return).status_code == 201
    assert (
        client.get(f"/api/v1/orders/{data['id']}", headers=headers).json()["status"] == "refunded"
    )


def test_failed_order_and_payment_are_atomic(client: TestClient, tenants: dict) -> None:
    headers = auth_headers(tenants["a"])
    customer, product = setup_sale(client, tenants["a"], stock=1)
    cart = {
        "customer_id": customer,
        "items": [{"product_id": product, "quantity": 2}],
        "idempotency_key": "failed",
    }
    assert client.post("/api/v1/orders", headers=headers, json=cart).status_code == 409
    assert client.get("/api/v1/orders", headers=headers).json() == []
    assert client.get("/api/v1/products", headers=headers).json()[0]["stock_on_hand"] == 1
    cart["items"][0]["quantity"] = 1
    created = client.post("/api/v1/orders", headers=headers, json=cart)
    assert created.status_code == 201, created.text
    path = f"/api/v1/orders/{created.json()['id']}/payments"
    pay = {"amount": "12.50", "method": "cash", "idempotency_key": "payment-1"}
    one = client.post(path, headers=headers, json=pay)
    two = client.post(path, headers=headers, json=pay)
    assert one.status_code == two.status_code == 201
    assert one.json()["id"] == two.json()["id"]
    assert (
        client.post(path, headers=headers, json={**pay, "idempotency_key": "overpay"}).status_code
        == 409
    )


def test_concurrent_sales_cannot_oversell(client: TestClient, tenants: dict) -> None:
    headers = auth_headers(tenants["a"])
    customer, product = setup_sale(client, tenants["a"], stock=1)

    def sell(key: str) -> int:
        response = client.post(
            "/api/v1/orders",
            headers=headers,
            json={
                "customer_id": customer,
                "items": [{"product_id": product, "quantity": 1}],
                "idempotency_key": key,
            },
        )
        return response.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = list(executor.map(sell, ["concurrent-a", "concurrent-b"]))
    assert sorted(statuses) == [201, 409]
    assert client.get("/api/v1/products", headers=headers).json()[0]["stock_on_hand"] == 0
    assert len(client.get("/api/v1/orders", headers=headers).json()) == 1


def test_foreign_product_and_idempotency_collision(client: TestClient, tenants: dict) -> None:
    headers = auth_headers(tenants["a"])
    customer, product = setup_sale(client, tenants["a"])
    _, foreign_product = setup_sale(client, tenants["b"])
    cart = {
        "customer_id": customer,
        "items": [{"product_id": foreign_product, "quantity": 1}],
        "idempotency_key": "foreign",
    }
    assert client.post("/api/v1/orders", headers=headers, json=cart).status_code == 404
    cart["items"][0]["product_id"] = product
    assert client.post("/api/v1/orders", headers=headers, json=cart).status_code == 201
    cart["items"][0]["quantity"] = 2
    assert client.post("/api/v1/orders", headers=headers, json=cart).status_code == 409
