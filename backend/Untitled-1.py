
@app.route("/api/sentiments", methods=["POST"])
def sentiment():
    """Fetches news and performs sentiment analysis."""
    data = request.json
    symbol = data.get("symbol", "").upper().strip()

    if not symbol:
        return jsonify({"error": "Please provide a valid stock symbol for sentiment analysis."}), 400

    newsapi_symbol = clean_symbol_for_newsapi(symbol)

    try:
        # Fetch latest & relevant news articles
        latest_articles = newsapi.get_everything(q=newsapi_symbol, language="en", sort_by="publishedAt", page_size=3)
        relevant_articles = newsapi.get_everything(q=newsapi_symbol, language="en", sort_by="relevancy", page_size=3)

        # Process articles
        latest_news = [
            {"title": article["title"], "description": article.get("description", ""), "url": article["url"]}
            for article in latest_articles.get("articles", [])
        ]
        relevant_news = [
            {"title": article["title"], "description": article.get("description", ""), "url": article["url"]}
            for article in relevant_articles.get("articles", [])
        ]

        # Combine & remove duplicates
        combined_news = {article["url"]: article for article in latest_news + relevant_news}.values()
        limited_news = list(combined_news)[:5]

        if not limited_news:
            return jsonify({"error": "No relevant news articles found."}), 404

        # Prepare for sentiment analysis
        news_texts = [f"{article['title']} {article['description']}" for article in limited_news]
        sentiment = SentimentAnalysis(news_texts).sentiment_analysis()
        links = [article["url"] for article in limited_news]

        return jsonify({"sentiments": sentiment, "links": links})

    except NewsAPIException as e:
        error_data = e.args[0]
        if error_data.get("code") == "rateLimited":
            return jsonify({"error": "NewsAPI request limit reached. Try again later."}), 429

    except Exception as e:
        logging.error(f"Error in sentiment analysis: {e}")
        return jsonify({"error": str(e)}), 500

