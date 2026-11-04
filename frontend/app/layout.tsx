import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import { AnalysisProvider } from "@/context/AnalysisContext";
import { AnimationProvider } from "@/context/AnimationContext";
import { GlobalFloatingLeaves } from "@/components/ambient/GlobalFloatingLeaves";

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "CanopyAI — AI-Powered Forest Carbon Intelligence",
  description:
    "High-resolution forest carbon stock estimation, biomass mapping, and MRV verification using multi-sensor satellite imagery and AI.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable} antialiased`}
    >
      <body className="min-h-screen bg-background font-sans text-charcoal relative">
        <AnimationProvider>
          <AuthProvider>
            <AnalysisProvider>
              <GlobalFloatingLeaves />
              {children}
            </AnalysisProvider>
          </AuthProvider>
        </AnimationProvider>
      </body>
    </html>
  );
}
