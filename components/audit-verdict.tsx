import { ShieldCheck, FileText, CheckCircle2 } from "lucide-react"

export function AuditVerdict() {
  return (
    <div className="rounded-xl border border-[#222122] bg-[#171717] p-8 animate-in fade-in slide-in-from-top-4 duration-700 delay-100">
      <div className="grid grid-cols-1 md:grid-cols-12 gap-12 items-center">
        <div className="md:col-span-8 space-y-6">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-[#69E300]/10 flex items-center justify-center border border-[#69E300]/20">
              <CheckCircle2 className="h-6 w-6 text-[#69E300]" />
            </div>
            <h2 className="text-2xl font-bold text-[#F8F7F8]">✅ Logic Passed | 📝 Docs Updated</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="flex items-start gap-3 p-4 rounded-lg bg-[#0A0809] border border-[#222122]">
              <ShieldCheck className="h-5 w-5 text-[#69E300] shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="text-sm font-semibold text-[#F8F7F8]">Security Audit</p>
                <p className="text-xs text-[#A1A1A1]">0 vulnerabilities detected in updated files.</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 rounded-lg bg-[#0A0809] border border-[#222122]">
              <CheckCircle2 className="h-5 w-5 text-[#69E300] shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="text-sm font-semibold text-[#F8F7F8]">Runtime Tests</p>
                <p className="text-xs text-[#A1A1A1]">12 unit tests executed successfully.</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 rounded-lg bg-[#0A0809] border border-[#222122]">
              <FileText className="h-5 w-5 text-[#69E300] shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="text-sm font-semibold text-[#F8F7F8]">Docs Status</p>
                <p className="text-xs text-[#A1A1A1]">README and API docs auto-updated.</p>
              </div>
            </div>
          </div>
        </div>

        <div className="md:col-span-4 flex flex-col items-center justify-center p-6 rounded-xl bg-[#202023] border border-[#262626]">
          <div className="relative h-24 w-24">
            <svg className="h-full w-full transform -rotate-90">
              <circle
                cx="48"
                cy="48"
                r="40"
                stroke="currentColor"
                strokeWidth="8"
                fill="transparent"
                className="text-white/5"
              />
              <circle
                cx="48"
                cy="48"
                r="40"
                stroke="currentColor"
                strokeWidth="8"
                fill="transparent"
                strokeDasharray={251.2}
                strokeDashoffset={251.2 * (1 - 0.92)}
                className="text-[#69E300]"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-xl font-bold text-[#F8F7F8]">92%</span>
            </div>
          </div>
          <p className="mt-4 text-sm font-bold text-[#F8F7F8] uppercase tracking-widest">AI Confidence</p>
          <p className="text-xs text-[#A1A1A1] mt-1 italic">High Reliability Score</p>
        </div>
      </div>
    </div>
  )
}
