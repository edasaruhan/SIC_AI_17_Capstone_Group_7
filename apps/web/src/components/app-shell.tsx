import { Activity, Boxes, Cable, ChartNoAxesCombined, CircleGauge, ClipboardCheck, FileUp, Megaphone, PackageCheck, Settings2, ShieldCheck, ShoppingBag, Sparkles, Users } from "lucide-react";
import Link from "next/link";

const navigation = [
  ["overview", "/", "Overview", CircleGauge], ["customers", "/customers", "Customers", Users], ["intelligence", "/intelligence", "Intelligence", Sparkles], ["audiences", "/audiences", "Audiences", ChartNoAxesCombined], ["orders", "/orders", "Orders", ShoppingBag], ["products", "/products", "Products", PackageCheck], ["inventory", "/inventory", "Inventory", Boxes], ["imports", "/imports", "Imports", FileUp], ["integrations", "/integrations", "Integrations", Cable], ["campaigns", "/campaigns", "Campaigns", Megaphone], ["decisions", "/decisions", "Decisions", ClipboardCheck], ["audit", "/audit", "Audit", Activity],
] as const;

export function AppShell({ active, children }: { active: string; children: React.ReactNode }) {
  return <div className="app-frame"><aside className="sidebar"><Link href="/" className="brand"><span>GP</span><div>GrowthPilot<small>Customer operations</small></div></Link><nav aria-label="Primary navigation">{navigation.map(([key, href, label, Icon]) => <Link key={key} href={href} aria-current={active === key ? "page" : undefined} className={active === key ? "active" : ""}><Icon size={18} /><span>{label}</span></Link>)}</nav><div className="sidebar-footer"><Link href="/settings"><Settings2 size={18} /> Settings</Link><div><ShieldCheck size={16} /><span>Server-enforced workspace</span></div></div></aside><main className="workspace"><div className="topbar"><div><span className="status-dot" /> Local workspace</div><span>GrowthPilot v0.1</span></div><div className="page-content">{children}</div></main></div>;
}
