"""Main module for the Python project."""


def hello_world() -> str:
    """Return a greeting message.

    Returns:
        str: A greeting message.
    """
    return "Hello, World!"


def main() -> None:
    """Main function to run the application."""
    print(hello_world())


if __name__ == "__main__":
    main()
