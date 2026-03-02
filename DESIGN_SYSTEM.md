# NXSTEP Dashboard — Design System Rules
# ⚠️ READ THIS BEFORE MODIFYING ANY CSS OR COMPONENT FILE ⚠️

## Brand Identity
- **Primary Brand Color**: `#8200db` (Imperial Purple)
- **Primary Light**: `#a346ff`
- **Primary Dark**: `#5b009d`
- **Background**: Deep black / near-black (`#0a0a0a`, `bg-black`)
- **Theme**: Ultra-premium glassmorphism, luxury fintech aesthetic

---

## 🚨 Non-Negotiable Rules

### 1. `app/globals.css` Must Always Have:
```css
@import "tailwindcss";

@theme {
  --color-primary: #8200db;
  --color-primary-light: #a346ff;
  --color-primary-dark: #5b009d;
}
```
**NEVER delete these lines.** They are the entire engine of the design system.

### 2. Never Use Hardcoded Hex in Component Props
❌ **WRONG**: `variant="#8200db"`  
✅ **CORRECT**: `variant="purple"`

All variants must be **semantic strings** (`"purple"`, `"gold"`, `"blue"`) that map to colors internally.

### 3. Never Use Global Find-and-Replace on CSS Files
CSS files have context-specific syntax. A blind replace of `purple` in `globals.css` will destroy `@apply bg-purple-500` and other valid Tailwind utilities. Always edit manually and precisely.

### 4. Never Remove Tailwind Utility Classes
The `.glass`, `.glass-card`, `.text-glow-purple` classes are hand-crafted and are NOT auto-generated. If removed, they are gone.

### 5. Changing a Brand Color Means:
1. **Only** update the `@theme` block in `globals.css`
2. Update component internal logic (e.g., `isPurple` → `isGreen`) to point to the new colors
3. **Do not** change the variant prop type names (e.g., keep `"purple"`, just map it to the new color internally)

---

## Component Variant Schema

All dashboard components accept a `variant` prop:

| Variant | Description |
|---|---|
| `"purple"` | Imperial Purple (Primary brand) |
| `"gold"` | Luxury Gold (Secondary brand) |

**Default is always `"purple"`.**

---

## Verification Checklist (Before Confirming Changes)

- [ ] Does `globals.css` still start with `@import "tailwindcss"`?
- [ ] Does the `@theme` block still exist?
- [ ] Are `.glass` and `.glass-card` utilities still defined?
- [ ] Do all components still use semantic variant strings (not hex values)?
- [ ] Does `npx tsc --noEmit --skipLibCheck` exit with code 0?
- [ ] Does Storybook on port 6008 render the `ImperialPurple` story without errors?

---

## Storybook
- **Port**: `6008` (not 6006 — port conflict with Windows)  
- **Main story**: `Pages/DashboardOverview` → `ImperialPurple`
- **Stories location**: `src/stories/`
- **Components location**: `components/dashboard/`
