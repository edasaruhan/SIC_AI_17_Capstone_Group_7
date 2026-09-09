import { ArrowUpRight, CircleAlert, TrendingUp, Users, WalletCards } from "lucide-react";
import Link from "next/link";
import { AppShell } from "@/components/app-shell";
import { ApiState, apiGet } from "@/lib/api";
import { evidenceLabel } from "@/lib/presentation";

type Overview = { evidence: string; currency: string; net_revenue: string; orders: number; customers: number; low_stock_products: number; roas: string | null; availability_notes: string[] };
const number = new Intl.NumberFormat("en-US");

function Metric({ label, value, note, icon }: { label: string; value: string; note: string; icon: React.ReactNode }) {
  return <article className="metric-card"><div className="metric-icon">{icon}</div><span>{label}</span><strong>{value}</strong><small>{note}</small></article>;
}

export default async function Home() {
  const result: ApiState<Overview> = await apiGet("/api/v1/analytics/overview");
  return <AppShell active="overview"><header className="page-header"><div><p className="eyebrow">Command center</p><h1>Good decisions start with grounded data.</h1><p>Operational performance, customer signals, and review queues in one accountable view.</p></div><span className="evidence-badge">{result.ok ? evidenceLabel(result.data.evidence) : "data unavailable"}</span></header>
    {!result.ok ? <section className="state-panel"><CircleAlert /><div><h2>{result.kind === "unconfigured" ? "Connect your workspace" : "Dashboard unavailable"}</h2><p>{result.message}</p></div></section> : <><section className="metric-grid"><Metric label="Net revenue" value={`${result.data.currency} ${result.data.net_revenue}`} note="Sales less posted refunds" icon={<WalletCards />} /><Metric label="Orders" value={number.format(result.data.orders)} note="Selected operational period" icon={<TrendingUp />} /><Metric label="Customers" value={number.format(result.data.customers)} note="Current customer records" icon={<Users />} /><Metric label="ROAS" value={result.data.roas ?? "Not available"} note="Requires verified provider spend" icon={<ArrowUpRight />} /></section><section className="content-grid"><article className="panel"><div className="panel-heading"><div><p className="eyebrow">Attention</p><h2>Operational signals</h2></div><span>{result.data.low_stock_products} low stock</span></div><ul className="note-list">{result.data.availability_notes.map((note) => <li key={note}>{note}</li>)}</ul></article><article className="panel dark-panel"><p className="eyebrow">Decision safety</p><h2>Recommendations remain review-only.</h2><p>Customer risk is a prioritization signal. Consent and a permitted human approval remain mandatory before any outreach.</p><Link href="/decisions">Open review queue <ArrowUpRight size={16} /></Link></article></section></>}
  </AppShell>;
}

export const dynamic = "force-dynamic";
