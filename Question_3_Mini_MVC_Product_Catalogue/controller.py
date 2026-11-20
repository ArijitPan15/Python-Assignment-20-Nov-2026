from datetime import datetime
from functools import wraps
import math

from model import ProductRepository
from view import show_message, show_product, show_products


def log_request(function):
    """Print each command before it reaches the controller."""
    @wraps(function)
    def wrapper(self, command: str):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[LOG] {now} {command}")
        return function(self, command)
    return wrapper


class ProductController:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    @log_request
    def handle_command(self, command: str) -> str:
        try:
            if command == "1":
                return show_products(self.repository.list_products())

            if command == "2":
                name = input("Product name: ").strip()
                if not name:
                    return show_message("Product name cannot be empty.")

                price_text = input("Price: ").strip()
                try:
                    price = float(price_text)
                except ValueError:
                    return show_message("Please enter a valid price.")

                if not math.isfinite(price) or price <= 0:
                    return show_message("Price must be a positive number.")

                product = self.repository.add_product(name, price)
                return show_message(f"Product added with ID {product.id}.")

            if command in ("3", "4"):
                id_text = input("Product ID: ").strip()
                if not id_text.isdigit() or int(id_text) == 0:
                    return show_message("Please enter a valid product ID.")

                product_id = int(id_text)
                if command == "3":
                    product = self.repository.find_product(product_id)
                    if product is None:
                        return show_message("Product not found.")
                    return show_product(product)

                if self.repository.delete_product(product_id):
                    return show_message("Product deleted.")
                return show_message("Product not found.")

            return show_message("Invalid choice. Choose 1 to 5.")
        except ValueError as error:
            return show_message(f"Error: {error}")
