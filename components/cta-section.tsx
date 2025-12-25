import { Button } from "@/components/ui/button"
import { ArrowRight, Play } from "lucide-react"

export function CTASection() {
  return (
    <div className="relative overflow-hidden rounded-3xl border border-[#69E300]/20 bg-[#69E300]/5 px-6 sm:px-12 md:px-16 lg:px-20 py-20 text-center">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 h-px w-3/4 bg-gradient-to-r from-transparent via-[#69E300]/50 to-transparent" />

      <div className="relative z-10 max-w-3xl mx-auto space-y-8">
        <div className="inline-flex items-center gap-2 rounded-full border border-[#69E300]/20 bg-[#69E300]/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-[#69E300]">
          Now in Private Beta
        </div>

        <h2 className="text-4xl font-bold tracking-tight sm:text-6xl text-balance">
          Automate your infrastructure at the speed of thought
        </h2>

        <p className="text-lg text-white/60 leading-relaxed text-pretty">
          Empower your entire organization to create, audit, and deploy at the speed of thought, while ensuring security
          remains at the forefront.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Button
            size="lg"
            className="h-14 px-8 rounded-full bg-white text-black hover:bg-white/90 font-bold text-base"
          >
            Request Early Access
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="h-14 px-8 rounded-full border-white/10 bg-white/5 hover:bg-white/10 font-bold text-base group"
          >
            <div className="mr-2 flex h-6 w-6 items-center justify-center rounded-full bg-white/10 transition-colors group-hover:bg-[#69E300] group-hover:text-black">
              <Play className="h-3 w-3 fill-current" />
            </div>
            Watch Technical Demo
          </Button>
        </div>
      </div>

      {/* Background Decorative Element */}
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_50%_120%,rgba(105,227,0,0.1),transparent_70%)]" />
    </div>
  )
}
