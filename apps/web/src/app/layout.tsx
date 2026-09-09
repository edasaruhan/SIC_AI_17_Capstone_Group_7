import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: { default: "GrowthPilot", template: "%s · GrowthPilot" }, description: "Grounded customer operations and accountable marketing decisions." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
