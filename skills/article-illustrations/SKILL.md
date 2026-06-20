---
name: article-illustrations
description: "Generate hand-drawn 16:9 article illustrations featuring the Grav character IP. Turns article concepts into memorable whiteboard-sketch explanations with a recurring floating character, sparse annotations, and absurd metaphors."
metadata:
  source: "https://github.com/vssinghh/article-illustrations"
  date_added: "2026-06-14"
---

# Article Illustrations — Grav Hand-Drawn Style

## Overview

Generate 16:9 landscape hand-drawn illustrations for articles, blog posts, and technical content. Each illustration captures one cognitive anchor point from an article and turns it into a clean, absurd, memorable whiteboard-sketch explanation.

The skill uses a recurring character IP called **Grav**: a small, round, always-floating figure with dot eyes and a thin antenna. Grav participates in the core action of every illustration — never just decoration.

**Repository:** [vssinghh/article-illustrations](https://github.com/vssinghh/article-illustrations)

## Use this skill when

- Writing articles, blog posts, or documentation that need inline illustrations
- Turning abstract concepts into concrete visual metaphors
- Establishing a consistent visual language across multiple articles
- Producing hand-drawn explanation sketches, not PPT infographics

## Do not use this skill when

- You need polished, corporate-style PPT infographics or formal flowcharts
- You do not want a recurring character IP (Grav) featured in the illustrations
- You require animated, 3D, or realistic interface mockups instead of whiteboard sketches

## Instructions

### Step 1: Digest the Article

Read the article and identify cognitive anchor points — core judgments, turning points, input/output loops, before/after contrasts, and common pitfalls. Don't distribute illustrations evenly; prioritize moments that benefit from visual explanation.

### Step 2: Plan a Shot List

For each illustration, define:
- **Placement**: After which section
- **Theme**: What this image is about
- **Core Meaning**: The one idea it conveys
- **Structure Type**: One of 8 composition patterns (Workflow, System Closeup, Before/After, Role States, Conceptual Metaphor, Layered Method, Map Route, Mini Comic)
- **Grav's Action**: What Grav is doing in the scene
- **Annotation Labels**: 3–5 short English labels

### Step 3: Generate Images

Fill in the [Prompt Template](#prompt-template) below with the shot-list details and generate one image per illustration. Use whatever image-generation capability is available in your environment — a built-in `generate_image` tool, an MCP image server, or simply by emitting the filled-in prompt for the user to paste into their own generator. Generate each image separately; never combine illustrations. Every image follows strict style rules:
- Pure white background, no textures
- Black hand-drawn line art with slight wobble
- Sparse red/orange/blue handwritten annotations
- Grav always floating (never touching surfaces)
- One core idea per image
- 40–60% canvas usage, 35%+ whitespace

### Step 4: QA Check

Run each image against the [QA Checklist](#qa-checklist) below. If it fails any must-pass item or shows a failure signal, regenerate or request an edit.

## Examples

### Example 1: Plan illustrations for an article

```
Analyze this article and create a shot list of 5 illustrations.
Don't generate images yet — just plan which cognitive anchor points
deserve illustrations and what each image should convey.

<paste article>
```

### Example 2: Generate illustrations directly

```
Generate 4 Grav-style illustrations for this article.
Requirements: 16:9 landscape, pure white background, black hand-drawn
line art, sparse red/orange/blue English annotations.

<paste article>
```

### Example 3: Single concept illustration

```
Generate one 16:9 illustration for this concept:
"Trust isn't declared — it's built one piece of evidence at a time."
Grav must perform the core action. Keep labels sparse — aim for 3–5.
```

### Example 4: Iterate on a result

```
This illustration is on the right track, but Grav feels like decoration.
Keep the core meaning but regenerate: make Grav the one actually
driving the structure.
```

## Visual Style

| Element | Rule |
|:--------|:-----|
| Background | Pure white — no cream, texture, gradients, or shadows |
| Line art | Black, hand-drawn, slightly wobbly, not mechanical |
| Whitespace | Main subject 40–60% of canvas, 35%+ empty space |
| Annotations | Handwritten English, 2–5 words each, max 5–8 per image |
| Color: Black | Main line art, characters, structures, objects |
| Color: Red | Key highlights, problems, warnings, results |
| Color: Orange | Main flow, paths, arrows, direction |
| Color: Blue | Supplementary notes, feedback, system state |
| Prohibited | Green, purple, yellow, pink, gradients, drop shadows, 3D, realistic UI |

## Character: Grav

- Small round body (pebble/potato shape)
- Two dot eyes (slightly asymmetric)
- One thin bent antenna with tiny circle tip
- Thin stick legs that dangle without touching surfaces
- Always hovering — visible gap between Grav and any surface
- Expression: calm, focused, deadpan
- Role: active participant in the system, never decoration

## Best Practices

- ✅ Start with a shot list before generating images
- ✅ Invent a new metaphor for every illustration — never reuse compositions
- ✅ Make Grav the action protagonist, not a bystander
- ✅ Keep it absurd but structurally clear
- ✅ Use color sparingly — when in doubt, use black
- ❌ Don't make PPT infographics or formal flowcharts
- ❌ Don't add title bars or decorative frames
- ❌ Don't let Grav touch the ground or stand on surfaces
- ❌ Don't make Grav cute, smiling, or emoji-like

## Common Pitfalls

- **Problem:** Illustration looks like a PPT slide
  **Solution:** Remove 30% of elements, increase whitespace, make it weirder

- **Problem:** Grav is just standing next to the action
  **Solution:** Redesign so Grav IS the mechanism — becomes the funnel, dangles from the lever, is suspended inside the machine

- **Problem:** Same metaphor as a previous illustration
  **Solution:** Replace the physical object entirely — same concept, different analogy

## Prompt Template

Fill in each `{variable}` from the shot list, then feed the result to your image generator (Step 3).

```
Generate one standalone 16:9 horizontal article illustration.

Visual DNA:
Pure white background. Minimalist black hand-drawn line art. Slightly wobbly pen lines. Lots of empty white space. Sparse red/orange/blue handwritten English annotations. Clean absurd product-sketch feeling. No gradients, no shadows, no paper texture, no complex background, no commercial vector style, no PPT infographic look, no cute mascot poster, no children's illustration, no realistic UI.

Recurring IP character required:
Grav, a small round floating figure with dot eyes, a single thin bent antenna with a tiny circle tip, thin dangling stick legs that never touch surfaces, and a slightly uneven hand-drawn body shape. Grav always hovers slightly above any surface — there is always a visible gap between Grav and the ground. Grav must perform the core conceptual action, not decorate the scene. Make Grav calm, deadpan, focused, and slightly bizarre — not cute.

Theme:
{theme of this illustration}

Structure type:
{one of: Workflow / System Closeup / Before-After / Role States / Conceptual Metaphor / Layered Method / Map Route / Mini Comic}

Core idea:
{the one thing this image must convey}

Composition:
{specific scene: where is Grav, what is Grav doing, what are the main objects, how does information flow}

Suggested elements:
{element 1} / {element 2} / {element 3} / {element 4}

English handwritten labels:
{label 1} / {label 2} / {label 3} / {label 4} / {optional label 5}

Color use:
Black for main line art and Grav. Orange for main flow/path/arrows. Red only for key warnings/problems/results. Blue only for secondary notes or feedback/system state.

Constraints:
One image explains only one core structure. Keep the main subject around 40%-60% of the canvas. Preserve at least 35% white space. No title bar at the top. No border or frame. Maximum 5-8 annotation labels. Each label is 2-5 words. The style should feel like a senior engineer's casual whiteboard sketch — absurd, clean, memorable.
```

## QA Checklist

Run every generated image against these. Regenerate or edit on any failure.

**Must pass:**
- 16:9 landscape format
- Clean white background (no cream, texture, gradient, shadow, or noise)
- Grav is present and floating (visible gap between body and any surface)
- Grav performs the core action — not decoration
- Composition is an original metaphor for the current article
- One core structure per image; main subject ≤ ~60% of canvas, 35%+ whitespace
- Annotations are sparse (3–5, max 8), short (2–5 words), and readable
- Color discipline: orange = flow/arrows only, red = highlights/problems/results only, blue = notes/feedback only

**Regenerate if:**
- A title bar or section label appears on the image
- Grav looks like a mascot/emoji, is grounded, or is idle decoration
- Layout resembles a PPT slide, course material, or formal flowchart
- More than ~8 elements/arrows/nodes, or text blocks instead of short labels
- Background has texture/shadow/gradient/cream tint, or realistic UI appears
- Composition is too similar to a previously generated illustration

## Additional Resources

- **Upstream source / example gallery:** [vssinghh/article-illustrations](https://github.com/vssinghh/article-illustrations) — [example illustrations](https://github.com/vssinghh/article-illustrations#examples)

## Attribution

Adapted from [vssinghh/article-illustrations](https://github.com/vssinghh/article-illustrations).
Copyright (c) 2025 Vipin Singh. Licensed under the MIT License.
