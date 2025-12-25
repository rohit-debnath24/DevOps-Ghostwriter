"use client"

import { useState, useEffect, useRef } from "react"
import { Terminal, Cpu, Shield, Code, BookOpen, Activity } from "lucide-react"

const AGENTS = [
  { id: "orchestrator", name: "Orchestrator Agent", icon: Cpu, time: "14:20:01", duration: "1.2s", toolCount: 4 },
  { id: "security", name: "Security Auditor", icon: Shield, time: "14:20:03", duration: "4.5s", toolCount: 12 },
  { id: "runtime", name: "Runtime Validator", icon: Code, time: "14:20:08", duration: "8.1s", toolCount: 8 },
  { id: "ghostwriter", name: "Ghostwriter", icon: BookOpen, time: "14:20:17", duration: "2.4s", toolCount: 3 },
]

const LOGS = [
  { agent: "orchestrator", text: "> Initializing ADK Agent Cluster...", type: "system" },
  { agent: "orchestrator", text: "> Context loaded. Analyzing PR #842...", type: "thought" },
  { agent: "security", text: "> Security Auditor dispatched. Tools: [semgrep, trivy, snyk]", type: "system" },
  { agent: "security", text: "> Scanning files for sensitive patterns...", type: "thought" },
  { agent: "security", text: "> Semgrep scan complete. No critical issues found.", type: "success" },
  { agent: "runtime", text: "> Runtime Validator spinning up sandbox...", type: "system" },
  { agent: "runtime", text: "> Executing: npm test -- --coverage", type: "code" },
  { agent: "runtime", text: "PASS  src/middleware/auth.test.ts (2.4s)", type: "output" },
  { agent: "runtime", text: "PASS  src/utils/token.test.ts (1.8s)", type: "output" },
  { agent: "ghostwriter", text: "> Documentation update required for API change.", type: "thought" },
  { agent: "ghostwriter", text: "> Patching README.md with new endpoint signatures...", type: "system" },
  { agent: "orchestrator", text: "> All agents completed. Finalizing verdict.", type: "system" },
]

export function AuditConsole() {
  const [activeAgentId, setActiveAgentId] = useState("orchestrator")
  const [visibleLogs, setVisibleLogs] = useState<number[]>([])
  const terminalRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let index = 0
    const interval = setInterval(() => {
      if (index < LOGS.length) {
        setVisibleLogs((prev) => [...prev, index])
        const currentLog = LOGS[index]
        if (currentLog) setActiveAgentId(currentLog.agent)
        index++
      } else {
        clearInterval(interval)
      }
    }, 1200)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [visibleLogs])

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-0 rounded-xl border border-[#222122] bg-[#171717] overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200">
      {/* Left - Agent Timeline */}
      <div className="lg:col-span-4 border-r border-[#222122] p-6 space-y-6">
        <div className="flex items-center gap-2 mb-8">
          <Activity className="h-4 w-4 text-[#69E300]" />
          <h3 className="text-xs font-bold text-[#F8F7F8] uppercase tracking-[0.2em]">Agent Execution</h3>
        </div>

        <div className="space-y-4">
          {AGENTS.map((agent) => {
            const isActive = activeAgentId === agent.id
            const Icon = agent.icon
            return (
              <div
                key={agent.id}
                className={`relative flex items-center justify-between p-4 rounded-lg border transition-all duration-300 ${
                  isActive ? "bg-[#69E300]/5 border-[#69E300]/30" : "bg-[#0A0809] border-[#222122] opacity-60"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`h-8 w-8 rounded-md flex items-center justify-center ${isActive ? "bg-[#69E300] text-black" : "bg-[#202023] text-[#A1A1A1]"}`}
                  >
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="space-y-0.5">
                    <p className={`text-sm font-bold ${isActive ? "text-[#F8F7F8]" : "text-[#A1A1A1]"}`}>
                      {agent.name}
                    </p>
                    <p className="text-[10px] text-[#71717A] uppercase tracking-widest">{agent.time}</p>
                  </div>
                </div>
                {isActive && <div className="h-2 w-2 rounded-full bg-[#69E300] animate-pulse" />}
                <div className="text-right">
                  <p className="text-[10px] text-[#A1A1A1] font-mono">{agent.duration}</p>
                  <p className="text-[9px] text-[#71717A] uppercase tracking-tighter">{agent.toolCount} tools</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Right - Terminal Log Panel */}
      <div className="lg:col-span-8 flex flex-col bg-[#0A0809]">
        <div className="flex items-center justify-between px-6 py-3 border-b border-[#222122] bg-[#171717]">
          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-[#A1A1A1]" />
            <span className="text-[10px] font-bold text-[#A1A1A1] uppercase tracking-[0.2em]">Live Execution Logs</span>
          </div>
          <div className="flex gap-1.5">
            <div className="h-2 w-2 rounded-full bg-white/5" />
            <div className="h-2 w-2 rounded-full bg-white/5" />
            <div className="h-2 w-2 rounded-full bg-white/5" />
          </div>
        </div>

        <div
          ref={terminalRef}
          className="h-[500px] overflow-y-auto p-8 font-mono text-[13px] leading-relaxed scrollbar-thin scrollbar-thumb-white/10"
        >
          {visibleLogs.map((logIndex) => {
            const log = LOGS[logIndex]
            if (!log) return null
            return (
              <div
                key={logIndex}
                className={`mb-3 flex gap-4 animate-in fade-in slide-in-from-left-2 duration-300 ${
                  log.type === "thought"
                    ? "text-[#A1A1A1] italic"
                    : log.type === "success"
                      ? "text-[#69E300]"
                      : log.type === "code"
                        ? "text-[#0069E2]"
                        : log.type === "output"
                          ? "text-white/60"
                          : "text-[#F8F7F8]"
                }`}
              >
                <span className="shrink-0 text-white/10 select-none">[{logIndex.toString().padStart(3, "0")}]</span>
                <span className="break-all">{log.text}</span>
              </div>
            )
          })}
          <div className="h-4 w-2 bg-[#69E300] inline-block animate-pulse ml-1" />
        </div>
      </div>
    </div>
  )
}
