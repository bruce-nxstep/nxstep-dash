import Link from "next/link";
import { Facebook, Twitter, Linkedin, Mail, MapPin, Phone } from "lucide-react";

export function Footer() {
    return (
        <footer className="bg-slate-50 border-t border-slate-200">
            <div className="container mx-auto px-6 py-12 md:py-20">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
                    {/* Brand */}
                    <div className="space-y-6">
                        <h3 className="text-2xl font-bold text-slate-900 tracking-tight">NXSTEP<span className="text-primary">.</span></h3>
                        <p className="text-sm text-slate-500 leading-relaxed font-light max-w-xs">
                            Transformez votre entreprise avec nos solutions digitales innovantes. L&apos;excellence opérationnelle à portée de main.
                        </p>
                        <div className="flex space-x-5">
                            <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-300">
                                <Linkedin className="h-5 w-5" />
                            </Link>
                            <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-300">
                                <Twitter className="h-5 w-5" />
                            </Link>
                            <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-300">
                                <Facebook className="h-5 w-5" />
                            </Link>
                        </div>
                    </div>

                    {/* Links */}
                    <div>
                        <h4 className="font-bold mb-6 text-slate-900">Entreprise</h4>
                        <ul className="space-y-4 text-sm text-slate-500 font-light">
                            <li><Link href="/about" className="hover:text-primary transition-colors">À Propos</Link></li>
                            <li><Link href="/careers" className="hover:text-primary transition-colors">Carrières</Link></li>
                            <li><Link href="/blog" className="hover:text-primary transition-colors">Blog</Link></li>
                            <li><Link href="/contact" className="hover:text-primary transition-colors">Contact</Link></li>
                        </ul>
                    </div>

                    {/* Services */}
                    <div>
                        <h4 className="font-bold mb-6 text-slate-900">Services</h4>
                        <ul className="space-y-4 text-sm text-slate-500 font-light">
                            <li><Link href="#" className="hover:text-primary transition-colors">Développement Web</Link></li>
                            <li><Link href="#" className="hover:text-primary transition-colors">Stratégie Digitale</Link></li>
                            <li><Link href="#" className="hover:text-primary transition-colors">UX/UI Design</Link></li>
                            <li><Link href="#" className="hover:text-primary transition-colors">Cloud Solutions</Link></li>
                        </ul>
                    </div>

                    {/* Contact */}
                    <div>
                        <h4 className="font-bold mb-6 text-slate-900">Contact</h4>
                        <ul className="space-y-4 text-sm text-slate-500 font-light">
                            <li className="flex items-center space-x-3">
                                <Mail className="h-4 w-4 text-primary" />
                                <span>contact@nxstep.com</span>
                            </li>
                            <li className="flex items-center space-x-3">
                                <Phone className="h-4 w-4 text-primary" />
                                <span>+33 1 23 45 67 89</span>
                            </li>
                            <li className="flex items-center space-x-3">
                                <MapPin className="h-4 w-4 text-primary" />
                                <span>Paris, France</span>
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="pt-8 border-t border-slate-200 flex flex-col md:flex-row justify-between items-center text-xs text-slate-400 font-light">
                    <p>© {new Date().getFullYear()} NXSTEP. Tous droits réservés.</p>
                    <div className="flex space-x-6 mt-4 md:mt-0">
                        <Link href="#" className="hover:text-slate-600 transition-colors">Confidentialité</Link>
                        <Link href="#" className="hover:text-slate-600 transition-colors">CGU</Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
