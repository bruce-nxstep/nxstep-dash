import { Button } from "@/components/ui/button";
import { ArrowRight, CheckCircle, Users, Target } from "lucide-react";

export default function AboutPage() {
    return (
        <div className="bg-white">
            {/* Hero Section */}
            <section className="py-20 bg-slate-50">
                <div className="container mx-auto px-4 text-center">
                    <h1 className="text-4xl font-bold text-slate-900 mb-6">À Propos de NXSTEP</h1>
                    <p className="text-xl text-slate-600 max-w-2xl mx-auto">
                        Nous sommes une agence digitale passionnée, dédiée à propulser les entreprises vers leur plein potentiel numérique.
                    </p>
                </div>
            </section>

            {/* Mission Section */}
            <section className="py-20">
                <div className="container mx-auto px-4 grid md:grid-cols-2 gap-12 items-center">
                    <div>
                        <h2 className="text-3xl font-bold text-slate-900 mb-6">Notre Mission</h2>
                        <p className="text-slate-600 mb-4 leading-relaxed">
                            Chez NXSTEP, notre mission est simple : démocratiser l&apos;excellence digitale. Nous croyons que chaque entreprise, quelle que soit sa taille, mérite des outils numériques performants, esthétiques et sécurisés.
                        </p>
                        <p className="text-slate-600 mb-6 leading-relaxed">
                            Nous combinons expertise technique et vision stratégique pour créer des solutions qui ne sont pas seulement belles, mais qui génèrent de vrais résultats commerciaux.
                        </p>
                        <ul className="space-y-3">
                            {[
                                "Innovation constante",
                                "Approche centrée sur l'utilisateur",
                                "Transparence et collaboration",
                                "Excellence technique"
                            ].map((item, index) => (
                                <li key={index} className="flex items-center space-x-2 text-slate-700">
                                    <CheckCircle className="h-5 w-5 text-primary" />
                                    <span>{item}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-primary/5 p-6 rounded-2xl">
                            <Users className="h-10 w-10 text-primary mb-4" />
                            <h3 className="text-4xl font-bold text-slate-900 mb-2">50+</h3>
                            <p className="text-slate-600">Clients satisfaits</p>
                        </div>
                        <div className="bg-blue-600 p-6 rounded-2xl text-white">
                            <Target className="h-10 w-10 text-white mb-4" />
                            <h3 className="text-4xl font-bold mb-2">100%</h3>
                            <p className="text-blue-100">Engagement</p>
                        </div>
                        {/* Placeholder placeholders for visual balance */}
                        <div className="bg-slate-100 p-6 rounded-2xl col-span-2 h-32 flex items-center justify-center text-slate-400">
                            Image d'équipe / Bureau
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 bg-slate-900 text-white text-center">
                <div className="container mx-auto px-4">
                    <h2 className="text-3xl font-bold mb-6">Prêt à travailler avec nous ?</h2>
                    <p className="text-slate-300 max-w-2xl mx-auto mb-8">
                        Discutons de votre projet et voyons comment nous pouvons vous aider à atteindre vos objectifs.
                    </p>
                    <Button size="lg" variant="default" className="bg-white text-slate-900 hover:bg-slate-100">
                        Contactez-nous <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            </section>
        </div>
    );
}
