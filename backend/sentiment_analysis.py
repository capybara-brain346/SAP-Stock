# Use a pipeline as a high-level helper
from typing import List

# Load model directly
from transformers import pipeline, AutoTokenizer
import torch


class SentimentAnalysis:
    def __init__(self, text: list):
        self.text = text
        # Load the tokenizer corresponding to the model
        self.tokenizer = AutoTokenizer.from_pretrained(
            "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
        )

    def sentiment_analysis(self):
        device = 0 if torch.cuda.is_available() else -1
        pipe = pipeline(
            "text-classification",
            model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis",
            device=device,
        )

        max_token_length = (
            self.tokenizer.model_max_length
        )  # Get the model's max token length (512)
        results = []

        for text_item in self.text:
            # Split into chunks and ensure no chunk exceeds 512 tokens
            chunks = self.split_into_chunks(text_item, max_token_length)
            for chunk in chunks:
                results.extend(pipe(chunk))

        return results

    def split_into_chunks(self, text, max_length=512):
        """
        Splits a long text into smaller chunks that fit within the model's token limit (512 tokens).
        """
        # Tokenize the input without truncating yet
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        input_ids = inputs["input_ids"][0]

        # Create chunks of tokens of max_length size
        chunks = []
        for i in range(0, len(input_ids), max_length):
            chunk_ids = input_ids[i : i + max_length]
            # Truncate any chunk that exceeds the maximum token length
            chunk_text = self.tokenizer.decode(chunk_ids, skip_special_tokens=True)
            chunks.append(chunk_text)

        return chunks


if __name__ == "__main__":
    s = SentimentAnalysis(["This stock is awesome!", "Good Morning"])
    print(s.sentiment_analysis())
