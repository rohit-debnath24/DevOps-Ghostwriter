import { Shield, Terminal, Zap, FileText } from "lucide-react"
import { cn } from "@/lib/utils"

const AGENTS = [
  { name: "Orchestrator Agent", icon: Zap, status: "Active", latency: "142ms" },
  { name: "Security Auditor", icon: Shield, status: "Idle", latency: "890ms" },
  { name: "Runtime Validator", icon: Terminal, status: "Active", latency: "1.2s" },
  { name: "Ghostwriter", icon: FileText, status: "Active", latency: "450ms" },
]

export function AgentActivitySummary() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold tracking-tight text-white">Agent Activity</h2>
      <div className="rounded-xl border border-white/5 bg-[#171717] divide-y divide-white/5">
        {AGENTS.map((agent) => (
          <div key={agent.name} className="flex items-center justify-between p-4 transition-all hover:bg-white/5">
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/5 border border-white/10 text-white/40 group-hover:text-[#69E300]">
                <agent.icon className="h-4 w-4" />
              </div>
              <div className="space-y-0.5">
                <div className="text-xs font-bold text-white">{agent.name}</div>
                <div className="flex items-center gap-2 text-[10px] text-white/40 uppercase tracking-widest">
                  Avg Latency: <span className="text-white/60 font-mono">{agent.latency}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase tracking-widest text-white/40">{agent.status}</span>
              <div
                className={cn(
                  "h-1.5 w-1.5 rounded-full",
                  agent.status === "Active" ? "bg-[#69E300] animate-pulse" : "bg-white/10",
                )}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-[#69E300]/20 bg-[#69E300]/5 p-5 transition-all hover:border-[#69E300]/40">
        <h3 className="mb-2 flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-[#69E300]">
          <Zap className="h-4 w-4 fill-current" />
          Observability Node
        </h3>
        <p className="mb-4 text-xs text-white/60 leading-relaxed">
          Every decision made by our specialized agents is traceable via Weights & Biases Weave. Access the full
          reasoning graph for absolute trust.
        </p>
        <button className="flex w-full items-center justify-center gap-2 rounded-lg bg-[#69E300] py-2.5 text-xs font-bold text-black transition-all hover:bg-[#5bc200] active:scale-[0.98]">
          View Full AI Reasoning Trace
          <ExternalLink className="h-3 w-3" />
        </button>
      </div>
    </div>
  )
}

function ExternalLink(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <polyline points="15 3 21 3 21 9" />
      <line x1="10" x2="21" y1="14" y2="3" />
    </svg>
  )
}
