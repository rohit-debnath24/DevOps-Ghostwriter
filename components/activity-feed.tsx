import { Terminal, Shield, FileText, CheckCircle2 } from "lucide-react"

const ACTIVITIES = [
  {
    id: 1,
    agent: "SecurityAuditor",
    action: "identified vulnerability in next-auth session handling",
    repo: "ghostwriter-core",
    time: "2m ago",
    icon: Shield,
    type: "critical",
  },
  {
    id: 2,
    agent: "DocWriter",
    action: "generated technical specification for API v2",
    repo: "adk-orchestrator",
    time: "15m ago",
    icon: FileText,
    type: "info",
  },
  {
    id: 3,
    agent: "CodeReviewer",
    action: "approved and merged PR #142 into main",
    repo: "weave-exporter",
    time: "42m ago",
    icon: CheckCircle2,
    type: "success",
  },
  {
    id: 4,
    agent: "SandboxRunner",
    action: "successfully executed isolation test suite",
    repo: "sandbox-runtime",
    time: "1h ago",
    icon: Terminal,
    type: "success",
  },
]

export function ActivityFeed() {
  return (
    <div className="space-y-4">
      {ACTIVITIES.map((activity) => (
        <div
          key={activity.id}
          className="flex items-start gap-4 rounded-xl border border-white/5 bg-[#171717] p-4 transition-all hover:bg-[#1a1a1a]"
        >
          <div
            className={`mt-0.5 flex h-8 w-8 items-center justify-center rounded-lg border ${
              activity.type === "critical"
                ? "bg-red-500/10 border-red-500/20 text-red-500"
                : activity.type === "success"
                  ? "bg-[#69E300]/10 border-[#69E300]/20 text-[#69E300]"
                  : "bg-blue-500/10 border-blue-500/20 text-blue-500"
            }`}
          >
            <activity.icon className="h-4 w-4" />
          </div>
          <div className="flex-1 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-white">{activity.agent}</span>
              <span className="text-[10px] font-medium text-white/20 uppercase tracking-widest">{activity.time}</span>
            </div>
            <p className="text-sm text-white/60">
              {activity.action} on <span className="text-white/80 font-medium">{activity.repo}</span>
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}
