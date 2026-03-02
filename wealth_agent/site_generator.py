import os
import shutil
import sqlite3
import re
from datetime import datetime

class SiteGenerator:
    def __init__(self, db_path: str, output_dir: str = "dist"):
        self.db_path = db_path
        self.output_dir = os.path.join(os.path.dirname(__file__), output_dir)
        self.assets_dir = os.path.join(self.output_dir, "assets")
        self.globals_css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "globals.css")
        
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _get_design_tokens(self):
        """Parses globals.css to extract ALL CSS variables as a flat dict {var_name: value}."""
        # Sensible defaults in case parsing fails
        defaults = {
            "--color-primary":             "#a400f3",
            "--color-primary-light":       "#ff8a00",
            "--color-primary-dark":        "#13a600",
            "--color-success":             "#c52222",
            "--color-warning":             "#f59e0b",
            "--color-danger":              "#ef4444",
            "--color-info":                "#a53bf6",
            "--color-text-primary":        "#ffffff",
            "--color-text-secondary":      "#a1a1aa",
            "--color-text-muted":          "#52525b",
            "--color-text-on-dark":        "#ffffff",
            "--color-bg-app":              "#161515",
            "--color-bg-card":             "#111118",
            "--color-bg-sidebar":          "#0d0d12",
            "--color-bg-input":            "#1a1a24",
            "--color-bg-page":             "#0a0a0a",
            "--color-border":              "#27272a",
            "--color-chart-equities":      "#db0000",
            "--color-chart-real-estate":   "#3b82f6",
            "--color-chart-fixed-income":  "#81ea28",
            "--color-chart-crypto":        "#34d399",
            "--radius-none":  "0px",
            "--radius-sm":    "3px",
            "--radius-md":    "6px",
            "--radius-lg":    "9px",
            "--radius-xl":    "17px",
            "--radius-2xl":   "30px",
            "--radius-3xl":   "46px",
            "--blur-sm":  "4px",
            "--blur-md":  "8px",
            "--blur-lg":  "16px",
            "--blur-xl":  "32px",
            "--blur-2xl": "64px",
            "--blur-3xl": "120px",
            "--font-size-h1":      "48px",
            "--font-size-h2":      "36px",
            "--font-size-h3":      "24px",
            "--font-size-body":    "16px",
            "--font-size-sm":      "14px",
            "--font-size-xs":      "12px",
            "--font-weight-bold":  "700",
            "--font-weight-semibold": "600",
            "--font-weight-medium":   "500",
            "--font-weight-regular":  "400",
            "--spacing-1":  "4px",
            "--spacing-2":  "8px",
            "--spacing-3":  "12px",
            "--spacing-4":  "16px",
            "--spacing-6":  "24px",
            "--spacing-8":  "32px",
            "--spacing-12": "48px",
            "--spacing-16": "64px",
        }

        if not os.path.exists(self.globals_css_path):
            return defaults

        try:
            with open(self.globals_css_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Extract every  --var-name: value;  pair from the whole file
            for m in re.finditer(r'(--[\w-]+)\s*:\s*([^;\n]+);', content):
                var, val = m.group(1).strip(), m.group(2).strip()
                if var in defaults:
                    defaults[var] = val
        except Exception as e:
            print(f"Token parsing error: {e}")

        return defaults

    def clean_output_directory(self):
        """Removes the output directory if it exists and creates it fresh."""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)
        os.makedirs(self.assets_dir)

    def get_published_content(self, post_type=None):
        sql = "SELECT * FROM posts WHERE status = 'published'"
        params = []
        if post_type:
            sql += " AND post_type = ?"
            params.append(post_type)
        sql += " ORDER BY updated_at DESC"
        
        with self._conn() as conn:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]

    def get_homepage(self):
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM posts WHERE is_homepage = 1 AND status = 'published' LIMIT 1").fetchone()
            return dict(row) if row else None

    def generate_css(self):
        """Generates a static style.css file with the FULL design token set synced from globals.css."""
        t = self._get_design_tokens()

        # Build a :root block with every token from globals.css
        root_vars = "\n".join(
            f"    {var}: {val};" for var, val in t.items()
        )

        primary = t.get("--color-primary", "#a400f3")
        bg      = t.get("--color-bg-app",  "#161515")
        text    = t.get("--color-text-primary", "#ffffff")
        muted   = t.get("--color-text-muted",   "#52525b")
        border  = t.get("--color-border",  "#27272a")

        css_content = f"""
:root {{
    /* ── Full design token set (auto-synced from globals.css) ── */
{root_vars}

    /* ── Aliases for legacy generated pages ── */
    --color-bg: {bg};
    --color-surface: rgba(20, 20, 20, 0.6);
    --color-surface-solid: #121212;
    --color-primary-hover: {primary};
    --color-primary-soft: {primary}20;
    --font-heading: 'Outfit', sans-serif;
    --font-sans: 'Inter', sans-serif;
    --glass-blur: blur(16px);
    --shadow-premium: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
    --transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}}

* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    -webkit-font-smoothing: antialiased;
}}

body {{
    background-color: var(--color-bg);
    background-image: 
        radial-gradient(circle at 20% 20%, var(--color-primary-soft) 0%, transparent 40%),
        radial-gradient(circle at 80% 80%, rgba(219, 218, 0, 0.03) 0%, transparent 40%);
    color: var(--color-text-primary);
    font-family: var(--font-sans);
    line-height: 1.8;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}}

a {{
    color: inherit;
    text-decoration: none;
    transition: var(--transition);
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 40px;
    width: 100%;
}}

/* Header & Nav */
header {{
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    background: rgba(3, 3, 3, 0.7);
    border-bottom: 1px solid var(--color-border);
    padding: 24px 0;
    position: sticky;
    top: 0;
    z-index: 100;
}}

nav {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.logo {{
    font-family: var(--font-heading);
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #fff 0%, #888 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.nav-links {{
    display: flex;
    gap: 40px;
}}

.nav-links a {{
    color: var(--color-text-muted);
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 0.01em;
}}

.nav-links a:hover {{
    color: var(--color-primary);
}}

/* Main Content */
main {{
    flex: 1;
    padding: 100px 0;
}}
main.full-width {{
    padding: 0;
}}

h1, h2, h3, h4 {{
    font-family: var(--font-heading);
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--color-text-primary);
}}

h1 {{ font-size: 4rem; line-height: 1; margin-bottom: 2.5rem; }}
h2 {{ font-size: 2.5rem; margin-top: 4rem; margin-bottom: 1.5rem; }}
h3 {{ font-size: 1.8rem; margin-top: 2.5rem; margin-bottom: 1.2rem; }}

p {{ margin-bottom: 1.8rem; color: #b5b5b5; font-size: 1.15rem; }}

/* Hero section */
.hero {{
    text-align: center;
    max-width: 900px;
    margin: 0 auto 120px;
}}

.hero h1 {{
    font-size: 5rem;
    background: linear-gradient(to bottom, #fff 20%, #666 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.5rem;
}}

.hero p {{
    font-size: 1.4rem;
    color: var(--color-text-muted);
}}

/* Posts Grid */
.posts-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 40px;
}}

.post-card {{
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: 48px;
    display: flex;
    flex-direction: column;
    transition: var(--transition);
}}

.post-card:hover {{
    transform: translateY(-12px) scale(1.02);
    border-color: var(--color-primary);
    box-shadow: var(--shadow-premium);
    background: rgba(40, 40, 40, 0.4);
}}

.post-card .badge {{
    margin-bottom: 24px;
}}

.post-card h2 {{ font-size: 1.8rem; margin-bottom: 20px; line-height: 1.2; }}
.post-card .excerpt {{ 
    font-size: 1rem; 
    color: var(--color-text-muted);
    margin-bottom: 32px;
}}

.post-card .read-more {{
    margin-top: auto;
    font-weight: 700;
    color: var(--color-primary);
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.95rem;
}}

/* Post Detail */
.post-header {{
    max-width: 800px;
    margin: 0 auto 80px;
    text-align: center;
}}

.post-header .badge {{ margin-bottom: 24px; }}

.post-body {{
    font-size: 1.25rem;
    line-height: 1.9;
}}
.post-body:not(.full-width) {{
    max-width: 780px;
    margin: 0 auto;
}}

.post-body h2 {{ color: #fff; }}
.post-body p {{ color: #ccc; }}

.post-body blockquote {{
    padding: 32px 40px;
    background: var(--color-primary-soft);
    border-radius: var(--radius-md);
    border-left: 4px solid var(--color-primary);
    margin: 60px 0;
    font-style: italic;
    font-size: 1.6rem;
    line-height: 1.5;
    color: #fff;
}}

/* Badges */
.badge {{
    display: inline-block;
    padding: 6px 16px;
    background: var(--color-primary-soft);
    color: var(--color-primary);
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

/* Footer */
footer {{
    margin-top: 100px;
    padding: 80px 0;
    border-top: 1px solid var(--color-border);
    text-align: center;
    color: var(--color-text-muted);
}}
"""
        with open(os.path.join(self.assets_dir, "style.css"), "w", encoding="utf-8") as f:
            f.write(css_content)

    def _get_layout(self, title, content, pages_list, full_width=False):
        """Premium layout wrapper with Outfit and Inter fonts."""
        tokens = self._get_design_tokens()
        nav_html = ""
        for page in pages_list:
            nav_html += f'<a href="{page["slug"]}.html">{page["title"]}</a>'
            
        return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | NXSTEP Premium CMS</title>
    <link rel="stylesheet" href="assets/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Custom tweaks to play nice with Tailwind and keeping our primary color sync */
        :root {{
            --color-primary: {tokens.get('--color-primary', '#a400f3')};
        }}
        .hero-gradient {{
            background: radial-gradient(circle at 20% 20%, {tokens.get('--color-primary', '#a400f3')}20 0%, transparent 40%),
                        radial-gradient(circle at 80% 80%, {tokens.get('--color-primary', '#a400f3')}10 0%, transparent 40%);
        }}
        .gradient-text {{
            background: linear-gradient(135deg, #fff 0%, {tokens.get('--color-primary', '#a400f3')} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .floating {{
            animation: float 6s ease-in-out infinite;
        }}
        @keyframes float {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-20px); }}
            100% {{ transform: translateY(0px); }}
        }}
    </style>
</head>
<body>
    <header class="sticky top-0 z-[100] backdrop-blur-xl bg-black/70 border-b border-white/10 py-6">
        <div class="container mx-auto px-10">
            <nav class="flex justify-between items-center">
                <a href="index.html" class="text-3xl font-extrabold tracking-tighter bg-gradient-to-b from-white to-gray-500 bg-clip-text text-transparent italic">NXSTEP</a>
                <div class="flex gap-10 text-gray-400 font-medium">
                    <a href="index.html" class="hover:text-(--color-primary) transition-colors">Journal</a>
                    {nav_html}
                </div>
            </nav>
        </div>
    </header>

    <main class="{"full-width" if full_width else ""}">
        {"<div class='container'>" if not full_width else ""}
            {content}
        {"</div>" if not full_width else ""}
    </main>

    <footer>
        <div class="container">
            <p>&copy; {datetime.now().year} NXSTEP. Propulsé par Expert Content Architect.</p>
        </div>
    </footer>
</body>
</html>"""

    def generate_index(self, posts, pages):
        """Generates the premium index.html. Uses custom homepage if set, else grid."""
        homepage = self.get_homepage()
        
        if homepage:
            # Use the single page/post template for the index
            is_page = homepage.get('post_type') == 'page'
            content = f"""
            {f'<div class="post-header"><h1>{homepage["title"]}</h1></div>' if not is_page else ""}
            <div class="post-body {"full-width" if is_page else ""}">
                {homepage['content']}
            </div>
            """
            html = self._get_layout(homepage['title'], content, pages, full_width=is_page)
        else:
            # Fallback to the classic article grid
            posts_html = ""
            if not posts:
                posts_html = "<p style='text-align:center; padding: 40px;'>Aucun article publié pour le moment.</p>"
            else:
                for p in posts:
                    posts_html += f"""
                    <article class="post-card">
                        <span class="badge">Article</span>
                        <h2><a href="{p['slug']}.html">{p['title']}</a></h2>
                        <p class="excerpt">{p.get('excerpt') or ''}</p>
                        <a href="{p['slug']}.html" class="read-more">Explorer l'article &rarr;</a>
                    </article>
                    """
            
            content = f"""
            <section class="hero">
                <h1>Expert Architecture & Innovation</h1>
                <p>Découvrez les dernières avancées en IA, Design System et automatisation intelligente par NXSTEP.</p>
            </section>
            <div class="posts-grid">
                {posts_html}
            </div>
            """
            html = self._get_layout("Journal", content, pages)

        with open(os.path.join(self.output_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)

    def generate_site(self):
        """Main entry point to generate the entire site."""
        self.clean_output_directory()
        self.generate_css()
        
        posts = self.get_published_content(post_type="post")
        pages_content = self.get_published_content(post_type="page")
        
        # 1. Generate Index
        self.generate_index(posts, pages_content)
        
        # 2. Generate Posts
        for p in posts:
            content = f"""
            <div class="post-header">
                <span class="badge">Publication</span>
                <h1>{p['title']}</h1>
                <div class="post-meta">MàJ le {p['updated_at'][:10]} &bull; Par {p.get('author','IA')}</div>
            </div>
            <div class="post-body">
                {p['content']}
            </div>
            """
            html = self._get_layout(p['title'], content, pages_content)
            with open(os.path.join(self.output_dir, f"{p['slug']}.html"), "w", encoding="utf-8") as f:
                f.write(html)
                
        # 3. Generate Pages
        for p in pages_content:
            content = f"""
            <div class="post-body full-width">
                {p['content']}
            </div>
            """
            # Pages are full-width by default as per user request
            html = self._get_layout(p['title'], content, pages_content, full_width=True)
            with open(os.path.join(self.output_dir, f"{p['slug']}.html"), "w", encoding="utf-8") as f:
                f.write(html)
        
        return self.output_dir

if __name__ == "__main__":
    # Test generation
    db = os.path.join(os.path.dirname(__file__), "data", "cms.db")
    if os.path.exists(db):
        gen = SiteGenerator(db)
        out = gen.generate_site()
        print(f"Site généré avec succès dans : {out}")
    else:
        print("Base de données introuvable for the test.")
