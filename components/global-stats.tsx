import { Clock, ShieldCheck, Zap, GitBranch } from "lucide-react"

const STATS = [
  { label: "Pull Requests Reviewed", value: "1,284", icon: GitBranch, sub: "+12% this week" },
  { label: "Security Vulnerabilities Patched", value: "412", icon: ShieldCheck, sub: "0 critical pending" },
  { label: "Avg. Review Time", value: "42s", icon: Clock, sub: "vs 4.2h human" },
  { label: "Agent Success Rate", value: "99.2%", icon: Zap, sub: "Verified by Weave" },
]

export function GlobalStats() {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
      {STATS.map((stat) => (
        <div
          key={stat.label}
          className="group relative overflow-hidden rounded-xl border border-white/5 bg-[#171717] p-6 transition-all hover:bg-[#1a1a1a]"
        >
          <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-[#69E300]/10 border border-[#69E300]/20 text-[#69E300]">
            <stat.icon className="h-5 w-5" />
          </div>
          <div className="space-y-1">
            <h4 className="text-[11px] font-bold uppercase tracking-widest text-white/30">{stat.label}</h4>
            <div className="text-3xl font-black text-white group-hover:text-[#69E300] transition-colors">
              {stat.value}
            </div>
            <p className="text-[11px] font-medium text-[#69E300]/60">{stat.sub}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
