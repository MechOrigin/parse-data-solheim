import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/ThemeProvider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Acronym Completion Platform",
  description: "AI-powered acronym completion and management platform",
  icons: {
    icon: [
      {
        url: "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzRGM0Y1MCI+PHBhdGggZD0iTTEyIDJMMiA3djEwbDEwIDUgMTAtNVY3TDEyIDJ6bTAgMmw2IDMtNiAzLTYtM2w2LTN6Ii8+PC9zdmc+",
        type: "image/svg+xml",
      }
    ],
    apple: [
      {
        url: "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzRGM0Y1MCI+PHBhdGggZD0iTTEyIDJMMiA3djEwbDEwIDUgMTAtNVY3TDEyIDJ6bTAgMmw2IDMtNiAzLTYtM2w2LTN6Ii8+PC9zdmc+",
        type: "image/svg+xml",
      }
    ],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzRGM0Y1MCI+PHBhdGggZD0iTTEyIDJMMiA3djEwbDEwIDUgMTAtNVY3TDEyIDJ6bTAgMmw2IDMtNiAzLTYtM2w2LTN6Ii8+PC9zdmc+" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzRGM0Y1MCI+PHBhdGggZD0iTTEyIDJMMiA3djEwbDEwIDUgMTAtNVY3TDEyIDJ6bTAgMmw2IDMtNiAzLTYtM2w2LTN6Ii8+PC9zdmc+" type="image/svg+xml" />
      </head>
      <body className={`${inter.variable} font-sans antialiased min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-indigo-950 dark:to-purple-900`}>
        <ThemeProvider>
          <div className="min-h-screen flex flex-col">
            <header className="sticky top-0 z-50 glass-panel border-b border-gray-200/50 dark:border-gray-700/50">
              <div className="container mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                  <h1 className="enterprise-heading">
                    Acronym Completion Platform
                  </h1>
                  <div className="flex items-center space-x-4">
                    {/* Add any header actions/buttons here */}
                  </div>
                </div>
              </div>
            </header>
            <main className="flex-1 relative">
              {/* Background decoration */}
              <div className="absolute inset-0 -z-10 overflow-hidden">
                <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-indigo-500/10 to-purple-500/10 rounded-full blur-3xl" />
                <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-full blur-3xl" />
              </div>
              {children}
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
