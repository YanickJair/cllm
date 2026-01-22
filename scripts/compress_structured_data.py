import json

from clm_core import CLMEncoder, CLMConfig
from clm_core.types import SDCompressionConfig


def load_nbas() -> list[dict]:
    with open("./data/raw/nbas_dataset.json", "r") as f:
        nbas: list = json.load(f)
    return nbas


def nba_compression():
    nbas = load_nbas()

    config_blue = CLMConfig(
        ds_config=SDCompressionConfig(
            required_fields=["id", "title", "description", "category"], auto_detect=False
        )
    )

    compressor = CLMEncoder(cfg=config_blue)
    return compressor.encode(nbas)


def example_kb_article_encoding():
    """Example: Encode KB articles (another new domain)"""

    kb_catalog = [
        {
            "article_id": "KB-001",
            "title": "How to Reset Password",
            "content": "To reset your password, go to the login page and click...",
            "category": "Account",
            "tags": ["password", "security", "account"],
            "views": 1523,
            "last_updated": "2024-10-15",
        }
    ]
    config = CLMConfig(
        ds_config=SDCompressionConfig(
            dataset_name="ARTICLE",
            auto_detect=True,
            required_fields=["article_id", "title"],
            field_importance={"tags": 0.8, "content": 0.9},
            max_field_length=100,  # Longer for articles
        )
    )

    compressor = CLMEncoder(cfg=config)
    compressed = compressor.encode(kb_catalog)
    print("\n" + "=" * 70)
    print("KB ARTICLE ENCODING")
    print("=" * 70)
    print(f"\nCompressed output:\n{compressed}")
    return compressed


def example_product_encoding():
    """Example: Encode product catalog (new domain, same format!)"""

    product_catalog = [
        {
            "product_id": "PROD-001",
            "name": "Wireless Headphones",
            "description": "High-quality Bluetooth headphones with noise cancellation",
            "price": 199.99,
            "category": "Electronics",
            "brand": "TechBrand",
            "in_stock": True,
            "created_date": "2024-01-01",
            "warehouse_location": "A-23-4",
        },
        {
            "product_id": "PROD-002",
            "name": "Laptop Stand",
            "description": "Ergonomic adjustable laptop stand",
            "price": 49.99,
            "category": "Accessories",
            "brand": "ErgoTech",
            "in_stock": True,
            "created_date": "2024-01-05",
            "warehouse_location": "B-15-2",
        },
    ]
    config = CLMConfig(
        ds_config=SDCompressionConfig(
            dataset_name="PRODUCT",
            auto_detect=True,
            required_fields=["product_id", "name", "price"],
            excluded_fields=["warehouse_location", "created_date"],
            default_fields_importance={"id": 1.0, "name": 0.8}
        )
    )
    compressor = CLMEncoder(cfg=config)
    compressed = compressor.encode(product_catalog)
    print("\n" + "=" * 70)
    print("PRODUCT CATALOG ENCODING")
    print("=" * 70)
    print(f"\nCompressed output:\n{compressed}")
    return compressed


if __name__ == "__main__":
    nba_compress = nba_compression()
    kb_compress = example_kb_article_encoding()
    p_compress = example_product_encoding()
