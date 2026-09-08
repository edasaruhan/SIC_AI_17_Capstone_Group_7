CREATE TABLE product_categories (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), name varchar(120) NOT NULL,
 UNIQUE(tenant_id,id), UNIQUE(tenant_id,name)
);
CREATE TABLE products (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), name varchar(200) NOT NULL, sku varchar(100) NOT NULL,
 category_id uuid, unit_price numeric(14,2) NOT NULL, currency varchar(3) NOT NULL,
 stock_on_hand integer NOT NULL DEFAULT 0, active boolean NOT NULL DEFAULT true,
 UNIQUE(tenant_id,id), UNIQUE(tenant_id,sku), CHECK (stock_on_hand>=0), CHECK(unit_price>=0),
 FOREIGN KEY(tenant_id,category_id) REFERENCES product_categories(tenant_id,id)
);
CREATE TABLE inventory_movements (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), product_id uuid NOT NULL,
 quantity_delta integer NOT NULL, reason varchar(200) NOT NULL, idempotency_key varchar(200) NOT NULL,
 reference_id uuid, UNIQUE(tenant_id,idempotency_key), CHECK(quantity_delta<>0),
 FOREIGN KEY(tenant_id,product_id) REFERENCES products(tenant_id,id)
);
CREATE TABLE orders (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), customer_id uuid NOT NULL, placed_at timestamptz NOT NULL,
 currency varchar(3) NOT NULL, total numeric(14,2) NOT NULL, refunded_total numeric(14,2) NOT NULL DEFAULT 0,
 status varchar(24) NOT NULL DEFAULT 'placed', idempotency_key varchar(150) NOT NULL,
 request_hash varchar(64) NOT NULL, UNIQUE(tenant_id,id), UNIQUE(tenant_id,idempotency_key),
 CHECK(total>=0), CHECK(refunded_total BETWEEN 0 AND total),
 CHECK(status IN ('placed','partially_refunded','refunded')),
 FOREIGN KEY(tenant_id,customer_id) REFERENCES customers(tenant_id,id)
);
CREATE INDEX ix_orders_customer_time ON orders(tenant_id,customer_id,placed_at DESC);
CREATE TABLE order_items (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), order_id uuid NOT NULL, product_id uuid NOT NULL,
 product_name varchar(200) NOT NULL, quantity integer NOT NULL, returned_quantity integer NOT NULL DEFAULT 0,
 unit_price numeric(14,2) NOT NULL, unit_discount numeric(14,2) NOT NULL, line_total numeric(14,2) NOT NULL,
 UNIQUE(tenant_id,id), UNIQUE(tenant_id,order_id,product_id),
 CHECK(quantity>0), CHECK(returned_quantity BETWEEN 0 AND quantity),
 CHECK(unit_price>=0), CHECK(unit_discount BETWEEN 0 AND unit_price),
 CHECK(line_total=(unit_price-unit_discount)*quantity),
 FOREIGN KEY(tenant_id,order_id) REFERENCES orders(tenant_id,id),
 FOREIGN KEY(tenant_id,product_id) REFERENCES products(tenant_id,id)
);
CREATE TABLE refunds (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), order_id uuid NOT NULL, order_item_id uuid NOT NULL,
 quantity integer NOT NULL, amount numeric(14,2) NOT NULL, restock boolean NOT NULL,
 reason varchar(200) NOT NULL, idempotency_key varchar(150) NOT NULL,
 UNIQUE(tenant_id,idempotency_key), CHECK(quantity>0), CHECK(amount>=0),
 FOREIGN KEY(tenant_id,order_id) REFERENCES orders(tenant_id,id),
 FOREIGN KEY(tenant_id,order_item_id) REFERENCES order_items(tenant_id,id)
);
CREATE TABLE payments (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), order_id uuid NOT NULL, amount numeric(14,2) NOT NULL,
 method varchar(24) NOT NULL, idempotency_key varchar(150) NOT NULL,
 UNIQUE(tenant_id,idempotency_key), CHECK(amount>0), CHECK(method IN ('cash','bank_transfer','external_card')),
 FOREIGN KEY(tenant_id,order_id) REFERENCES orders(tenant_id,id)
);
DO $$ DECLARE t text; BEGIN
 FOREACH t IN ARRAY ARRAY['product_categories','products','inventory_movements','orders','order_items','refunds','payments'] LOOP
  EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
  EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', t);
  EXECUTE format('CREATE POLICY tenant_scope ON %I USING (tenant_id=current_tenant_id()) WITH CHECK (tenant_id=current_tenant_id())', t);
  EXECUTE format('GRANT SELECT, INSERT ON %I TO growthpilot_app', t);
 END LOOP;
END $$;
GRANT UPDATE ON products,product_categories,orders,order_items TO growthpilot_app;
