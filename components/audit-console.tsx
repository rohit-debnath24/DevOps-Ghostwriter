"use client"

import { Terminal, ChevronRight } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MarkdownRenderer } from "@/components/markdown-renderer"

interface AuditConsoleProps {
  data: any
}

export function AuditConsole({ data }: AuditConsoleProps) {
  // Use real data or fallback
  // Use real data or fallback
  const diffSnippet = data?.diff || "No diff data available."
  const agentOutput = data?.result?.comment || "Waiting for agent output..."
  const status = data?.result?.status || "Unknown"

  return (
    <div className="rounded-xl border border-[#333] bg-[#0A0809] overflow-hidden shadow-2xl">
      {/* Terminal Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-[#1A1A1A] border-b border-[#333]">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
            <div className="w-3 h-3 rounded-full bg-green-500/80" />
          </div>
          <span className="ml-3 text-xs text-white/40 font-mono">agent-engine-v2.0.exe</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-[#69E300] font-mono animate-pulse">● LIVE CONNECTION</span>
        </div>
      </div>

      {/* Terminal Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 h-[400px]">
        {/* Left: Input (Diff) */}
        <div className="border-r border-[#333] p-0 flex flex-col">
          <div className="px-4 py-2 border-b border-[#333] bg-[#111]">
            <span className="text-xs text-white/50 font-bold uppercase tracking-wider">Input Context: Git Diff</span>
          </div>
          <div className="flex-1 p-4 bg-[#0F0F0F] overflow-y-auto scrollbar-thin scrollbar-thumb-white/10">
            <pre className="text-xs font-mono text-white/70 leading-relaxed whitespace-pre-wrap">
              {diffSnippet}
            </pre>
          </div>
        </div>

        {/* Right: Output (Reasoning) */}
        <div className="flex flex-col bg-black/50">
          <div className="px-4 py-2 border-b border-[#333] bg-[#111] flex justify-between">
            <span className="text-xs text-white/50 font-bold uppercase tracking-wider">Agent Reasoning Output</span>
            <span className="text-xs text-[#69E300]">{status.toUpperCase()}</span>
          </div>
          <div className="flex-1 p-4 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10">
            <div className="space-y-2 font-mono text-sm">
              <div className="flex gap-2 text-white/40">
                <ChevronRight className="h-4 w-4 shrink-0 mt-0.5" />
                <span>Initializing multi-agent swarm...</span>
              </div>
              <div className="flex gap-2 text-white/40">
                <ChevronRight className="h-4 w-4 shrink-0 mt-0.5" />
                <span>Analyzing logic flows...</span>
              </div>
              <div className="mt-4 pt-4 border-t border-white/5">
                <span className="text-[#69E300] font-bold block mb-2">{">"} FINAL FINDINGS:</span>
                <div className="prose prose-invert prose-sm text-white/80 max-w-none">
                  <MarkdownRenderer content={agentOutput} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
