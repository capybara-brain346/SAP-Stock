import os
import logging
from typing import List, Tuple
from langchain_chroma import Chroma
from langchain_community.document_loaders import JSONLoader
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
        news_file = r"backend\data\scraped_results.json"
        news_context = ""

        with open(news_file, "r", encoding="utf-8") as f:
            news_context = f.read()

        db = Chroma(
            persist_directory="chroma_stock",
            embedding_function=GoogleGenerativeAIEmbeddings(
                model="models/embedding-001"
            ),
        )

        db.add_texts([news_context])

        results = db.similarity_search_with_score(stock_symbol, k=len(db.get()["ids"]))

        context_text = " ".join([doc.page_content for doc, _score in results])

        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(
            stock_symbol=stock_symbol, context=context_text, question=question
        )

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
    stock_symbol = "TATA"  # Example stock symbol

    question = "What is the overall sentiment for this stock in the latest quarter?"

    print(query_rag(stock_symbol=stock_symbol, question=question))


if __name__ == "__main__":
    main()
