from controller import ProductController
from model import ProductRepository


def main() -> None:
    controller = ProductController(ProductRepository())

    print("PRODUCT CATALOGUE")

    while True:
        print("\n1. List products")
        print("2. Add product")
        print("3. Find product")
        print("4. Delete product")
        print("5. Exit")

        try:
            choice = input("Enter your choice: ").strip()
            if choice == "5":
                print("Goodbye!")
                break
            print(controller.handle_command(choice))
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
