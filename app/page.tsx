import { HeroSection } from "@/components/hero-section"
import { FeaturesSection } from "@/components/features-section"
import { CTASection } from "@/components/cta-section"
import { HowItWorks } from "@/components/how-it-works"
import { AgentsSection } from "@/components/agents-section"
import { PricingSection } from "@/components/pricing-section"
import TestimonialCarousel from "@/components/testimonial-carousel"

export default function Home() {
  return (
    <div className="min-h-screen bg-[#0a0809] text-white selection:bg-[#69E300]/30">
      <main className="pt-16">
        <HeroSection />

        <section className="container mx-auto px-6 sm:px-8 lg:px-12 xl:px-16 py-20 max-w-[1400px]">
          <div className="space-y-32">
            {/* How It Works Section */}
            <HowItWorks />

            {/* Key Features Section */}
            <FeaturesSection />

            {/* Agents and Testimonials Section with reduced spacing */}
            <div className="space-y-16">
              {/* Agents Section */}
              <AgentsSection />

              {/* Pricing Section */}
              <PricingSection />

              {/* Testimonial Carousel Section */}
              <TestimonialCarousel />
            </div>
          </div>

          {/* CTA Section */}
          <div className="mt-8">
            <CTASection />
          </div>
        </section>
      </main>
    </div>
  )
}
