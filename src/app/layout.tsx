import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";

// Load the Outfit font from Google Fonts
// This font will be used throughout the application
const outfit = Outfit({
  variable: "--font-outfit", // CSS variable name we can use in our styles
  subsets: ["latin"],        // Only load Latin characters to reduce bundle size
});

// Metadata for SEO and browser display
export const metadata: Metadata = {
  title: "Mess Feedback App",
  description: "Student feedback and admin analytics portal",
};

// Root layout component - wraps all pages in the app
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      {/* 
        suppressHydrationWarning: This tells React to ignore small differences
        between server and client rendering (like browser extensions adding classes).
        This is safe to use here because the body element doesn't need exact matching.
      */}
      <body
        className={`${outfit.variable} antialiased`}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}
