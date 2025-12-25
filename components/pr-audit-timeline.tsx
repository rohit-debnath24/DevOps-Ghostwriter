"use client"

import { useState } from "react"
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ChevronDown,
  ChevronRight,
  User,
  Terminal,
  Shield,
  FileText,
  Zap,
} from "lucide-react"
import { cn } from "@/lib/utils"
import Link from "next/link"

const AUDITS = [
  {
    id: "PR-1284",
    title: "Implement zero-trust isolation for sandbox runtimes",
    author: "alexpine",
    timestamp: "2 hours ago",
    status: "passed",
    security: "No critical vulnerabilities found. 3 minor dependency updates recommended.",
    runtime: "All 142 integration tests passed in isolated environment.",
    docs: "Updated internal API documentation for sandbox isolation.",
    ghostwriter: "This PR significantly improves security posture without performance regression.",
  },
  {
    id: "PR-1282",
    title: "Refactor orchestrator state management",
    author: "sarah_dev",
    timestamp: "5 hours ago",
    status: "issues",
    security: "Potential race condition identified in state transition logic.",
    runtime: "Runtime validation failed on edge cases for concurrent requests.",
    docs: "State machine documentation out of sync with implementation.",
    ghostwriter: "I recommend addressing the concurrency issues before merging to maintain stability.",
  },
  {
    id: "PR-1279",
    title: "Add support for custom agent constraints",
    author: "mike_audit",
    timestamp: "1 day ago",
    status: "failed",
    security: "Input validation bypass detected in constraint parser.",
    runtime: "Critical crash during stress testing of large constraint sets.",
    docs: "No documentation updates found for new configuration options.",
    ghostwriter: "Blocking merge due to security bypass and runtime instability.",
  },
]

export function PRAuditTimeline() {
  const [expandedId, setExpandedId] = useState<string | null>("PR-1284")

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold tracking-tight text-white">Audit Timeline</h2>
        <div className="text-[11px] font-medium text-white/40 uppercase tracking-widest">Showing last 12 audits</div>
      </div>

      <div className="relative space-y-4 before:absolute before:left-[17px] before:top-2 before:h-[calc(100%-16px)] before:w-px before:bg-white/5">
        {AUDITS.map((audit) => (
          <div
            key={audit.id}
            className={cn(
              "group relative ml-8 rounded-xl border border-white/5 bg-[#171717] transition-all hover:border-white/10",
              expandedId === audit.id && "border-[#69E300]/30 shadow-[0_0_20px_rgba(105,227,0,0.05)]",
            )}
          >
            {/* Timeline Dot */}
            <div
              className={cn(
                "absolute -left-[27px] top-5 h-4 w-4 rounded-full border-4 border-[#0A0809] z-10",
                audit.status === "passed" && "bg-[#69E300]",
                audit.status === "issues" && "bg-yellow-500",
                audit.status === "failed" && "bg-red-500",
              )}
            />

            <div
              className="flex cursor-pointer items-center justify-between p-4"
              onClick={() => setExpandedId(expandedId === audit.id ? null : audit.id)}
            >
              <div className="flex items-center gap-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/5 border border-white/10">
                  <User className="h-4 w-4 text-white/60" />
                </div>
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-[#69E300]">{audit.id}</span>
                    <h3 className="font-semibold text-white transition-colors group-hover:text-[#69E300]">
                      {audit.title}
                    </h3>
                  </div>
                  <div className="flex items-center gap-3 text-[11px] text-white/40">
                    <span>by {audit.author}</span>
                    <span>•</span>
                    <span>{audit.timestamp}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div
                  className={cn(
                    "flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider",
                    audit.status === "passed" && "bg-[#69E300]/10 text-[#69E300]",
                    audit.status === "issues" && "bg-yellow-500/10 text-yellow-500",
                    audit.status === "failed" && "bg-red-500/10 text-red-500",
                  )}
                >
                  {audit.status === "passed" && <CheckCircle2 className="h-3 w-3" />}
                  {audit.status === "issues" && <AlertTriangle className="h-3 w-3" />}
                  {audit.status === "failed" && <XCircle className="h-3 w-3" />}
                  {audit.status}
                </div>
                {expandedId === audit.id ? (
                  <ChevronDown className="h-4 w-4 text-white/20" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-white/20" />
                )}
              </div>
            </div>

            {expandedId === audit.id && (
              <div className="border-t border-white/5 p-4 space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
                <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                  <div className="space-y-2 rounded-lg bg-black/20 p-3 border border-white/5">
                    <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-white/40">
                      <Shield className="h-3 w-3 text-[#69E300]" />
                      Security Finding
                    </div>
                    <p className="text-xs text-white/70 leading-relaxed">{audit.security}</p>
                  </div>
                  <div className="space-y-2 rounded-lg bg-black/20 p-3 border border-white/5">
                    <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-white/40">
                      <Terminal className="h-3 w-3 text-[#69E300]" />
                      Runtime Validation
                    </div>
                    <p className="text-xs text-white/70 leading-relaxed">{audit.runtime}</p>
                  </div>
                  <div className="space-y-2 rounded-lg bg-black/20 p-3 border border-white/5">
                    <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-white/40">
                      <FileText className="h-3 w-3 text-[#69E300]" />
                      Documentation
                    </div>
                    <p className="text-xs text-white/70 leading-relaxed">{audit.docs}</p>
                  </div>
                </div>

                <div className="rounded-lg bg-[#69E300]/5 p-4 border border-[#69E300]/10">
                  <div className="mb-2 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-[#69E300]">
                      <Zap className="h-3 w-3 fill-current" />
                      Ghostwriter Summary
                    </div>
                    <Link
                      href={`/audit/${audit.id}`}
                      className="text-[10px] font-bold uppercase tracking-wider text-white/40 hover:text-[#69E300] transition-colors"
                    >
                      View Full Trace →
                    </Link>
                  </div>
                  <p className="text-sm italic text-white/80 leading-relaxed">"{audit.ghostwriter}"</p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
