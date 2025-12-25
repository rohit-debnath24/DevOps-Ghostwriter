import { Badge } from "@/components/ui/badge"
import { Clock, Database, FileText, Clipboard } from "lucide-react"

export function AuditDetails() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-400">
      {/* Runtime Validation */}
      <div className="lg:col-span-7 space-y-6">
        <div className="flex items-center gap-2">
          <Database className="h-5 w-5 text-[#69E300]" />
          <h3 className="text-sm font-bold text-[#F8F7F8] uppercase tracking-[0.2em]">Runtime Validation</h3>
        </div>

        <div className="rounded-xl border border-[#222122] bg-[#171717] overflow-hidden">
          <div className="p-6 border-b border-[#222122]">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Badge className="bg-[#69E300]/10 text-[#69E300] border-[#69E300]/20 font-bold text-[10px] tracking-widest uppercase">
                  Pass
                </Badge>
                <h4 className="font-bold text-[#F8F7F8]">Test Suite Execution</h4>
              </div>
              <div className="flex items-center gap-2 text-[11px] text-[#A1A1A1]">
                <Clock className="h-3 w-3" />
                <span>8.1s execution time</span>
              </div>
            </div>
            <p className="text-sm text-[#A1A1A1] italic mb-4">
              "Executed in ADK isolated sandbox environments (Node 18.x)"
            </p>
            <div className="rounded-lg bg-[#0A0809] border border-[#222122] p-4 font-mono text-[12px] text-[#F8F7F8] space-y-1">
              <p className="text-white/20">Running tests...</p>
              <p>✓ Authentication middleware handles expired tokens</p>
              <p>✓ Refresh token rotation succeeds</p>
              <p>✓ API response includes correct security headers</p>
              <p className="text-[#69E300] pt-2">Result: 12 passed, 0 failed, 12 total</p>
            </div>
          </div>
        </div>
      </div>

      {/* Ghostwriter Documentation */}
      <div className="lg:col-span-5 space-y-6">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-[#69E300]" />
          <h3 className="text-sm font-bold text-[#F8F7F8] uppercase tracking-[0.2em]">Ghostwriter Output</h3>
        </div>

        <div className="rounded-xl border border-[#222122] bg-[#171717] overflow-hidden">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-bold text-[#F8F7F8]">Generated PR Comment</h4>
              <button className="text-[#A1A1A1] hover:text-[#69E300] transition-colors">
                <Clipboard className="h-4 w-4" />
              </button>
            </div>
            <div className="rounded-lg bg-[#0A0809] border border-[#222122] p-4 font-mono text-[11px] text-[#A1A1A1] space-y-3 prose prose-invert max-w-none">
              <p className="font-bold text-[#F8F7F8]">## AI Audit Summary</p>
              <p>Ghostwriter has reviewed your changes to authentication middleware. </p>
              <p className="text-[#69E300]">✓ Security: Verified OWASP compliance for session handling.</p>
              <p>✓ Tests: Coverage maintained at 94%.</p>
              <p>✓ Docs: API signature changes synced to /docs/api-auth.md.</p>
            </div>
            <button className="w-full mt-6 py-2 rounded-lg bg-[#202023] border border-[#262626] text-[11px] font-bold text-[#F8F7F8] hover:border-[#69E300] transition-colors">
              Preview README Diffs
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
