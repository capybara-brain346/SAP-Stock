# Use a pipeline as a high-level helper
from typing import List

# Load model directly
from transformers import pipeline


class SentimentAnalysis:
    def __init__(self, text: str | List):
        self.text = text

    def sentiment_analysis(self):
        pipe = pipeline(
            "text-classification",
            model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis",
        )

        return pipe(self.text)


if __name__ == "__main__":
    s = SentimentAnalysis(["This stock is awesome!", "Good Morning"])
    print(s.sentiment_analysis())
