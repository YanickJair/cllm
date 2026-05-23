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
    data = [
      {
        "id": "2539",
        "listing_url": "https://www.airbnb.com/rooms/2539",
        "name": "Cozy Capitol Hill Studio",
        "description": "Modern studio apartment with water view...",
        "neighborhood": "Capitol Hill",
        "latitude": 47.6205,
        "longitude": -122.3212,
        "property_type": "Apartment",
        "room_type": "Entire home/apt",
        "accommodates": 2,
        "bathrooms": 1.0,
        "bedrooms": 1,
        "beds": 1,
        "price": "$135.00",
        "minimum_nights": 2,
        "maximum_nights": 365,
        "number_of_reviews": 47,
        "review_scores_rating": 92,
        "review_scores_accuracy": 9,
        "review_scores_cleanliness": 9,
        "review_scores_checkin": 10,
        "review_scores_communication": 10,
        "review_scores_location": 9,
        "review_scores_value": 9,
        "host_name": "Sarah",
        "host_response_time": "within an hour",
        "availability_365": 180
      },
      {
        "id": "2540",
        "listing_url": "https://www.airbnb.com/rooms/2540",
        "name": "Cozy Capitol Hill Studio",
        "description": "Modern studio apartment with water view...",
        "neighborhood": "Capitol Hill",
        "latitude": 47.6205,
        "longitude": -122.3212,
        "property_type": "Apartment",
        "room_type": "Entire home/apt",
        "accommodates": 2,
        "bathrooms": 1.0,
        "bedrooms": 1,
        "beds": 1,
        "price": "$135.00",
        "minimum_nights": 2,
        "maximum_nights": 365,
        "number_of_reviews": 47,
        "review_scores_rating": 92,
        "review_scores_accuracy": 9,
        "review_scores_cleanliness": 9,
        "review_scores_checkin": 10,
        "review_scores_communication": 10,
        "review_scores_location": 9,
        "review_scores_value": 9,
        "host_name": "Sarah",
        "host_response_time": "within an hour",
        "availability_365": 180
      },
      {
        "id": "2541",
        "listing_url": "https://www.airbnb.com/rooms/2541",
        "name": "Cozy Capitol Hill Studio",
        "description": "Modern studio apartment with water view...",
        "neighborhood": "Capitol Hill",
        "latitude": 47.6205,
        "longitude": -122.3212,
        "property_type": "Apartment",
        "room_type": "Entire home/apt",
        "accommodates": 2,
        "bathrooms": 1.0,
        "bedrooms": 1,
        "beds": 1,
        "price": "$135.00",
        "minimum_nights": 2,
        "maximum_nights": 365,
        "number_of_reviews": 47,
        "review_scores_rating": 92,
        "review_scores_accuracy": 9,
        "review_scores_cleanliness": 9,
        "review_scores_checkin": 10,
        "review_scores_communication": 10,
        "review_scores_location": 9,
        "review_scores_value": 9,
        "host_name": "Sarah",
        "host_response_time": "within an hour",
        "availability_365": 180
      },
      {
        "id": "2541",
        "listing_url": "https://www.airbnb.com/rooms/2541",
        "name": "Cozy Capitol Hill Studio",
        "description": "Modern studio apartment with water view...",
        "neighborhood": "Capitol Hill",
        "latitude": 47.6205,
        "longitude": -122.3212,
        "property_type": "Apartment",
        "room_type": "Entire home/apt",
        "accommodates": 2,
        "bathrooms": 1.0,
        "bedrooms": 1,
        "beds": 1,
        "price": "$135.00",
        "minimum_nights": 2,
        "maximum_nights": 365,
        "number_of_reviews": 47,
        "review_scores_rating": 92,
        "review_scores_accuracy": 9,
        "review_scores_cleanliness": 9,
        "review_scores_checkin": 10,
        "review_scores_communication": 10,
        "review_scores_location": 9,
        "review_scores_value": 9,
        "host_name": "Sarah",
        "host_response_time": "within an hour",
        "availability_365": 180
      },
      {
        "id": "2541",
        "listing_url": "https://www.airbnb.com/rooms/2541",
        "name": "Cozy Capitol Hill Studio",
        "description": "Modern studio apartment with water view...",
        "neighborhood": "Capitol Hill",
        "latitude": 47.6205,
        "longitude": -122.3212,
        "property_type": "Apartment",
        "room_type": "Entire home/apt",
        "accommodates": 2,
        "bathrooms": 1.0,
        "bedrooms": 1,
        "beds": 1,
        "price": "$135.00",
        "minimum_nights": 2,
        "maximum_nights": 365,
        "number_of_reviews": 47,
        "review_scores_rating": 92,
        "review_scores_accuracy": 9,
        "review_scores_cleanliness": 9,
        "review_scores_checkin": 10,
        "review_scores_communication": 10,
        "review_scores_location": 9,
        "review_scores_value": 9,
        "host_name": "Sarah",
        "host_response_time": "within an hour",
        "availability_365": 180
    },
    {
        "id": "2542",
        "listing_url": "https://www.airbnb.com/rooms/2542",
        "name": "Cozy Capitol Hill Studio",
        "description": "Modern studio apartment with water view...",
        "neighborhood": "Capitol Hill",
        "latitude": 47.6205,
        "longitude": -122.3212,
        "property_type": "Apartment",
        "room_type": "Entire home/apt",
        "accommodates": 2,
        "bathrooms": 1.0,
        "bedrooms": 1,
        "beds": 1,
        "price": "$135.00",
        "minimum_nights": 2,
        "maximum_nights": 365,
        "number_of_reviews": 47,
        "review_scores_rating": 92,
        "review_scores_accuracy": 9,
        "review_scores_cleanliness": 9,
        "review_scores_checkin": 10,
        "review_scores_communication": 10,
        "review_scores_location": 9,
        "review_scores_value": 9,
        "host_name": "Sarah",
        "host_response_time": "within an hour",
        "availability_365": 180
    },
    {
      "id": "2539",
      "listing_url": "https://www.airbnb.com/rooms/2539",
      "name": "Cozy Capitol Hill Studio",
      "description": "Modern studio apartment with water view...",
      "neighborhood": "Capitol Hill",
      "latitude": 47.6205,
      "longitude": -122.3212,
      "property_type": "Apartment",
      "room_type": "Entire home/apt",
      "accommodates": 2,
      "bathrooms": 1.0,
      "bedrooms": 1,
      "beds": 1,
      "price": "$135.00",
      "minimum_nights": 2,
      "maximum_nights": 365,
      "number_of_reviews": 47,
      "review_scores_rating": 92,
      "review_scores_accuracy": 9,
      "review_scores_cleanliness": 9,
      "review_scores_checkin": 10,
      "review_scores_communication": 10,
      "review_scores_location": 9,
      "review_scores_value": 9,
      "host_name": "Sarah",
      "host_response_time": "within an hour",
      "availability_365": 180
    },
    {
      "id": "2540",
      "listing_url": "https://www.airbnb.com/rooms/2540",
      "name": "Cozy Capitol Hill Studio",
      "description": "Modern studio apartment with water view...",
      "neighborhood": "Capitol Hill",
      "latitude": 47.6205,
      "longitude": -122.3212,
      "property_type": "Apartment",
      "room_type": "Entire home/apt",
      "accommodates": 2,
      "bathrooms": 1.0,
      "bedrooms": 1,
      "beds": 1,
      "price": "$135.00",
      "minimum_nights": 2,
      "maximum_nights": 365,
      "number_of_reviews": 47,
      "review_scores_rating": 92,
      "review_scores_accuracy": 9,
      "review_scores_cleanliness": 9,
      "review_scores_checkin": 10,
      "review_scores_communication": 10,
      "review_scores_location": 9,
      "review_scores_value": 9,
      "host_name": "Sarah",
      "host_response_time": "within an hour",
      "availability_365": 180
    },
    {
      "id": "2541",
      "listing_url": "https://www.airbnb.com/rooms/2541",
      "name": "Cozy Capitol Hill Studio",
      "description": "Modern studio apartment with water view...",
      "neighborhood": "Capitol Hill",
      "latitude": 47.6205,
      "longitude": -122.3212,
      "property_type": "Apartment",
      "room_type": "Entire home/apt",
      "accommodates": 2,
      "bathrooms": 1.0,
      "bedrooms": 1,
      "beds": 1,
      "price": "$135.00",
      "minimum_nights": 2,
      "maximum_nights": 365,
      "number_of_reviews": 47,
      "review_scores_rating": 92,
      "review_scores_accuracy": 9,
      "review_scores_cleanliness": 9,
      "review_scores_checkin": 10,
      "review_scores_communication": 10,
      "review_scores_location": 9,
      "review_scores_value": 9,
      "host_name": "Sarah",
      "host_response_time": "within an hour",
      "availability_365": 180
    },
    {
      "id": "2541",
      "listing_url": "https://www.airbnb.com/rooms/2541",
      "name": "Cozy Capitol Hill Studio",
      "description": "Modern studio apartment with water view...",
      "neighborhood": "Capitol Hill",
      "latitude": 47.6205,
      "longitude": -122.3212,
      "property_type": "Apartment",
      "room_type": "Entire home/apt",
      "accommodates": 2,
      "bathrooms": 1.0,
      "bedrooms": 1,
      "beds": 1,
      "price": "$135.00",
      "minimum_nights": 2,
      "maximum_nights": 365,
      "number_of_reviews": 47,
      "review_scores_rating": 92,
      "review_scores_accuracy": 9,
      "review_scores_cleanliness": 9,
      "review_scores_checkin": 10,
      "review_scores_communication": 10,
      "review_scores_location": 9,
      "review_scores_value": 9,
      "host_name": "Sarah",
      "host_response_time": "within an hour",
      "availability_365": 180
    },
    {
      "id": "2541",
      "listing_url": "https://www.airbnb.com/rooms/2541",
      "name": "Cozy Capitol Hill Studio",
      "description": "Modern studio apartment with water view...",
      "neighborhood": "Capitol Hill",
      "latitude": 47.6205,
      "longitude": -122.3212,
      "property_type": "Apartment",
      "room_type": "Entire home/apt",
      "accommodates": 2,
      "bathrooms": 1.0,
      "bedrooms": 1,
      "beds": 1,
      "price": "$135.00",
      "minimum_nights": 2,
      "maximum_nights": 365,
      "number_of_reviews": 47,
      "review_scores_rating": 92,
      "review_scores_accuracy": 9,
      "review_scores_cleanliness": 9,
      "review_scores_checkin": 10,
      "review_scores_communication": 10,
      "review_scores_location": 9,
      "review_scores_value": 9,
      "host_name": "Sarah",
      "host_response_time": "within an hour",
      "availability_365": 180
  },
  {
      "id": "2542",
      "listing_url": "https://www.airbnb.com/rooms/2542",
      "name": "Cozy Capitol Hill Studio",
      "description": "Modern studio apartment with water view...",
      "neighborhood": "Capitol Hill",
      "latitude": 47.6205,
      "longitude": -122.3212,
      "property_type": "Apartment",
      "room_type": "Entire home/apt",
      "accommodates": 2,
      "bathrooms": 1.0,
      "bedrooms": 1,
      "beds": 1,
      "price": "$135.00",
      "minimum_nights": 2,
      "maximum_nights": 365,
      "number_of_reviews": 47,
      "review_scores_rating": 92,
      "review_scores_accuracy": 9,
      "review_scores_cleanliness": 9,
      "review_scores_checkin": 10,
      "review_scores_communication": 10,
      "review_scores_location": 9,
      "review_scores_value": 9,
      "host_name": "Sarah",
      "host_response_time": "within an hour",
      "availability_365": 180
  },
    ]

    print(len(data))

    start_time = time.perf_counter()
    config = CLMConfig(
        ds_config=SDCompressionConfig(
            dataset_name="AirbnB Listing",
            required_fields=[
                "id",
                "name",
                "neighborhood",
                "property_type",
                "price",
                "bedrooms",
                "number_of_reviews",
                "review_scores_rating",
                "latitude",
                "longitude"
            ],
            max_truncation_mapping={"description": 200},
            drop_non_required_fields=True
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
