import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "GrowthPilot — Customer operations", description: "Understand your customers. Make accountable marketing decisions." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
