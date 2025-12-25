import { ShieldCheck, Activity, FileText, Zap, TrendingUp, TrendingDown } from "lucide-react"
import { cn } from "@/lib/utils"

const METRICS = [
  {
    label: "Security Health",
    value: "94",
    trend: "+2.4%",
    up: true,
    icon: ShieldCheck,
    description: "Vulnerability-free code segments",
  },
  {
    label: "Code Stability",
    value: "98.2%",
    trend: "+0.5%",
    up: true,
    icon: Activity,
    description: "Runtime validation pass rate",
  },
  {
    label: "Docs Coverage",
    value: "87%",
    trend: "-1.2%",
    up: false,
    icon: FileText,
    description: "Auto-generated documentation",
  },
  {
    label: "AI Confidence",
    value: "96",
    trend: "+1.1%",
    up: true,
    icon: Zap,
    description: "Aggregated agent certainty",
  },
]

export function RepoHealthOverview() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {METRICS.map((metric) => (
        <div
          key={metric.label}
          className="group relative overflow-hidden rounded-xl border border-white/5 bg-[#171717] p-5 transition-all hover:bg-[#1a1a1a]"
        >
          <div className="mb-4 flex items-center justify-between">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#69E300]/10 border border-[#69E300]/20 text-[#69E300]">
              <metric.icon className="h-5 w-5" />
            </div>
            <div
              className={cn(
                "flex items-center gap-1 text-[10px] font-bold px-2 py-1 rounded-md",
                metric.up ? "text-[#69E300] bg-[#69E300]/5" : "text-red-500 bg-red-500/5",
              )}
            >
              {metric.up ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
              {metric.trend}
            </div>
          </div>

          <div className="space-y-1">
            <h4 className="text-[11px] font-bold uppercase tracking-widest text-white/30">{metric.label}</h4>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black text-white group-hover:text-[#69E300] transition-colors">
                {metric.value}
              </span>
              {metric.label.includes("Health") || metric.label.includes("Confidence") ? (
                <span className="text-xs font-medium text-white/20">/ 100</span>
              ) : null}
            </div>
            <p className="text-[11px] font-medium text-white/40">{metric.description}</p>
          </div>

          <div className="mt-4 h-1 w-full overflow-hidden rounded-full bg-white/5">
            <div
              className="h-full bg-[#69E300] transition-all duration-1000 group-hover:shadow-[0_0_10px_rgba(105,227,0,0.5)]"
              style={{ width: `${metric.value.replace("%", "")}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}
