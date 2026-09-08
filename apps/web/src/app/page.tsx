import { ArrowUpRight, Compass, ShieldCheck } from "lucide-react";

export default function Home() {
  return <main className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-20">
    <div className="mb-16 flex items-center gap-3 text-lg font-semibold"><span className="rounded-xl bg-emerald-950 p-3 text-lime-200"><Compass size={24} /></span> GrowthPilot</div>
    <div className="mb-6 flex items-center gap-2 text-xs font-semibold uppercase tracking-[.2em] text-emerald-800"><span className="h-2 w-2 rounded-full bg-emerald-600" /> Customer operations, connected</div>
    <h1 className="max-w-3xl text-5xl font-semibold leading-[1.08] tracking-tight md:text-7xl">Know your customers.<br /><span className="text-emerald-700">Make the next move.</span></h1>
    <p className="mt-7 max-w-xl text-lg leading-8 text-neutral-600">Your customer history, sales, and marketing decisions in one accountable workspace.</p>
    <div className="mt-12 max-w-lg rounded-2xl border border-neutral-200 bg-white p-7">
      <div className="mb-3 flex items-center justify-between"><h2 className="font-semibold">Workspace setup</h2><ArrowUpRight size={18} /></div>
      <p className="text-sm leading-6 text-neutral-500">This local installation is being configured. Your workspace will appear after authenticated organization access is available.</p>
      <div className="mt-6 flex items-center gap-2 border-t border-neutral-100 pt-4 text-xs text-neutral-500"><ShieldCheck size={16} /> Organization access is verified on the server.</div>
    </div>
  </main>;
}
