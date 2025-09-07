import re

import nltk
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    print("Downloading nltk data...")
    nltk.download("punkt")
    nltk.download("punkt_tab")
    nltk.download("stopwords")
    nltk.download("averaged_perceptron_tagger")


class TitleGenerator:
    def __init__(self) -> None:
        self.stop_words = set(nltk.corpus.stopwords.words("english"))
        # Load spaCy model for NER (install with: python -m spacy download en-core-web-trf)
        self.nlp: spacy.Language | None = None
        try:
            self.nlp = spacy.load("en-core-web-trf")
        except OSError:
            print(
                "Warning: spaCy model not found. Install with: python -m spacy download en-core-web-trf"
            )
            self.nlp = None

    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess the text"""
        # Remove extra whitespace and normalize
        text = re.sub(r"\s+", " ", text.strip())
        # Remove URLs and email addresses
        text = re.sub(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            "",
            text,
        )
        text = re.sub(r"\S+@\S+", "", text)
        return text

    def extract_keywords_tfidf(self, text: str, max_features: int = 20) -> list[str]:
        """Extract keywords using TF-IDF"""

        # Custom tokenizer that preserves technical terms
        def technical_tokenizer(text: str) -> list[str]:
            # Keep alphanumeric, hyphens, underscores
            tokens = re.findall(r"[a-zA-Z0-9_-]+", text.lower())
            return [
                token
                for token in tokens
                if len(token) > 2 and token not in self.stop_words
            ]

        vectorizer = TfidfVectorizer(
            tokenizer=technical_tokenizer,
            max_features=max_features,
            ngram_range=(1, 3),  # Include bigrams and trigrams
            min_df=1,
            token_pattern=None,
        )

        try:
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]

            # Get top keywords with scores
            keyword_scores = list(zip(feature_names, scores, strict=False))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)

            return [kw for kw, score in keyword_scores if score > 0]
        except Exception:
            return []

    def extract_named_entities(self, text: str) -> list[str]:
        """Extract named entities using spaCy"""
        if not self.nlp:
            return []

        doc = self.nlp(text[:1000])  # Limit to first 1000 chars for efficiency
        entities = []

        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "TECHNOLOGY", "PERSON", "GPE"]:
                entities.append(ent.text)

        return list(set(entities))

    def extract_first_sentence_title(self, text: str) -> str:
        """Generate title from first meaningful sentence"""
        sentences = nltk.sent_tokenize(text)

        for sentence in sentences[:3]:  # Check first 3 sentences
            sentence = sentence.strip()
            if (
                len(sentence) < 20 or len(sentence) > 200
            ):  # Skip very short/long sentences
                continue

            # Remove common document starters
            sentence = re.sub(
                r"^(this|the)\s+(document|paper|article|report|study)\s+",
                "",
                sentence,
                flags=re.IGNORECASE,
            )

            # Extract main clause (before first comma or "that")
            main_clause = re.split(r",|\sthat\s|\swhich\s", sentence)[0]

            # Clean up
            main_clause = main_clause.strip().rstrip(".,;:")

            if 10 <= len(main_clause) <= 80:
                return main_clause

        return ""

    def generate_keyword_title(self, keywords: list[str], max_words: int = 8) -> str:
        """Generate title from top keywords"""
        if not keywords:
            return ""

        # Prioritize multi-word technical terms
        multi_word = [kw for kw in keywords if " " in kw or "_" in kw or "-" in kw]
        single_word = [
            kw for kw in keywords if " " not in kw and "_" not in kw and "-" not in kw
        ]

        # Build title with preference for technical terms
        title_parts = []
        word_count = 0

        # Add multi-word terms first
        for term in multi_word[:3]:
            if word_count + len(term.split()) <= max_words:
                title_parts.append(term)
                word_count += len(term.split())

        # Fill remaining space with single words
        for word in single_word:
            if word_count < max_words:
                title_parts.append(word)
                word_count += 1

        if title_parts:
            return " ".join(title_parts).title()

        return ""

    def score_sentences(self, text: str) -> list[tuple[str, int]]:
        """Score sentences for title potential"""
        sentences = nltk.sent_tokenize(text)
        keywords = self.extract_keywords_tfidf(text, max_features=30)
        keyword_set = {kw.lower() for kw in keywords[:15]}

        scored_sentences = []

        for i, sentence in enumerate(
            sentences[:10]
        ):  # Only consider first 10 sentences
            sentence_clean = sentence.strip()
            if len(sentence_clean) < 15 or len(sentence_clean) > 150:
                continue

            score = 0
            words = sentence_clean.lower().split()

            # Position bonus (earlier sentences score higher)
            score += max(0, 10 - i)

            # Keyword density bonus
            keyword_matches = sum(1 for word in words if word in keyword_set)
            score += keyword_matches * 2

            # Length penalty for very long sentences
            if len(sentence_clean) > 100:
                score -= 2

            # Bonus for technical patterns
            if re.search(
                r"\b(method|approach|system|framework|algorithm|model)\b",
                sentence_clean,
                re.IGNORECASE,
            ):
                score += 3

            scored_sentences.append((sentence_clean, score))

        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return scored_sentences

    def generate_title(self, text: str, method: str = "auto") -> str:
        """
        Generate title using specified method
        Methods: 'tfidf', 'first_sentence', 'scored_sentence', 'entities', 'auto'
        """
        text = self.preprocess_text(text)

        if method == "auto":
            # Try multiple methods and return the best one
            titles = {}

            # Method 1: TF-IDF keywords
            keywords = self.extract_keywords_tfidf(text)
            if keywords:
                titles["tfidf"] = self.generate_keyword_title(keywords)

            # Method 2: First sentence
            titles["first_sentence"] = self.extract_first_sentence_title(text)

            # Method 3: Best scored sentence
            scored_sentences = self.score_sentences(text)
            if scored_sentences:
                best_sentence = scored_sentences[0][0]
                # Compress the sentence
                compressed = re.split(r",|\sthat\s|\swhich\s", best_sentence)[0]
                compressed = compressed.strip().rstrip(".,;:")
                if 10 <= len(compressed) <= 80:
                    titles["scored_sentence"] = compressed

            # Method 4: Named entities + keywords
            entities = self.extract_named_entities(text)
            if entities and keywords:
                entity_title_parts = entities[:2] + keywords[:3]
                titles["entities"] = " ".join(entity_title_parts).title()

            # Select best title (prefer non-None, reasonable length)
            for method_name in [
                "scored_sentence",
                "first_sentence",
                "tfidf",
                "entities",
            ]:
                if method_name in titles and titles[method_name]:
                    title = str(titles[method_name])
                    if 10 <= len(title) <= 100:
                        return title

            # Fallback to any available title
            for t in titles.values():
                if t:
                    return str(t)

            return "untitled"

        else:
            # Use specific method
            if method == "tfidf":
                keywords = self.extract_keywords_tfidf(text)
                return self.generate_keyword_title(keywords)

            elif method == "first_sentence":
                return self.extract_first_sentence_title(text)

            elif method == "scored_sentence":
                scored_sentences = self.score_sentences(text)
                if scored_sentences:
                    return scored_sentences[0][0]
                return "untitled"

            elif method == "entities":
                entities = self.extract_named_entities(text)
                keywords = self.extract_keywords_tfidf(text)
                if entities or keywords:
                    title_parts = entities[:2] + keywords[:3]
                    return " ".join(title_parts).title()
                return "untitled"

        return "untitled"


# Example usage
def main() -> None:
    # Sample technical document text
    sample_text = """
    This paper presents a novel machine learning approach for automated code review
    using natural language processing techniques. The proposed system combines
    static analysis tools with deep learning models to identify potential bugs
    and security vulnerabilities in source code. We evaluate our method on a
    dataset of over 10,000 Python repositories from GitHub and demonstrate
    significant improvements over existing approaches. The system achieves
    92% accuracy in bug detection while reducing false positive rates by 35%.
    """

    generator = TitleGenerator()

    # Generate titles using different methods
    methods = ["auto", "tfidf", "first_sentence", "scored_sentence", "entities"]

    for method in methods:
        title = generator.generate_title(sample_text, method)
        print(f"{method.upper():15} -> {title}")


if __name__ == "__main__":
    main()
