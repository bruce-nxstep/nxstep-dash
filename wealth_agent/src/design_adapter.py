import os
import re
from dotenv import load_dotenv

try:
    from openai import OpenAI
    _HAS_OPENAI = True
except ImportError:
    _HAS_OPENAI = False


class DesignAdapter:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI() if _HAS_OPENAI else None
        self._globals_css_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'app', 'globals.css'
        )
        self.css_content = self._read_global_css()

    def _read_global_css(self) -> str:
        """Reads the global CSS file to get variable names."""
        try:
            if os.path.exists(self._globals_css_path):
                with open(self._globals_css_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""
        except Exception as e:
            print(f"Error reading globals.css: {e}")
            return ""

    def _build_token_style_block(self) -> str:
        """
        Parses globals.css and returns a <style>:root{...}</style> block
        containing every --variable: value pair found in the file.
        This is injected into every Stitch-generated page so that
        var(--radius-xl), var(--color-primary), etc. always resolve.
        """
        css_content = self._read_global_css()
        vars_lines = []
        seen = set()
        for m in re.finditer(r'(--[\w-]+)\s*:\s*([^;\n]+);', css_content):
            var, val = m.group(1).strip(), m.group(2).strip()
            if var not in seen:
                seen.add(var)
                vars_lines.append(f"    {var}: {val};")

        if not vars_lines:
            return ""

        vars_block = "\n".join(vars_lines)
        return f"""<style>
/* ── Design System Tokens (auto-injected from globals.css) ── */
:root {{
{vars_block}
}}
</style>"""

    def inject_tokens(self, html: str) -> str:
        """
        Inserts the full design token :root block into the <head> of the HTML.
        If there is no <head>, prepends it at the top.
        """
        token_block = self._build_token_style_block()
        if not token_block:
            return html

        if re.search(r'<head', html, re.IGNORECASE):
            # Insert just after the opening <head> tag (case-insensitive)
            html = re.sub(
                r'(<head[^>]*>)',
                rf'\1\n{token_block}',
                html,
                count=1,
                flags=re.IGNORECASE
            )
        else:
            html = token_block + "\n" + html
        return html

    def adapt_html(self, html_content: str) -> str:
        """
        Uses GPT-4o to rewrite the HTML content, replacing hardcoded styles
        with Design System variables and utility classes.
        Always injects the full :root token block regardless.
        """
        if not html_content:
            return html_content

        # Step 1: Always inject tokens so var() references resolve in the browser
        html_content = self.inject_tokens(html_content)

        # Step 2: Optionally refactor with GPT-4o (skip if no OpenAI client)
        if not self.client:
            return html_content

        system_prompt = f"""
        You are an expert Frontend Engineer specialized in Design Systems and Tailwind CSS.
        Your task is to REFACTOR the provided HTML code to strictly adhere to the project's Design System.

        ### DESIGN SYSTEM CONTEXT (globals.css):
        {self.css_content[:3000]}... (truncated)

        ### INSTRUCTIONS:
        1. **Replace Hardcoded Colors**:
           - Identify any hex codes (e.g., #c000f3) or standard Tailwind colors (e.g., bg-purple-600).
           - Replace them with the corresponding CSS variable using Tailwind arbitrary values.
           - Example: `bg-[#c000f3]` -> `bg-[var(--color-primary)]`
           - Example: `text-white` -> `text-[var(--color-text-primary)]`

        2. **Use Semantic Classes**:
           - If you see a card with glassmorphism, use the class `glass-card`.
           - If you see a panel/container with glassmorphism, use the class `glass`.
           - If you see glowing text, use `text-glow-purple`.

        3. **Layout & Structure**:
           - Ensure the main container has `min-h-screen bg-[var(--color-bg-app)]`.
           - Do NOT remove the main structure, just update the classes/styles.
           - Do NOT remove or alter the <style>:root{{...}}</style> token block already present in <head>.

        4. **Output**:
           - Return ONLY the modified HTML code. Do not wrap in markdown blocks like ```html ... ```.
           - Ensure the code is complete and valid HTML.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here is the HTML code to refactor:\n\n{html_content}"}
                ],
                temperature=0.2,
            )

            cleaned_html = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present (despite instructions)
            if cleaned_html.startswith("```html"):
                cleaned_html = cleaned_html[7:]
            if cleaned_html.startswith("```"):
                cleaned_html = cleaned_html[3:]
            if cleaned_html.endswith("```"):
                cleaned_html = cleaned_html[:-3]

            adapted = cleaned_html.strip()

            # Safety net: re-inject tokens if GPT accidentally stripped the <style> block
            if ":root" not in adapted:
                adapted = self.inject_tokens(adapted)

            return adapted

        except Exception as e:
            print(f"Error adapting HTML: {e}")
            return html_content  # Return (token-injected) original on error


# Singleton instance
design_adapter = DesignAdapter()
