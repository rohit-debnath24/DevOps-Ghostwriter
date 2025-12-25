import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Github, RotateCcw, ChevronLeft } from "lucide-react"
import Link from "next/link"

interface AuditHeaderProps {
  prId: string
}

export function AuditHeader({ prId }: AuditHeaderProps) {
  return (
    <div className="flex flex-col gap-6 border-b border-[#222122] pb-8 animate-in fade-in slide-in-from-top-4 duration-700">
      <div className="flex items-center gap-2 text-sm text-[#A1A1A1]">
        <Link href="/repositories" className="hover:text-[#69E300] transition-colors flex items-center gap-1">
          <ChevronLeft className="h-4 w-4" />
          Back to Repository
        </Link>
      </div>

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-start gap-4">
          <Avatar className="h-12 w-12 border border-white/10">
            <AvatarImage src="/diverse-user-avatars.png" />
            <AvatarFallback>JD</AvatarFallback>
          </Avatar>
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-display font-bold text-[#F8F7F8] tracking-tight">
                Update authentication middleware
              </h1>
              <Badge className="bg-[#171717] text-[#A1A1A1] border-[#222122] hover:bg-[#171717]">#{prId}</Badge>
            </div>
            <div className="flex items-center gap-3 text-sm text-[#71717A]">
              <span className="font-medium text-[#A1A1A1]">ghostwriter-core</span>
              <span>•</span>
              <span>
                Opened by <span className="text-[#F8F7F8]">jane_dev</span>
              </span>
              <span>•</span>
              <span>2 hours ago</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#69E300]/10 border border-[#69E300]/20 mr-2">
            <div className="h-2 w-2 rounded-full bg-[#69E300] animate-pulse" />
            <span className="text-xs font-bold text-[#69E300] uppercase tracking-wider">Passed</span>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="border-[#222122] bg-transparent text-[#F8F7F8] hover:bg-[#171717] hover:text-[#69E300]"
          >
            <RotateCcw className="mr-2 h-4 w-4" />
            Re-run Audit
          </Button>
          <Button size="sm" className="bg-[#F8F7F8] text-black hover:bg-[#F8F7F8]/90 font-semibold">
            <Github className="mr-2 h-4 w-4" />
            View on GitHub
          </Button>
        </div>
      </div>
    </div>
  )
}
