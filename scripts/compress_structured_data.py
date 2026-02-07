import json
import time

from clm_core import CLMEncoder, CLMConfig
from clm_core.types import SDCompressionConfig


def load_sample_catalog() -> list[dict]:
    """Load a sample catalog dataset."""
    with open("./data/raw/nbas_dataset.json", "r") as f:
        catalog: list = json.load(f)
    return catalog


def catalog_compression():
    """Example: Compress a catalog with script/content fields."""
    catalog = load_sample_catalog()
    data = {
      "context": {
        "task": "Our favorite hikes together",
        "location": "Boulder",
        "season": "spring_2025"
      },
      "friends": [
        "ana",
        "luis",
        "sam"
      ],
      "hikes": [
        {
          "id": 1,
          "name": "Blue Lake Trail",
          "distanceKm": 7.5,
          "elevationGain": 320,
          "companion": "ana",
          "wasSunny": True
        },
        {
          "id": 2,
          "name": "Ridge Overlook",
          "distanceKm": 9.2,
          "elevationGain": 540,
          "companion": "luis",
          "wasSunny": False
        },
        {
          "id": 3,
          "name": "Wildflower Loop",
          "distanceKm": 5.1,
          "elevationGain": 180,
          "companion": "sam",
          "wasSunny": True
        }
      ]
    }

    start_time = time.perf_counter()
    config = CLMConfig(
        ds_config=SDCompressionConfig(
            max_truncation_mapping={
                "task": 10
            }
        )
    )

    compressor = CLMEncoder(cfg=config)
    elapsed_seconds = time.perf_counter() - start_time
    print(f"Elapsed creating config: {elapsed_seconds:.6f} s")

    start_time = time.perf_counter()
    c = compressor.encode(data)
    elapsed_seconds = time.perf_counter() - start_time

    print(f"Elapsed compressing data: {elapsed_seconds:.6f} s")
    return c

def example_kb_article_encoding():
    """Example: Encode KB articles."""

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
            auto_detect=True,
            required_fields=["article_id", "title"],
            field_importance={"tags": 0.8, "content": 0.9},
            max_truncation_mapping=100,
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
    """Example: Encode product catalog."""

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
    result = catalog_compression()
    print(f"Compressed: {result.compressed}")
    print(f"Tokens (Out/In): {result.c_tokens}/{result.n_tokens}")
    print(f"Compression ratio: {result.compression_ratio}%")
