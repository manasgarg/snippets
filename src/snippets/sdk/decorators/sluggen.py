import re
import unicodedata


class SlugGenerator:
    def __init__(self, max_length: int = 50, word_separator: str = "-") -> None:
        """
        Initialize slug generator

        Args:
            max_length: Maximum length of generated slug
            word_separator: Character to separate words (usually '-' or '_')
        """
        self.max_length = max_length
        self.word_separator = word_separator

        # Common stop words to remove from slugs (optional)
        self.stop_words = {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "has",
            "he",
            "in",
            "is",
            "it",
            "its",
            "of",
            "on",
            "that",
            "the",
            "to",
            "was",
            "will",
            "with",
        }

    def remove_accents(self, text: str) -> str:
        """Remove accents and diacritical marks from text"""
        # Normalize unicode characters
        text = unicodedata.normalize("NFKD", text)
        # Remove combining characters (accents)
        text = "".join(c for c in text if not unicodedata.combining(c))
        return text

    def clean_text(self, text: str) -> str:
        """Clean and normalize text for slug generation"""
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove accents
        text = self.remove_accents(text)

        # Replace common symbols and punctuation with spaces
        text = re.sub(r"[&+@#%]", " and ", text)  # Replace special chars with 'and'
        text = re.sub(r'[.,;:!?()[\]{}"\']', " ", text)  # Remove punctuation
        text = re.sub(r"[/\\|]", " ", text)  # Replace slashes with spaces

        # Handle numbers and technical terms
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)  # camelCase to words
        text = re.sub(r"([0-9]+)", r" \1 ", text)  # Separate numbers

        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def filter_words(
        self, words: list[str], remove_stop_words: bool = False
    ) -> list[str]:
        """Filter words based on various criteria"""
        filtered_words = []

        for word in words:
            # Skip empty words
            if not word or len(word) < 1:
                continue

            # Skip single characters (except numbers)
            if len(word) == 1 and not word.isdigit():
                continue

            # Skip stop words if requested
            if remove_stop_words and word.lower() in self.stop_words:
                continue

            # Keep technical terms, numbers, and meaningful words
            if word.isalnum() or "-" in word or "_" in word:
                filtered_words.append(word)

        return filtered_words

    def truncate_slug(self, slug: str) -> str:
        """Truncate slug to max_length, ensuring it ends at word boundary"""
        if len(slug) <= self.max_length:
            return slug

        # Find last word separator before max_length
        truncated = slug[: self.max_length]
        last_separator = truncated.rfind(self.word_separator)

        if last_separator > 0:
            return truncated[:last_separator]
        else:
            # If no separator found, just truncate
            return truncated

    def generate_slug(
        self,
        title: str,
        remove_stop_words: bool = True,
        custom_replacements: dict[str, str] | None = None,
    ) -> str:
        """
        Generate URL-friendly slug from title

        Args:
            title: Input title text
            remove_stop_words: Whether to remove common stop words
            custom_replacements: Dict of custom text replacements

        Returns:
            URL-friendly slug string
        """
        if not title or not title.strip():
            return "untitled"

        # Apply custom replacements first
        text = title
        if custom_replacements:
            for old, new in custom_replacements.items():
                text = text.replace(old, new)

        # Clean the text
        cleaned = self.clean_text(text)

        # Split into words
        words = cleaned.split()

        # Filter words
        filtered_words = self.filter_words(words, remove_stop_words)

        # Handle empty result
        if not filtered_words:
            return "untitled"

        # Join words with separator
        slug = self.word_separator.join(filtered_words)

        # Remove any remaining invalid characters
        slug = re.sub(r"[^a-zA-Z0-9\-_]", "", slug)

        # Clean up multiple separators
        separator_pattern = f"[{re.escape(self.word_separator)}]+"
        slug = re.sub(separator_pattern, self.word_separator, slug)

        # Remove leading/trailing separators
        slug = slug.strip(self.word_separator)

        # Truncate if necessary
        slug = self.truncate_slug(slug)

        # Final cleanup
        slug = slug.strip(self.word_separator)

        return slug if slug else "untitled"

    def generate_unique_slug(
        self, title: str, existing_slugs: set[str], max_attempts: int = 100
    ) -> str:
        """
        Generate unique slug that doesn't exist in existing_slugs set

        Args:
            title: Input title
            existing_slugs: Set of already used slugs
            max_attempts: Maximum attempts to find unique slug

        Returns:
            Unique slug string
        """
        base_slug = self.generate_slug(title)

        if base_slug not in existing_slugs:
            return base_slug

        # Try adding numbers
        for i in range(2, max_attempts + 2):
            candidate = f"{base_slug}{self.word_separator}{i}"
            if candidate not in existing_slugs:
                return candidate

        # Fallback: add timestamp-like suffix
        import time

        timestamp_suffix = str(int(time.time()))[-6:]  # Last 6 digits
        return f"{base_slug}{self.word_separator}{timestamp_suffix}"


def create_slug_variants() -> None:
    """Demonstrate different slug generation approaches"""

    generator = SlugGenerator()

    test_titles = [
        "Machine Learning Approach for Automated Code Review",
        "Deep Learning Models & Neural Networks: A Comprehensive Guide",
        "API Design Patterns in RESTful Services (2024)",
        "Kubernetes Configuration Management with Helm Charts",
        "The Ultimate Guide to React.js Performance Optimization",
        "Microservices Architecture: Benefits, Challenges & Best Practices",
        "Data Science with Python: NumPy, Pandas & Matplotlib Tutorial",
    ]

    print("=== SLUG GENERATION EXAMPLES ===\n")

    for title in test_titles:
        print(f"Title: {title}")

        # Standard slug
        standard = generator.generate_slug(title)
        print(f"Standard:      {standard}")

        # With stop words
        with_stops = generator.generate_slug(title, remove_stop_words=False)
        print(f"With stops:    {with_stops}")

        # Shorter version
        short_gen = SlugGenerator(max_length=30)
        short = short_gen.generate_slug(title)
        print(f"Short (30):    {short}")

        # With underscores
        underscore_gen = SlugGenerator(word_separator="_")
        underscore = underscore_gen.generate_slug(title)
        print(f"Underscores:   {underscore}")

        print("-" * 80)


def main() -> None:
    """Example usage and testing"""

    # Basic usage
    generator = SlugGenerator()

    # Test cases
    test_cases = [
        "Hello World!",
        "Machine Learning & Deep Learning",
        "React.js Component Lifecycle",
        "API Design Patterns (RESTful)",
        "Café Münü - Special Characters",
        "This is a very long title that should be truncated to fit within the maximum length limit",
        "",
        "123 Numbers & Symbols #@$%",
    ]

    print("=== BASIC SLUG GENERATION ===\n")

    for title in test_cases:
        slug = generator.generate_slug(title)
        print(f"'{title}' -> '{slug}'")

    print("\n" + "=" * 60 + "\n")

    # Demonstrate unique slug generation
    existing_slugs = {"machine-learning", "machine-learning-2", "machine-learning-3"}

    unique_slug = generator.generate_unique_slug(
        "Machine Learning Tutorial", existing_slugs
    )

    print(f"Unique slug: {unique_slug}")
    print(f"Existing slugs: {existing_slugs}")

    print("\n" + "=" * 60 + "\n")

    # Show different variants
    create_slug_variants()


if __name__ == "__main__":
    main()
