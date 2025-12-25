import { GitBranch, AlertCircle, CheckCircle2 } from "lucide-react"

const REPOS = [
  { name: "ghostwriter-core", health: 98, status: "Clean", branch: "main", issues: 0 },
  { name: "adk-orchestrator", health: 92, status: "Review Required", branch: "develop", issues: 3 },
  { name: "weave-exporter", health: 100, status: "Protected", branch: "v2.0", issues: 0 },
  { name: "sandbox-runtime", health: 85, status: "Audit Active", branch: "feature/isolation", issues: 12 },
]

export function RepositoryGrid() {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
      {REPOS.map((repo) => (
        <div
          key={repo.name}
          className="group relative overflow-hidden rounded-xl border border-white/5 bg-[#171717] p-4 transition-all hover:border-[#69E300]/30 hover:shadow-[0_0_20px_rgba(105,227,0,0.1)]"
        >
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <h3 className="font-display font-semibold text-white group-hover:text-[#69E300] transition-colors">
                {repo.name}
              </h3>
              <div className="flex items-center gap-2 text-[11px] text-white/40">
                <GitBranch className="h-3 w-3" />
                {repo.branch}
              </div>
            </div>
            <div className="relative flex h-10 w-10 items-center justify-center">
              <svg className="h-full w-full rotate-[-90deg]">
                <circle
                  cx="20"
                  cy="20"
                  r="18"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                  className="text-white/5"
                />
                <circle
                  cx="20"
                  cy="20"
                  r="18"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeDasharray={2 * Math.PI * 18}
                  strokeDashoffset={2 * Math.PI * 18 * (1 - repo.health / 100)}
                  className="text-[#69E300]"
                />
              </svg>
              <span className="absolute text-[10px] font-bold text-white">{repo.health}%</span>
            </div>
          </div>

          <div className="mt-4 flex items-center justify-between border-t border-white/5 pt-3">
            <div className="flex items-center gap-1.5">
              {repo.issues > 0 ? (
                <AlertCircle className="h-3.5 w-3.5 text-yellow-500" />
              ) : (
                <CheckCircle2 className="h-3.5 w-3.5 text-[#69E300]" />
              )}
              <span className="text-[11px] font-medium text-white/60">{repo.status}</span>
            </div>
            <span className="text-[10px] text-white/30 uppercase tracking-tighter">{repo.issues} Findings</span>
          </div>
        </div>
      ))}
    </div>
  )
}
