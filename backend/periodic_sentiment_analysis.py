from typing import List
from transformers import pipeline, AutoTokenizer
import torch
import os


class SentimentAnalysis:
    def __init__(self, text: List[str]):
        self.text = text
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

        max_token_length = self.tokenizer.model_max_length
        results = []

        for text_item in self.text:
            # Split into chunks
            chunks = self.split_into_chunks(text_item, max_token_length)
            for chunk in chunks:
                sentiment_result = pipe(chunk)
                results.append({
                    'headline': chunk,
                    'label': sentiment_result[0]['label'],
                    'score': sentiment_result[0]['score']
                })

        return results

    def split_into_chunks(self, text, max_length=512):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        input_ids = inputs["input_ids"][0]

        # Create chunks
        chunks = []
        for i in range(0, len(input_ids), max_length):
            chunk_ids = input_ids[i: i + max_length]
            chunk_text = self.tokenizer.decode(chunk_ids, skip_special_tokens=True)
            chunks.append(chunk_text)

        return chunks

# Function to analyze ticker files
def analyze_ticker_files(tickers, news_directory):
    for ticker in tickers:
        file_path = f"{news_directory}/{ticker}_news.txt"
        
        if os.path.exists(file_path):
            print(f"\nSentiment analysis for {ticker}:\n{'=' * 40}")
            
            with open(file_path, 'r') as file:
                news_text = file.readlines()

            sentiment_analyzer = SentimentAnalysis(news_text)
            results = sentiment_analyzer.sentiment_analysis()

            # Print the results, filtering out entries without headlines
            for result in results:
                if result['headline'].strip():  # Check if the headline is not empty
                    label = result['label']
                    score = result['score']
                    
                    # Adjust thresholds for more interesting outputs
                    if label == 'neutral':
                        if score < 0.3:  # Lower threshold for negative sentiment
                            label = 'slightly negative'
                        elif score > 0.7:  # Higher threshold for positive sentiment
                            label = 'slightly positive'
                        else:
                            label = 'neutral'
                    
                    # Add custom logic to make labels more interesting
                    if 'strongly' in result['headline']:
                        label = 'strongly positive' if 'rise' in result['headline'] else 'strongly negative'
                    
                    print(f"Headline: {result['headline']}, Sentiment: {label}, Score: {score:.2f}")

# Example usage
if __name__ == "__main__":
    news_directory = "news"  # Ensure this matches your actual directory
    tickers = ['AMZN', 'GOOG', 'DRUG', 'AAPL']  # Replace with your actual tickers
    analyze_ticker_files(tickers, news_directory)
