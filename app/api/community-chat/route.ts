import { NextResponse } from 'next/server';

const JOY_SYSTEM_PROMPT = `Tu t'appelles Joy, la Community Manager de l'agence NXSTEP. Tu es une experte en stratégie de contenu LinkedIn.
Ton rôle est d'aider l'utilisateur à créer et organiser sa présence sur LinkedIn via des posts classiques et des carrousels (max 10 images).

Règles :
- Si l'utilisateur a une idée vague, note-la et propose une structure.
- Si l'utilisateur parle d'un carrousel, suggère une structure en slides et rappelle la limite de 10 images.
- Tu es créative, enthousiaste et tu as un oeil pour le storytelling impactant.
- Réponds toujours en français.
- Donne des conseils concrets et actionnables.
- Propose des hashtags pertinents.
- Quand tu proposes un post, formate-le proprement avec des emojis et une structure claire.

Tu peux aussi aider à :
- Planifier un calendrier éditorial sur la semaine ou le mois
- Rédiger des posts engageants (hook, storytelling, CTA)
- Structurer des carrousels LinkedIn
- Optimiser les meilleurs horaires de publication`;

export async function POST(request: Request) {
    try {
        const { message, history } = await request.json();

        // Determine which AI provider to use
        const activeProvider = process.env.ACTIVE_LLM_PROVIDER || 'OpenAI';
        let apiUrl: string;
        let apiKey: string | undefined;
        let model: string;

        if (activeProvider.includes('Google') || activeProvider.includes('Gemini')) {
            apiKey = process.env.GEMINI_API_KEY;
            apiUrl = 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions';
            model = 'gemini-2.0-flash';
        } else {
            apiKey = process.env.OPENAI_API_KEY;
            apiUrl = 'https://api.openai.com/v1/chat/completions';
            model = 'gpt-4o';
        }

        if (!apiKey) {
            return NextResponse.json({ error: 'No API key configured' }, { status: 500 });
        }

        // Build messages array
        const messages = [
            { role: 'system', content: JOY_SYSTEM_PROMPT },
            ...(history || []).map((m: { role: string; content: string }) => ({
                role: m.role,
                content: m.content,
            })),
            { role: 'user', content: message },
        ];

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`,
            },
            body: JSON.stringify({
                model,
                messages,
                temperature: 0.7,
            }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('AI API error:', errorText);
            return NextResponse.json({ error: 'AI API error' }, { status: 502 });
        }

        const data = await response.json();
        const reply = data.choices?.[0]?.message?.content || 'Désolé, je n\'ai pas pu générer de réponse.';

        return NextResponse.json({ response: reply });
    } catch (error) {
        console.error('Community chat error:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
