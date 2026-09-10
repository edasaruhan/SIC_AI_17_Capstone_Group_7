import { ArrowUpRight, CircleAlert, DatabaseZap } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { AppShell } from "@/components/app-shell";
import { apiGet } from "@/lib/api";
import { displayValue, type DisplayValue } from "@/lib/presentation";

type RecordValue = DisplayValue;
type Section = { title: string; eyebrow: string; description: string; endpoint?: string; key: string; empty: string; fields?: string[] };
const sections: Record<string, Section> = {
  customers: { title: "Customers", eyebrow: "CRM", description: "Searchable customer records with consent and interaction history.", endpoint: "/api/v1/customers", key: "items", empty: "No customers are in this workspace yet.", fields: ["name", "email", "status"] },
  orders: { title: "Orders", eyebrow: "Commerce", description: "Canonical orders, payments, and refund-aware totals.", endpoint: "/api/v1/orders", key: "root", empty: "No orders have been recorded.", fields: ["placed_at", "status", "total", "currency"] },
  products: { title: "Products", eyebrow: "Catalog", description: "Sellable catalog and current stock position.", endpoint: "/api/v1/products", key: "root", empty: "No products have been added.", fields: ["name", "sku", "stock_on_hand", "unit_price"] },
  inventory: { title: "Inventory", eyebrow: "Operations", description: "Append-only stock movements and traceable adjustments.", endpoint: "/api/v1/inventory/movements", key: "root", empty: "No inventory movements have been recorded.", fields: ["created_at", "quantity_delta", "reason"] },
  imports: { title: "Imports", eyebrow: "Data intake", description: "Secure staged CSV/XLSX inspection, mapping, and canonical commit.", endpoint: "/api/v1/imports", key: "root", empty: "No import batches have been started.", fields: ["kind", "status", "filename", "created_at"] },
  intelligence: { title: "Customer intelligence", eyebrow: "Prioritization", description: "Churn-proxy risk, RFM context, model lineage, and explanations.", key: "none", empty: "Open a customer record to request an eligible demo score." },
  audiences: { title: "Audiences", eyebrow: "Activation", description: "Versioned segment definitions with consent-aware membership snapshots.", endpoint: "/api/v1/marketing/audiences", key: "root", empty: "No audience definitions are available yet.", fields: ["name", "version", "status"] },
  integrations: { title: "Integrations", eyebrow: "Integration hub", description: "Provider accounts, sync checkpoints, health, and evidence boundaries.", endpoint: "/api/v1/integrations", key: "root", empty: "No provider account has been connected.", fields: ["name", "provider", "status", "last_success_at"] },
  campaigns: { title: "Campaigns", eyebrow: "Marketing", description: "Approval-controlled campaign drafts and provider synchronization.", endpoint: "/api/v1/marketing/campaigns", key: "root", empty: "No campaign drafts have been created.", fields: ["name", "provider", "status", "budget"] },
  decisions: { title: "Decision review", eyebrow: "Human control", description: "Review recommendations, consent evidence, and approval requirements.", key: "none", empty: "No recommendations are awaiting review." },
  audit: { title: "Audit trail", eyebrow: "Governance", description: "Immutable operational evidence for meaningful workspace events.", endpoint: "/api/v1/audit", key: "root", empty: "No audit evidence is visible to this role.", fields: ["created_at", "event_type", "entity_id"] },
  settings: { title: "Workspace settings", eyebrow: "Administration", description: "Organization context, team roles, permissions, and safety controls.", endpoint: "/api/v1/workspace", key: "object", empty: "Workspace configuration is unavailable.", fields: ["name", "role", "timezone", "currency"] },
};

export async function generateMetadata({ params }: { params: Promise<{ section: string }> }): Promise<Metadata> {
  const { section } = await params;
  return { title: sections[section]?.title ?? "Page not found" };
}

export default async function SectionPage({ params }: { params: Promise<{ section: string }> }) {
  const { section: slug } = await params; const section = sections[slug]; if (!section) notFound();
  const result = section.endpoint ? await apiGet<unknown>(section.endpoint) : null; let rows: Record<string, RecordValue>[] = [];
  if (result?.ok) { const data = result.data as Record<string, RecordValue> | Record<string, RecordValue>[] | { items: Record<string, RecordValue>[] }; rows = section.key === "root" ? data as Record<string, RecordValue>[] : section.key === "items" ? (data as { items: Record<string, RecordValue>[] }).items : [data as Record<string, RecordValue>]; }
  return <AppShell active={slug}><header className="page-header compact"><div><p className="eyebrow">{section.eyebrow}</p><h1>{section.title}</h1><p>{section.description}</p></div>{slug === "customers" && <span className="button-muted">New customer</span>}</header>
    {result && !result.ok ? <section className="state-panel"><CircleAlert /><div><h2>{result.kind === "unconfigured" ? "Workspace connection required" : "Data unavailable"}</h2><p>{result.message}</p></div></section> : rows.length ? <section className="record-list">{rows.map((row, index) => <article key={String(row.id ?? index)}>{section.fields?.map((field, fieldIndex) => <div key={field} className={fieldIndex === 0 ? "primary-field" : ""}><small>{field.replaceAll("_", " ")}</small><span>{displayValue(row[field])}</span></div>)}{slug === "customers" && row.id && <Link href={`/customers/${row.id}`}>Open <ArrowUpRight size={15} /></Link>}</article>)}</section> : <section className="empty-panel"><DatabaseZap /><h2>{section.empty}</h2><p>GrowthPilot does not invent placeholder business data. Valid records will appear here when created or imported.</p></section>}
  </AppShell>;
}
