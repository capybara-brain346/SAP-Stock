"use client";

import { useState } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Home() {
    const [stockSymbol, setStockSymbol] = useState("");
    const [stockPrice, setStockPrice] = useState<number | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [historicalData, setHistoricalData] = useState([]);

    const fetchStockPrice = async () => {
        setLoading(true);
        setError("");
        try {
            // Fetch latest stock price
            const response = await axios.get(`http://127.0.0.1:5000/api/stock?symbol=${stockSymbol}`);
            const price = response.data.currentPrice;
            setStockPrice(price);

            // Fetch historical data
            const historicalResponse = await axios.get(`http://127.0.0.1:5000/stock_data/${stockSymbol}`);
            const historicalPrices = historicalResponse.data.values.map((value, index) => ({
                name: historicalResponse.data.labels[index], // Use actual dates
                price: value,
            }));
            setHistoricalData(historicalPrices);
        } catch (error) {
            console.error("Error fetching stock price:", error);
            setError("Error fetching stock price. Please check the symbol.");
            setStockPrice(null);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            {/* Your existing landing page content goes here... */}
            
            <div className="flex flex-col items-center my-4">
                <input
                    type="text"
                    placeholder="Enter stock symbol (e.g., AAPL)"
                    value={stockSymbol}
                    onChange={(e) => setStockSymbol(e.target.value)}
                    className="border rounded p-2"
                />
                <Button onClick={fetchStockPrice} className="mt-2" disabled={loading}>
                    {loading ? "Fetching..." : "Get Insights"}
                </Button>
                {/* Display Stock Price */}
                {stockPrice !== null && (
                    <p className="mt-4 text-lg">
                        Latest Closing Price: ${stockPrice.toFixed(2)}
                    </p>
                )}
                {error && <p className="mt-4 text-red-500">{error}</p>}

                {/* Line Chart */}
                {historicalData.length > 0 && (
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={historicalData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Line type="monotone" dataKey="price" stroke="#8884d8" activeDot={{ r: 8 }} />
                        </LineChart>
                    </ResponsiveContainer>
                )}
            </div>

            {/* Footer */}
            <footer className="border-t border-border p-4 text-center">
                <p>&copy; 2024 Your Company Name. All rights reserved.</p>
            </footer>
        </>
    );
}
