import { ArrowLeft, CircleAlert } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { AppShell } from "@/components/app-shell";
import { apiGet } from "@/lib/api";

type Customer = { id: string; name: string; email: string | null; phone: string | null; status: string; tags: string[] };
type Summary = { recency_days: number | null; frequency: number; monetary: string; currency: string; segment: string; churn_probability: number | null; model_status: string };

export const metadata: Metadata = { title: "Customer 360" };

export default async function CustomerPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params; const [customer, summary] = await Promise.all([apiGet<Customer>(`/api/v1/customers/${id}`), apiGet<Summary>(`/api/v1/analytics/customers/${id}`)]);
  return <AppShell active="customers"><Link className="back-link" href="/customers"><ArrowLeft size={16} /> Customers</Link>{!customer.ok ? <section className="state-panel"><CircleAlert /><div><h2>Customer unavailable</h2><p>{customer.message}</p></div></section> : <><header className="page-header compact"><div><p className="eyebrow">Customer 360</p><h1>{customer.data.name}</h1><p>{customer.data.email ?? "No email"} · {customer.data.phone ?? "No phone"}</p></div><span className="evidence-badge">{customer.data.status}</span></header><section className="metric-grid three">{summary.ok ? <><article className="metric-card"><span>Recency</span><strong>{summary.data.recency_days ?? "—"}</strong><small>Days since last order</small></article><article className="metric-card"><span>Frequency</span><strong>{summary.data.frequency}</strong><small>Observed purchases</small></article><article className="metric-card"><span>Customer value</span><strong>{summary.data.currency} {summary.data.monetary}</strong><small>Net observed revenue</small></article></> : <article className="state-panel"><CircleAlert /><p>{summary.message}</p></article>}</section><section className="content-grid"><article className="panel"><p className="eyebrow">Profile</p><h2>{customer.data.tags.length ? customer.data.tags.join(" · ") : "No tags"}</h2><p>Deterministic segment: {summary.ok ? summary.data.segment.replaceAll("_", " ") : "unavailable"}</p></article><article className="panel"><p className="eyebrow">Intelligence</p><h2>{summary.ok && summary.data.churn_probability !== null ? `${Math.round(summary.data.churn_probability * 100)}% inactivity risk` : "Not scored"}</h2><p>{summary.ok ? summary.data.model_status.replaceAll("_", " ") : "No model state available"}. Scores never authorize outreach.</p></article></section></> }</AppShell>;
}
