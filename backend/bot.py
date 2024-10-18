import os
import logging
from typing import List, Tuple
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def query_rag(stock_symbol: str, question: str) -> Tuple[str, List[str]] | str:
    PROMPT_TEMPLATE = """
    You are an assistant providing sentiment analysis and stock market news summaries.

    Stock Symbol:
    {stock_symbol}
    
    Related News:
    {context}

    Please answer the question based on the stock-related news context.

    Question:

    {question}
    """
    try:
        # Load the news data for the specific stock from .txt files
        # Assuming news data is already stored in the "news/" directory
        news_files = [f'backend/news/{stock_symbol}.txt']
        news_context = ""
        
        # Load and concatenate all the news text data for the stock
        for file in news_files:
            with open(file, 'r', encoding='utf-8') as f:
                news_context += f.read() + " "
        
        # Initialize embeddings and database using Chroma and Google Embeddings
        db = Chroma(
            persist_directory="chroma_stock",
            embedding_function=GoogleGenerativeAIEmbeddings(
                model="models/embedding-001"
            ),
        )

        # Store all the news text into Chroma
        # Assuming each line in the text file represents a separate news item
        db.add_texts([news_context])

        # Perform similarity search using the embeddings
        results = db.similarity_search_with_score(
            stock_symbol, k=len(db.get()["ids"])
        )

        # Extract the relevant context
        context_text = " ".join([doc.page_content for doc, _score in results])

        # Format the prompt with the news context
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(
            stock_symbol=stock_symbol, context=context_text, question=question
        )

        # Use Google Generative AI model for final question answering
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", api_key=os.getenv("GOOGLE_API_KEY")
        )
        response = model.invoke(prompt)
        if hasattr(response, "content"):
            return response.content.strip()
        return str(response).strip()

    except Exception as e:
        logging.error(f"Error in query_rag: {e}")
        return "An error occurred while processing the query."


def main() -> None:
    # Stock symbol to analyze
    stock_symbol = "AAPL"  # Example stock symbol

    # Question related to sentiment analysis or stock news
    question = "What is the overall sentiment for this stock in the latest quarter?"

    # Query the RAG system
    print(query_rag(stock_symbol=stock_symbol, question=question))


if __name__ == "__main__":
    main()
