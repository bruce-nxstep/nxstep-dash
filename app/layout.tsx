import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/organisms/Header";
import { Footer } from "@/components/layout/Footer";
import { NavigationWrapper } from "@/components/layout/NavigationWrapper";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "NXSTEP - Solutions Digitales",
  description: "Accompagnement dans votre transformation numérique",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" className="dark">
      <body
        className={`${inter.variable} antialiased min-h-screen flex flex-col font-sans bg-background text-foreground`}
      >
        <NavigationWrapper header={<Header />} footer={<Footer />}>
          {children}
        </NavigationWrapper>
      </body>
    </html>
  );
}
