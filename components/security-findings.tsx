import { Badge } from "@/components/ui/badge"
import { ShieldAlert, ExternalLink } from "lucide-react"

const FINDINGS = [
  {
    id: "SEC-001",
    severity: "Medium",
    title: "Insecure JWT Token Expiration",
    file: "src/middleware/auth.ts",
    line: 42,
    explanation:
      "JWT tokens are currently set to expire in 7 days. Industry standard for high-security applications recommends 15-60 minutes with refresh tokens.",
    fix: "Implement a short-lived access token (15m) and a secure HTTP-only refresh token.",
    impact: "Potential for long-term session hijacking if a token is intercepted.",
  },
  {
    id: "SEC-002",
    severity: "Low",
    title: "Informational Header Leakage",
    file: "src/server.ts",
    line: 15,
    explanation:
      "Server is exposing 'X-Powered-By' header, which reveals technology stack information to potential attackers.",
    fix: "Use helmet middleware to disable sensitive headers: app.disable('x-powered-by');",
    impact: "Provides reconnaissance data for targeted attacks.",
  },
]

export function SecurityFindings() {
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-300">
      <div className="flex items-center gap-2">
        <ShieldAlert className="h-5 w-5 text-[#69E300]" />
        <h3 className="text-sm font-bold text-[#F8F7F8] uppercase tracking-[0.2em]">Security Analysis</h3>
      </div>

      <div className="grid gap-4">
        {FINDINGS.map((finding) => (
          <div key={finding.id} className="rounded-xl border border-[#222122] bg-[#171717] overflow-hidden group">
            <div className="p-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                <div className="flex items-center gap-3">
                  <Badge
                    className={`
                    ${
                      finding.severity === "Critical"
                        ? "bg-red-500/10 text-red-500 border-red-500/20"
                        : finding.severity === "Medium"
                          ? "bg-yellow-500/10 text-yellow-500 border-yellow-500/20"
                          : "bg-blue-500/10 text-blue-500 border-blue-500/20"
                    } 
                    px-2 py-0 border font-bold uppercase text-[10px] tracking-widest
                  `}
                  >
                    {finding.severity}
                  </Badge>
                  <h4 className="text-lg font-bold text-[#F8F7F8] group-hover:text-[#69E300] transition-colors">
                    {finding.title}
                  </h4>
                </div>
                <div className="flex items-center gap-2 text-[11px] font-mono text-[#71717A]">
                  <span className="text-[#A1A1A1]">{finding.file}</span>
                  <span className="text-white/10">:</span>
                  <span>L{finding.line}</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-3">
                  <p className="text-xs font-bold text-[#A1A1A1] uppercase tracking-wider">Analysis</p>
                  <p className="text-sm text-[#F8F7F8] leading-relaxed">{finding.explanation}</p>
                </div>
                <div className="space-y-3">
                  <p className="text-xs font-bold text-[#A1A1A1] uppercase tracking-wider">Recommended Fix</p>
                  <div className="p-3 rounded-lg bg-[#0A0809] border border-[#222122] font-mono text-[12px] text-[#69E300]">
                    {finding.fix}
                  </div>
                </div>
              </div>
            </div>
            <div className="px-6 py-3 bg-[#202023] border-t border-[#262626] flex items-center justify-between">
              <p className="text-[11px] text-[#71717A]">
                Impact: <span className="text-[#A1A1A1]">{finding.impact}</span>
              </p>
              <button className="text-[11px] font-bold text-[#69E300] flex items-center gap-1 hover:underline">
                View trace details <ExternalLink className="h-3 w-3" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
