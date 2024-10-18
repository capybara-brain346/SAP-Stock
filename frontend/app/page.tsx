"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { ArrowRightIcon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { features } from "@/data/features"; // Ensure you have this file or modify as needed
import axios from "axios"; // Make sure to install axios with `npm install axios`

export default function Home() {
    const [stockSymbol, setStockSymbol] = useState("");
    const [stockPrice, setStockPrice] = useState<number | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const fetchStockPrice = async () => {
        setLoading(true);
        setError(""); // Reset error message
        try {
            const response = await axios.get(`http://127.0.0.1:5000/api/stock?symbol=${stockSymbol}`);
            const price = response.data.currentPrice; // Use `response.data.price` directly
            setStockPrice(price);
            console.log(error)
            console.log(price)
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
            <div className="border-b border-border">
                <main className="container mx-auto">
                    <div className="relative md:mt-24 mx-auto w-full max-w-4xl pt-4 text-center">
                        <div className="justify-center hidden md:flex">
                            <div className="flex flex-row items-center justify-center gap-5 p-1 text-xs bg-card/60 backdrop-blur-lg rounded-md border border-border">
                                <Badge className="font-semibold">New</Badge>
                                <h5>Announce your new feature here</h5>
                                <Link href="/" className="flex flex-row items-center">
                                    View all features
                                    <ArrowRightIcon className="w-6 h-6 ml-2" />
                                </Link>
                            </div>
                        </div>
                        <h1 className="md:text-7xl my-4 font-extrabold text-4xl md:leading-tight">SAP Stock!</h1>
                        <p className="mx-auto my-4 text-sm w-full max-w-xl text-center font-medium leading-relaxed tracking-wide">
                            This is a landing page template that you can use to create a beautiful website. It is
                            designed to be easy to use and customize.
                        </p>

                        {/* Input Box for Stock Symbol */}
                        <div className="flex flex-col items-center my-4">
                            <input
                                type="text"
                                placeholder="Enter stock symbol (e.g., AAPL)"
                                value={stockSymbol}
                                onChange={(e) => setStockSymbol(e.target.value)}
                                className="border rounded p-2"
                            />
                            <Button onClick={fetchStockPrice} className="mt-2" disabled={loading}>
                                {loading ? "Fetching..." : "Get Stock Price"}
                            </Button>
                        </div>

                        {/* Display Stock Price */}
                        {stockPrice !== null && (
                            <p className="mt-4 text-lg">
                                Current Price: ${stockPrice.toFixed(2)}
                            </p>
                        )}
                        
                        {error && <p className="mt-4 text-red-500">{error}</p>}

                        <div className="flex flex-row justify-center items-center space-x-4 my-8">
                            <Button>
                                Get Started
                            </Button>
                            <Button variant="secondary">
                                Learn More
                            </Button>
                        </div>

                        <div className="absolute top-0 -z-10 max-h-full max-w-screen-lg w-full h-full blur-2xl">
                            <div className="absolute top-24 left-24 w-56 h-56 bg-violet-600 rounded-full mix-blend-multiply opacity-70 animate-blob filter blur-3xl"></div>
                            <div className="absolute hidden md:block bottom-2 right-1/4 w-56 h-56 bg-sky-600 rounded-full mix-blend-multiply opacity-70 animate-blob delay-1000 filter blur-3xl"></div>
                            <div className="absolute hidden md:block bottom-1/4 left-1/3 w-56 h-56 bg-pink-600 rounded-full mix-blend-multiply opacity-70 animate-blob delay-500 filter blur-3xl"></div>
                        </div>
                    </div>

                    <div className="max-w-4xl mx-auto mb-8">
                        <Image className="w-full" src="/dashboard-ui.png" alt="Dashboard ui design" priority width={1200} height={800} />
                    </div>
                </main>
            </div>

            {/* features */}
            <section className="border-b border-border bg-gradient-to-b from-background to-transparent via-background via-90% relative">
                <div className="container mx-auto text-center">
                    <div className="my-24">
                        <h5 className="text-primary">WHY CHOOSE US</h5>
                        <h2 className="text-4xl font-extrabold my-4">Build better websites with us</h2>
                        <p className="mx-auto my-4 text-sm w-full max-w-md bg-transparent text-center font-medium leading-relaxed tracking-wide text-muted-foreground">
                            Show off your features or services in a beautiful way. This section is perfect for showcasing
                        </p>

                        <div className="flex flex-col md:flex-row gap-4 mt-12">
                            {features.map((feature) => (
                                <Card key={feature.title} className="max-w-lg mx-auto">
                                    <CardHeader>
                                        <div className="w-16 h-16 text-primary-foreground flex justify-center items-center border border-border rounded-xl bg-primary mx-auto">
                                            {feature.icon}
                                        </div>
                                    </CardHeader>
                                    <CardContent>
                                        <CardTitle>{feature.title}</CardTitle>
                                        <CardDescription className="mt-4">
                                            {feature.description}
                                        </CardDescription>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </div>
                </div>
                <div className="absolute top-0 -z-10 max-h-full w-full h-full blur-2xl">
                    <div className="absolute bottom-0 left-0 w-1/2 h-56 bg-violet-600 rounded-full mix-blend-multiply opacity-70 animate-blob filter blur-3xl"></div>
                    <div className="absolute top-24 right-0 w-1/2 h-56 bg-sky-600 rounded-full mix-blend-multiply opacity-70 animate-blob delay-1000 filter blur-3xl"></div>
                </div>
            </section>
        </>
    );
}
