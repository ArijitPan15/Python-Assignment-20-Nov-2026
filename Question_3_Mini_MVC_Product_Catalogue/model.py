import json
from pathlib import Path


class Product:
    def __init__(self, product_id: int, name: str, price: float):
        self.id = product_id
        self.name = name
        self.price = price

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "price": self.price}


class ProductRepository:
    def __init__(self, file_path=None):
        self.file_path = Path(file_path) if file_path else Path(__file__).with_name("products.json")

    def list_products(self) -> list[Product]:
        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                records = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"Unable to read product data: {error}") from error

        if not isinstance(records, list):
            raise ValueError("Product file must contain a list.")

        try:
            return [Product(item["id"], item["name"], item["price"]) for item in records]
        except (TypeError, KeyError) as error:
            raise ValueError("Product file contains an invalid product.") from error

    def save_products(self, products: list[Product]) -> None:
        try:
            with self.file_path.open("w", encoding="utf-8") as file:
                json.dump([item.to_dict() for item in products], file, indent=2)
        except OSError as error:
            raise ValueError(f"Unable to save product data: {error}") from error

    def add_product(self, name: str, price: float) -> Product:
        products = self.list_products()
        next_id = max((product.id for product in products), default=0) + 1
        new_product = Product(next_id, name, price)
        products.append(new_product)
        self.save_products(products)
        return new_product

    def find_product(self, product_id: int) -> Product | None:
        for product in self.list_products():
            if product.id == product_id:
                return product
        return None

    def delete_product(self, product_id: int) -> bool:
        products = self.list_products()
        remaining = [product for product in products if product.id != product_id]
        if len(remaining) == len(products):
            return False
        self.save_products(remaining)
        return True
