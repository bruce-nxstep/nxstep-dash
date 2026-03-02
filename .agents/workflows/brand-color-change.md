---
description: How to safely change the brand color of the dashboard
---

# Brand Color Change Workflow

## ⚠️ WARNING
Changing the brand color is a SYSTEM-WIDE operation. Follow this workflow precisely to avoid breaking the design.

## Step 0: MANDATORY — Ask the user first (DO NOT SKIP)
Before doing ANYTHING else, you MUST ask the user:
1. **What is the target color?** (exact hex code, e.g. `#00b300`)
2. **Which components should be affected?** (all dashboard components, or specific ones?)
3. **Is this a temporary experiment or a permanent change?**

Do NOT read any file, do NOT make any edit, until you have received explicit answers to these three questions.
If the user only typed `/brand-color-change` without additional context, reply with these questions and wait.

## Step 1: Read the current design system
Read `DESIGN_SYSTEM.md`. Understand the current primary color and where it is used.

## Step 2: Update ONLY the @theme block in globals.css
Edit `app/globals.css` and update only the `@theme` block:
```css
@theme {
  --color-primary: #YOUR_NEW_COLOR;
  --color-primary-light: #YOUR_LIGHTER_COLOR;
  --color-primary-dark: #YOUR_DARKER_COLOR;
}
```
Do NOT touch anything else in the file.

## Step 3: Update component internal color logic
In each dashboard component (`MetricCard`, `PortfolioChart`, etc.):
- Find the internal color mappings (e.g., `rgba(130, 0, 219, 0.4)` for purple)
- Replace the RGBA values with the new color's RGBA equivalent
- Do NOT change the variant prop types (keep `"purple"` as the string, just re-map what color it represents)

## Step 4: Update DESIGN_SYSTEM.md
Update the brand identity section at the top of `DESIGN_SYSTEM.md` to reflect the new color.

## Step 5: Type Check
// turbo
Run: `npx tsc --noEmit --project tsconfig.json --skipLibCheck`

## Step 6: Verify in Storybook
Take a screenshot to confirm the new color is applied correctly everywhere before reporting success.
