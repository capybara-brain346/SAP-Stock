"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from "recharts";

export default function Home() {
    const [stock1, setStock1] = useState("");
    const [stock2, setStock2] = useState("");
    const [historicalData, setHistoricalData] = useState<Record<string, any>>({});
    const [sentimentData, setSentimentData] = useState<Record<string, any>>({});
    const [loadingData, setLoadingData] = useState(false);
    const [loadingSentiment, setLoadingSentiment] = useState(false);

    // ✅ Fetch stock price trends for both stocks
    const fetchStockComparison = async () => {
        if (!stock1 || !stock2) {
            alert("Please enter two stock symbols.");
            return;
        }

        setLoadingData(true);
        try {
            const [response1, response2] = await Promise.all([
                axios.get(`http://127.0.0.1:5000/stock_data/${stock1}`),
                axios.get(`http://127.0.0.1:5000/stock_data/${stock2}`)
            ]);

            setHistoricalData({
                [stock1]: response1.data.values.map((value: number, index: number) => ({ name: `Day ${index + 1}`, price: value })),
                [stock2]: response2.data.values.map((value: number, index: number) => ({ name: `Day ${index + 1}`, price: value }))
            });

        } catch (error) {
            console.error("Error fetching stock data:", error);
        } finally {
            setLoadingData(false);
        }
    };

    // ✅ Fetch sentiment analysis for both stocks
    const fetchSentimentComparison = async () => {
        if (!stock1 || !stock2) {
            alert("Please enter two stock symbols.");
            return;
        }

        setLoadingSentiment(true);
        try {
            const response = await axios.post("http://127.0.0.1:5000/api/sentiment_comparison", { symbols: [stock1, stock2] });
            console.log("DEBUG: Sentiment Comparison API Response:", response.data);
            setSentimentData(response.data);
        } catch (error) {
            console.error("Error fetching sentiment comparison:", error);
        } finally {
            setLoadingSentiment(false);
        }
    };

    return (
        <>
            <div className="container mx-auto text-center">
                <h1 className="text-5xl font-extrabold my-4">Compare Stocks</h1>

                {/* Stock Inputs */}
                <div className="flex justify-center gap-4 my-4">
                    <input
                        type="text"
                        placeholder="Stock 1 (e.g., AAPL)"
                        value={stock1}
                        onChange={(e) => setStock1(e.target.value.toUpperCase())}
                        className="border rounded p-2"
                    />
                    <input
                        type="text"
                        placeholder="Stock 2 (e.g., MSFT)"
                        value={stock2}
                        onChange={(e) => setStock2(e.target.value.toUpperCase())}
                        className="border rounded p-2"
                    />
                </div>

                <div className="flex justify-center gap-4">
                    <Button onClick={fetchStockComparison} disabled={loadingData}>
                        {loadingData ? "Loading..." : "Compare Prices"}
                    </Button>
                    <Button onClick={fetchSentimentComparison} disabled={loadingSentiment}>
                        {loadingSentiment ? "Loading..." : "Compare Sentiments"}
                    </Button>
                </div>

                {/* Stock Price Comparison */}
                {Object.keys(historicalData).length > 0 && (
                    <div className="my-8">
                        <h2 className="text-3xl font-bold">Stock Price Trends</h2>
                        <ResponsiveContainer width="100%" height={400}>
                            <LineChart>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip />
                                {Object.keys(historicalData).map((symbol, index) => (
                                    <Line
                                        key={symbol}
                                        type="monotone"
                                        dataKey="price"
                                        data={historicalData[symbol]}
                                        stroke={["#FF5733", "#4287f5"][index]} // Different colors for different stocks
                                        name={symbol}
                                    />
                                ))}
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                )}

                {/* Sentiment Comparison */}
                {Object.keys(sentimentData).length > 0 && (
                    <div className="my-8">
                        <h2 className="text-3xl font-bold">Sentiment Comparison</h2>
                        <ResponsiveContainer width="100%" height={400}>
                            <BarChart data={Object.keys(sentimentData).map((symbol) => ({
                                name: symbol.toUpperCase(),
                                positive: sentimentData[symbol]?.sentiment_counts?.positive || 0,
                                neutral: sentimentData[symbol]?.sentiment_counts?.neutral || 0,
                                negative: sentimentData[symbol]?.sentiment_counts?.negative || 0,
                            }))}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="positive" fill="#4CAF50" name="Positive" />
                                <Bar dataKey="neutral" fill="#FFC107" name="Neutral" />
                                <Bar dataKey="negative" fill="#F44336" name="Negative" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </div>
        </>
    );
}
