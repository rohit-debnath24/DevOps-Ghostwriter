import { ExternalLink, Play } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

interface RepoHeaderProps {
  id: string
}

export function RepoHeader({ id }: RepoHeaderProps) {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h1 className="font-display text-2xl font-bold text-white">{id}</h1>
            <div className="flex items-center gap-1.5 rounded-full bg-[#69E300]/10 px-2 py-0.5 border border-[#69E300]/20">
              <div className="h-1.5 w-1.5 rounded-full bg-[#69E300] animate-pulse" />
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#69E300]">Connected</span>
            </div>
          </div>
          <p className="text-sm text-white/40">
            Organization: <span className="text-white/60">ghostwriter-ai</span> • Branch:{" "}
            <span className="font-mono text-white/60">main</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            className="border-white/10 bg-white/5 text-white hover:bg-white/10"
            asChild
          >
            <Link href={`https://github.com/ghostwriter-ai/${id}`} target="_blank">
              <ExternalLink className="mr-2 h-4 w-4" />
              View on GitHub
            </Link>
          </Button>
          <Button size="sm" className="bg-[#69E300] text-black hover:bg-[#5bc200] font-bold">
            <Play className="mr-2 h-4 w-4 fill-current" />
            Trigger Manual Audit
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-x-8 gap-y-2 border-y border-white/5 py-3">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold uppercase tracking-widest text-white/20">Last Scanned</span>
          <span className="text-xs font-medium text-white/60">14 minutes ago</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold uppercase tracking-widest text-white/20">Total PRs</span>
          <span className="text-xs font-medium text-white/60">142 analyzed</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold uppercase tracking-widest text-white/20">Active Agents</span>
          <span className="text-xs font-medium text-white/60">4 specialized units</span>
        </div>
      </div>
    </div>
  )
}
