"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from "recharts";

export default function Home() {
    const [stock1, setStock1] = useState("");
    const [stock2, setStock2] = useState("");
    const [historicalData, setHistoricalData] = useState([]);
    const [sentimentData, setSentimentData] = useState<Record<string, any>>({});
    const [loadingData, setLoadingData] = useState(false);
    const [loadingSentiment, setLoadingSentiment] = useState(false);

    // ✅ Fetch last 30 trading days for both stocks
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

            // ✅ Convert timestamps to real dates & align both stocks
            const formatStockData = (data: any, symbol: string) =>
                Object.entries(data.values)
                    .slice(-30) // Get last 30 trading days
                    .map(([date, price]) => ({
                        date: new Date(date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
                        [symbol]: price, // Store under stock symbol
                    }));

            // ✅ Merge both stocks based on date
            const mergedData = mergeStockData(formatStockData(response1.data, stock1), formatStockData(response2.data, stock2));

            setHistoricalData(mergedData);

        } catch (error) {
            console.error("Error fetching stock data:", error);
        } finally {
            setLoadingData(false);
        }
    };

    // ✅ Merge stock data by date
    const mergeStockData = (data1: any[], data2: any[]) => {
        const mergedMap: Record<string, any> = {};
        data1.forEach(entry => mergedMap[entry.date] = { ...mergedMap[entry.date], ...entry });
        data2.forEach(entry => mergedMap[entry.date] = { ...mergedMap[entry.date], ...entry });
        return Object.values(mergedMap);
    };

    // ✅ Fetch sentiment comparison for both stocks
    const fetchSentimentComparison = async () => {
        if (!stock1 || !stock2) {
            alert("Please enter two stock symbols.");
            return;
        }

        setLoadingSentiment(true);
        try {
            const response = await axios.post("http://127.0.0.1:5000/api/sentiment_comparison", { symbols: [stock1, stock2] });
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

                {/* ✅ Stock Price Comparison (Last 30 Days) */}
                {historicalData.length > 0 && (
                    <div className="my-8">
                        <h2 className="text-3xl font-bold">Stock Price Trends (Last 30 Days)</h2>
                        <ResponsiveContainer width="100%" height={400}>
                            <LineChart data={historicalData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="date" />
                                <YAxis />
                                <Tooltip />
                                <Line type="monotone" dataKey={stock1} stroke="#FF5733" name={stock1} />
                                <Line type="monotone" dataKey={stock2} stroke="#4287f5" name={stock2} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                )}

                {/* ✅ Sentiment Comparison Table */}
                {Object.keys(sentimentData).length > 0 && (
                    <div className="my-8">
                        <h2 className="text-3xl font-bold">Sentiment Comparison</h2>
                        <div className="overflow-x-auto">
                            <table className="w-full border-collapse border border-gray-300">
                                <thead>
                                    <tr className="bg-gray-200">
                                        <th className="border border-gray-300 p-2">Stock</th>
                                        <th className="border border-gray-300 p-2">Positive</th>
                                        <th className="border border-gray-300 p-2">Neutral</th>
                                        <th className="border border-gray-300 p-2">Negative</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {Object.keys(sentimentData).map((symbol) => {
                                        const sentimentCounts = sentimentData[symbol]?.sentiment_counts || {};
                                        return (
                                            <tr key={symbol} className="text-center">
                                                <td className="border border-gray-300 p-2 font-bold">{symbol.toUpperCase()}</td>
                                                <td className="border border-gray-300 p-2">{sentimentCounts.positive || 0}</td>
                                                <td className="border border-gray-300 p-2">{sentimentCounts.neutral || 0}</td>
                                                <td className="border border-gray-300 p-2">{sentimentCounts.negative || 0}</td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>

                        {/* ✅ Sentiment Bar Chart */}
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
