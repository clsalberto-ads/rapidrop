"""RLS SQL statements for PostgreSQL.

Execute these manually as a superuser to enable RLS on tenant tables:

    psql -d rapidrop -f src/core/rls_setup.sql
"""

RLS_STATEMENTS = {
    "merchants": """
        ALTER TABLE merchants ENABLE ROW LEVEL SECURITY;
        CREATE POLICY merchants_tenant_isolation ON merchants
            USING (id::text = current_setting('app.current_merchant_id'));
    """,
    "products": """
        ALTER TABLE products ENABLE ROW LEVEL SECURITY;
        CREATE POLICY products_tenant_isolation ON products
            USING (merchant_id::text = current_setting('app.current_merchant_id'));
    """,
}

TENANT_TABLES = [
    "products",
    "product_categories",
    "product_variations",
    "riders",
    "rider_payment_configs",
    "rider_payment_periods",
    "orders",
    "order_items",
    "orders_rider",
    "invoices",
    "invoice_transactions",
    "payment_transactions",
    "customer_addresses",
    "customer_payment_methods",
    "merchant_onboardings",
    "onboarding_events",
    "audit_logs",
]
