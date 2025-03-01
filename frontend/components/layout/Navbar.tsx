import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { navLinks } from "@/data/navLinks";
import { ThemeChanger } from "@/app/Theme-changer";

const Navbar = () => {
    return (
        <nav className="py-4 bg-background/30 backdrop-blur-sm">
            <div className="container flex flex-row justify-between items-center">
                {/* Logo */}
                <Link href="/">
                    <Image 
                        src="/logo2.png" // Ensure the filename has no spaces
                        alt="Logo"
                        width={180}
                        height={50}
                        className="object-contain"
                        priority // Optimized loading
                    />
                </Link>

                {/* Navigation Links */}
                <ul className="md:flex flex-row justify-between gap-8 hidden">
                    {navLinks.map((link) => (
                        <li key={link.title}>
                            <Link href={link.href} className="hover:text-primary transition">
                                {link.title}
                            </Link>
                        </li>
                    ))}
                </ul>

                {/* Right Actions */}
                <div className="flex flex-row justify-end space-x-2">
                    <ThemeChanger />
                    <Button>
                        Get Started
                    </Button>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
