def show_products(products) -> str:
    if not products:
        return "No products available."

    lines = [f"{'ID':<5}{'Name':<22}{'Price':>10}", "-" * 37]
    for product in products:
        lines.append(f"{product.id:<5}{product.name:<22}{product.price:>10.2f}")
    return "\n".join(lines)


def show_product(product) -> str:
    return f"ID: {product.id} | Name: {product.name} | Price: {product.price:.2f}"


def show_message(message: str) -> str:
    return message
