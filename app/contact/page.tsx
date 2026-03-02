import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Mail, MapPin, Phone, Send } from "lucide-react";

export default function ContactPage() {
    return (
        <div className="bg-white py-20">
            <div className="container mx-auto px-4">
                <div className="text-center mb-16">
                    <h1 className="text-4xl font-bold text-slate-900 mb-4">Contactez-nous</h1>
                    <p className="text-slate-600 max-w-2xl mx-auto">
                        Vous avez un projet en tête ? Une question ? Notre équipe est là pour vous répondre.
                    </p>
                </div>

                <div className="grid md:grid-cols-3 gap-12 max-w-6xl mx-auto">
                    {/* Contact Info */}
                    <div className="md:col-span-1 space-y-8">
                        <div className="flex items-start space-x-4">
                            <div className="bg-primary/10 p-3 rounded-lg text-primary">
                                <Mail className="h-6 w-6" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-900">Email</h3>
                                <p className="text-slate-600">contact@nxstep.com</p>
                                <p className="text-slate-600">support@nxstep.com</p>
                            </div>
                        </div>

                        <div className="flex items-start space-x-4">
                            <div className="bg-primary/10 p-3 rounded-lg text-primary">
                                <Phone className="h-6 w-6" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-900">Téléphone</h3>
                                <p className="text-slate-600">+33 1 23 45 67 89</p>
                                <p className="text-sm text-slate-500">Du Lundi au Vendredi, 9h-18h</p>
                            </div>
                        </div>

                        <div className="flex items-start space-x-4">
                            <div className="bg-primary/10 p-3 rounded-lg text-primary">
                                <MapPin className="h-6 w-6" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-900">Bureau</h3>
                                <p className="text-slate-600">123 Avenue du Numérique</p>
                                <p className="text-slate-600">75000 Paris, France</p>
                            </div>
                        </div>
                    </div>

                    {/* Contact Form */}
                    <div className="md:col-span-2 bg-slate-50 p-8 rounded-2xl border border-slate-100">
                        <form className="space-y-6">
                            <div className="grid md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <Label htmlFor="firstname">Prénom</Label>
                                    <Input id="firstname" placeholder="Jean" />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="lastname">Nom</Label>
                                    <Input id="lastname" placeholder="Dupont" />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <Input id="email" type="email" placeholder="jean.dupont@exemple.com" />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="message">Message</Label>
                                <Textarea id="message" placeholder="Dites-nous en plus sur votre projet..." className="min-h-[150px]" />
                            </div>

                            <Button type="submit" className="w-full md:w-auto">
                                Envoyer le message <Send className="ml-2 h-4 w-4" />
                            </Button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}
