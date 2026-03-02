import { Rocket, Shield, Zap, Globe, LineChart, Code, LucideIcon } from "lucide-react";

interface Feature {
    title: string;
    description: string;
    icon: LucideIcon;
}

const features: Feature[] = [
    {
        title: "Performance Maximale",
        description: "Des sites web optimisés pour une vitesse de chargement de premier ordre et une expérience utilisateur fluide.",
        icon: Zap,
    },
    {
        title: "Sécurité Avancée",
        description: "Protection de vos données et de celles de vos utilisateurs avec les normes de sécurité les plus strictes.",
        icon: Shield,
    },
    {
        title: "Innovation Continue",
        description: "Utilisation des dernières technologies pour garder une longueur d&apos;avance sur vos concurrents.",
        icon: Rocket,
    },
    {
        title: "Design Sur Mesure",
        description: "Une identité visuelle unique qui reflète parfaitement les valeurs de votre marque.",
        icon: Code,
    },
    {
        title: "Stratégie Digitale",
        description: "Accompagnement complet pour définir et atteindre vos objectifs commerciaux en ligne.",
        icon: LineChart,
    },
    {
        title: "Portée Internationale",
        description: "Solutions adaptées pour toucher votre audience, où qu&apos;elle soit dans le monde.",
        icon: Globe,
    },
];

export function FeatureSection() {
    return (
        <section className="py-32 bg-white relative">
            <div className="container mx-auto px-6">
                <div className="text-center mb-20">
                    <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6 tracking-tight">Pourquoi choisir NXSTEP ?</h2>
                    <p className="text-xl text-slate-500 max-w-3xl mx-auto font-light">
                        Nous combinons ingénierie de pointe et vision stratégique pour créer des automatisations qui impactent directement votre rentabilité.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {features.map((feature, index) => {
                        const Icon = feature.icon;
                        return (
                            <div key={index} className="group p-8 rounded-3xl border border-slate-100 bg-white hover:border-primary/30 shadow-sm hover:shadow-2xl hover:shadow-primary/10 transition-all duration-300 hover:-translate-y-2 relative overflow-hidden cursor-default">
                                <div className="absolute top-0 right-0 p-8 opacity-0 group-hover:opacity-10 transition-opacity duration-300 transform translate-x-1/4 -translate-y-1/4">
                                    <Icon className="w-24 h-24 text-primary" />
                                </div>

                                <div className="w-14 h-14 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-center mb-6 text-slate-900 group-hover:bg-primary group-hover:text-white group-hover:border-primary transition-colors duration-300 shadow-sm">
                                    <Icon className="h-7 w-7" />
                                </div>

                                <h3 className="text-2xl font-bold mb-3 text-slate-900 tracking-tight group-hover:text-primary transition-colors duration-300">{feature.title}</h3>
                                <p className="text-slate-600 leading-relaxed font-light">{feature.description}</p>
                            </div>
                        );
                    })}
                </div>
            </div>
        </section>
    );
}
