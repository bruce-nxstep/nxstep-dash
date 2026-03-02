import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export function HeroSection() {
    return (
        <section className="relative py-20 lg:py-32 overflow-hidden bg-slate-50">
            <div className="container mx-auto px-4 relative z-10">
                <div className="max-w-3xl mx-auto text-center">
                    <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-slate-900 mb-6">
                        Propulsez votre entreprise vers le <span className="text-primary">futur digital</span>
                    </h1>
                    <p className="text-lg md:text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
                        NXSTEP vous accompagne dans la transformation numérique de votre business avec des solutions sur mesure, performantes et élégantes.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Button size="lg" className="w-full sm:w-auto gap-2">
                            Commencer maintenant <ArrowRight className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="lg" className="w-full sm:w-auto">
                            Découvrir nos services
                        </Button>
                    </div>
                </div>
            </div>

            {/* Abstract Background Element */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-3xl -z-10" />
        </section>
    );
}
