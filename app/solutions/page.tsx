import { Button } from "@/components/ui/button";
import { Laptop, Smartphone, Search, Cloud } from "lucide-react";

const solutions = [
    {
        title: "Développement Web Sur Mesure",
        description: "Des sites vitrines aux applications web complexes, nous développons des solutions robustes et évolutives.",
        icon: Laptop,
        features: ["React / Next.js", "Architecture Moderne", "Performance"]
    },
    {
        title: "Applications Mobiles",
        description: "Créez une expérience unique pour vos utilisateurs sur iOS et Android avec nos solutions cross-platform.",
        icon: Smartphone,
        features: ["React Native", "iOS & Android", "Expérience Fluide"]
    },
    {
        title: "SEO & Marketing Digital",
        description: "Améliorez votre visibilité en ligne et attirez plus de clients qualifiés grâce à nos stratégies SEO.",
        icon: Search,
        features: ["Audit SEO", "Optimisation de Contenu", "Google Ads"]
    },
    {
        title: "Solutions Cloud & DevOps",
        description: "Déployez, gérez et faites évoluer vos applications en toute sérénité sur le cloud.",
        icon: Cloud,
        features: ["AWS / Azure", "CI/CD", "Sécurité"]
    }
];

export default function SolutionsPage() {
    return (
        <div className="bg-white">
            {/* Header */}
            <section className="bg-slate-900 text-white py-20">
                <div className="container mx-auto px-4 text-center">
                    <h1 className="text-4xl md:text-5xl font-bold mb-6">Nos Solutions</h1>
                    <p className="text-xl text-slate-300 max-w-2xl mx-auto">
                        Une gamme complète de services pour répondre à tous vos défis numériques.
                    </p>
                </div>
            </section>

            {/* Solutions Grid */}
            <section className="py-20">
                <div className="container mx-auto px-4">
                    <div className="grid md:grid-cols-2 gap-8">
                        {solutions.map((solution, index) => {
                            const Icon = solution.icon;
                            return (
                                <div key={index} className="flex flex-col p-8 rounded-2xl border border-slate-200 hover:border-primary/50 hover:shadow-xl transition-all duration-300 group">
                                    <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center text-primary mb-6 group-hover:bg-primary group-hover:text-white transition-colors">
                                        <Icon className="h-7 w-7" />
                                    </div>
                                    <h3 className="text-2xl font-bold text-slate-900 mb-4">{solution.title}</h3>
                                    <p className="text-slate-600 mb-6 flex-grow">{solution.description}</p>
                                    <ul className="space-y-2 mb-8">
                                        {solution.features.map((feature, i) => (
                                            <li key={i} className="flex items-center text-sm text-slate-500">
                                                <div className="w-1.5 h-1.5 rounded-full bg-primary mr-2" />
                                                {feature}
                                            </li>
                                        ))}
                                    </ul>
                                    <Button variant="outline" className="w-full group-hover:bg-primary group-hover:text-white group-hover:border-primary">
                                        En savoir plus
                                    </Button>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </section>

            {/* Bottom CTA */}
            <section className="py-20 bg-slate-50">
                <div className="container mx-auto px-4 text-center">
                    <h2 className="text-3xl font-bold text-slate-900 mb-6">Un projet spécifique ?</h2>
                    <Button size="lg">Contactez-nous pour un devis gratuit</Button>
                </div>
            </section>
        </div>
    );
}
