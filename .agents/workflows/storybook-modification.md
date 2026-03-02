---
description: How to safely modify Storybook dashboard components
---

# Storybook Modification Workflow

Follow these steps STRICTLY every time you modify a dashboard component or its story.

## Step 1: Read Before You Touch
Read `DESIGN_SYSTEM.md` at the root of the project FIRST. This is mandatory.
If it doesn't exist, STOP and tell the user.

## Step 2: Understand What You Are Modifying
- **CSS/Styling only** → Edit `app/globals.css` or inline Tailwind classes only. Never use global find-replace on CSS files.
- **Component logic** → Edit the `.tsx` file in `components/dashboard/`. Keep variant props semantic.
- **Story (documentation)** → Edit `.stories.tsx` in `src/stories/`.

## Step 3: Make Your Changes
Edit files surgically. Use precise, targeted replacements. Never replace the entirety of a file unless absolutely necessary.

After each file edit, mentally answer:
- Is `@import "tailwindcss"` still in globals.css?
- Are there any hardcoded hex codes in variant props?

## Step 4: Type Check
// turbo
Run: `npx tsc --noEmit --project tsconfig.json --skipLibCheck`

If the exit code is not 0, DO NOT REPORT SUCCESS. Fix the errors first.

## Step 5: Verify in Storybook
Take a screenshot of Storybook at `http://localhost:6008` to confirm the visual result.
Navigate to the relevant story and confirm the component renders correctly with the correct colors.

## Step 6: Confirm
Only after Steps 4 and 5 pass, report to the user that the task is complete.
