---
name: design-taste-frontend
description: >-
  When to read: building, designing, redesigning, or reviewing a landing page, company, product,
  or SaaS site — or a page looks generic, templated, or 'AI-made'. Use for: anti-slop frontend
  work at tasteskill 2.5.1 — plain copy in a voice of its own, one system, one section per
  screen, real photographs and product UI. Does: enforces it with a checker and finish gate in a
  real browser; shader effects only on tech/gaming/software pages. Matches tasteskill 2.5.1
  (verified on the VM, 2026-11-14).
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# tasteskill 2.5.1

Matches tasteskill 2.5.1 (verified on the VM, 2026-11-14).

Build the website a good company would ship: plainly what is sold, the real thing on every screen, made for this client — not from a template, not like an art piece. figma.com and x.ai are the bar (in words: `layout-v4.md` section 1).

`<skill>` is this folder. It needs Node 22+ and Chrome, Edge or Chromium (ffmpeg optional).

## House rules

These nine win over everything else in this skill.

1. **No caption or description under any image, render or visual.** Licence credits go in one footer line.
2. **Every visual renders, never an empty ground,** at 1440, 1024, 768 and 390.
3. **One section per screen:** the hero alone on the first screen, every section exactly one or two screens tall at 1440x900, no second section heading peeking in. Exception: a live `photo-chapters` section, three or four screens, set by the moment.
4. **Equal left and right content edges.**
5. **Hover micro-animations:** a linked card lifts 2px, a photo zooms 1.02-1.03 inside its frame, buttons step on hover and press on click, underlines draw, card loops cycle in 2.5-4 s, repeat and restart on hover. The motion layer does it; never strip or override it. No tilt, carousels or timed tabs. Every hero enters once on load (`data-enter`); every page carries one dealt moment, two on a long page (the gate holds both).
6. **More and better real photographs where they fit;** nicer backgrounds; better heroes, layouts and fonts.
7. **Real full-colour icons** (a known product's real icon, never a drawn one); small diagram visuals in cards (a hub with branches; one input, a main processor, three parallel lanes; pulses along the lines).
8. **The big award-site scenes and creative moments are part of the skill:** every page deals its moments (photo- and type-led off tech), but shader effects and scenes only where the trade has a technical subject (tech, AI, developer tools, gaming, fintech, hardware), never on a local cafe, bakery, guesthouse or shop — those get photographs.
9. **Addresses:** street and district only (no street given: the district), no house number, postcode or coordinates; no register or VAT numbers; no phone in a real format; contacts on `.example`.

## 1. The kind of business decides everything

Write the kind on the plan's first line and declare it on the page: the page type on `<html data-type>` and `<meta name="page-type">` (same value), and `<meta name="site-kind">`; a place adds `<meta name="page-kind" content="place">`. The dealers take the last column (`start.mjs --page`, `moments.mjs --page`), the hero dealer the page type; `consistency.mjs` reads the metas.

| Brief | page type | site-kind | kind |
|---|---|---|---|
| App, SaaS, AI, developer tool, fintech or banking app, a studio selling its own software | software | software | software |
| A game, a studio launching its game | software | gaming | gaming |
| Hardware or a tech device (a drone, a robot arm, a keyboard) | product | tech | tech |
| Any other physical product or brand (a chair, a bike, coffee beans sold online) | product | other | product |
| People are hired: clinic, law firm, agency, creative studio, trade | service | other | service |
| People come to it: cafe, bar, bakery, restaurant, guesthouse, small hotel, shop, florist, bike shop, gym, local studio | place | other | place |

A maker that also opens its door or teaches (a ceramics studio, a bakery with a web shop) is a **place**; its web shop becomes the goods section. It is a product only when nothing happens at the door.

"Tech" below means site-kind software, gaming or tech; "other" is everything else. Effects, scenes, loops, counts, CSS grounds, dark pages and dark heroes are tech only. An other page is photographs, flat colour, type, real icons, the hero's entrance, its dealt moment (photo- or type-led, `moments.md`) and the hover layer.

## 2. The page plan by kind

The full plans, deal lists and section order: `references/sections.md`.

- **Place** (a cafe, bakery, guesthouse, shop). Photographs lead: 12 to 20 on the full page, 8 to 12 compact, under 8 frames the 3-screen short page; no client photographs: the draft path and a live search (`photos.md`), then count; the palette dealt by trade. The hero a photograph whenever a frame fits (a remote place: its region's landscape), the visit block on screen two, the offer, the place, orders or booking.
  **Variety without effects** (`sections.md` section 4): the offer and the place deal different compositions, never two sections round one picture; one type moment (the address or name set large); one main action a screen; list text 16px. Flat grounds, square photographs, one button style, the phone bar, the dealt moments; no effect, ground, loop, fragment, diagram or tab.
- **Product and service** (site-kind other). Photographs lead: the product, the people, the rooms, the work, two or more a screen on a product page. Real icons for the tools a studio uses; one still diagram at most; flat grounds and one brand band. No shader effect, print, grain, gradient, scene or loop (the dealt moments only); WebGL only for a product render the brief asks for. **A physical product with no photographs is shown in photographs:** stand-ins of the same kind of thing from `photos.mjs search`, each listed in the report, on the full product page; a render (`assets/objects/product-render`, stills) only when the brief asks for 3D or a render; never a drawing, mood stock or a set of props (`sections.md`, Product).
- **Every product page** (photographed, in stand-ins or rendered on a 3D ask, hardware too; the bar is Figure and 1X; `sections.md`, Product): the product **big** where it stands whole (most of its frame, or on the ground at anchor scale), never mid-size in a grey rounded panel on a grey ground; **a different picture each section**, never one view twice; **every headline promise pictured**; dealt compositions, no structure twice, one contrasting ground; the **swatch changes the picture**, every colour shown once; **no fact twice**; buttons step and press (rule 5).
- **Tech** (software, gaming, hardware). The client's own subject leads at true size. Software: its own UI as live HTML showing what it works on in one `app-frame`, never a generic dashboard or only fragments on panels; cards: fragments on lit panels, pulsing diagrams, real icons. Hardware: its photographs, else stand-in photographs of its kind (a render only when the brief asks for 3D), never a split hero of only an order form or a drawn SVG. A game: its name in the h1, a launch line, its world as full-bleed key art (else its name set large over stand-in photographs of its setting), an effect never in its place (`sections.md`, Gaming). **60 to 80 words a screen** outside UI mocks (`copy.md`). By deal: **one effect** (a shader ground in the hero or the one `[data-visual]` frame, a WebGL part, an object or one big scene) and **one or two moments** in their own sections; four live WebGL contexts at most; no card moves with the scroll (`effects-usage.md`).
- **One object never carries the page.** The product or hero object whole leads the hero and **two more sections at most**; another kind of visual the brief supports carries the rest (`sections.md` section 1, its table).
- **The client's own assets get slots.** A trailer, key art, screenshots, CAD renders or a motion video the brief names each get a frame that reads finished now (a real `<video>` with a stand-in poster, a play control only when there is a page or file to play, three to five stand-in photographs of the world, a CAD frame), named in a comment for the client's file, never empty (`sections-library.md`, client-slots).

## 3. What serves which page

The asset-family matrix is in [Asset matrix](references/asset-matrix.md) — open the reference of every asset family the page uses first. A dash means never.
## 4. The run

0. **The stack.** An empty folder builds a static page: copy `<skill>/assets` into `assets`, start from `assets/starter.html`. An existing project builds in its own stack, its components taking the starter's markup and classes, with the kit copied into its public folder (`public/assets`) and loaded from there as plain files. A Next.js brief builds a static export (`output: 'export'`), checked on its built page.

1. **Read the brief.** Write down the kind (section 1), what is sold, who buys it, the one main action (Book a room, Order a cake, Start a free trial; a place with neither: Get directions) and the real material: logo, screens, photographs, prices, address, hours. Then arm the finish gate, before any page exists:

   ```bash
   node <skill>/scripts/gate.mjs --start index.html --kind <kind> --category "<what is sold>" --primary "<main action>"
   ```

   A framework build names its dev server's URL (`--start http://localhost:5173/`) or its built page (`--start dist/index.html --root dist`; Next.js export: `out`) instead of `index.html`, and rebuilds before every gate run.

2. **Write all the copy first,** with the copy layer (`copy-voice.md`: the fact sheet, the voice card on the plan, the page's shape, the device budget; a register from `copy-registers.md`, the moves of `copy-moves.md`) within the rules of `copy.md`: the h1 names the category and the buyer or the place (a game: its name and genre), one hard fact on the first screen, a noun in every heading, buttons as a verb and an object. Nothing is invented but a coined brand name (searched first, the result kept in `names.json` beside the page) and, on a place, plausible hours and prices, each marked `data-assumed` (`copy.md`, What may be assumed). A draft kept in a `.md` file lints the same way as the page (the voice card and part labels are skipped).

3. **Plan the page as screens.** Line 1: the kind. Line 2: the deal (step 4), with one sentence on why the palette fits the trade. Then one line per section: its id, its one idea, its picture and its kind (object, use, parts, world, slot, diagram, type; three object lines at most), its screens (1 or 2, from its content height, `layout-v4.md` section 2), which section holds a moment and why it moves (on tech also the effect or the scene). Pick the photographs now (`photos.md`); their count, stand-ins included, sets a place's length (section 2). Then read `cards.md` and the recipe of every id you use in `sections-library.md`.

4. **Deal, never choose by taste.** Each command keeps a history, so pages differ:

   ```bash
   node <skill>/assets/layout/deal.mjs --type <page type> --has <photo,ui,film,object,setting> --history .taste-skill/layout-history.json   # the hero; a game adds --kind gaming, hardware --kind tech
   node <skill>/scripts/start.mjs deal --page <kind> --trade <trade> --history .taste-skill/history.json    # three palettes made for the trade, three pairings: take the first; add --axis after a word or editorial hero
   node <skill>/scripts/start.mjs css --page <kind> --palette <id> --type <id> --radius soft --history .taste-skill/history.json
   node <skill>/scripts/start.mjs brand --page place --bg "#.." --ink "#.." --accent "#.." [--surface "#.."] [--muted "#.."] --type <id> --radius soft   # the client's own colours (a logo, a painted shopfront), in place of css
   node <skill>/scripts/moments.mjs pick --page <kind> --count 1|2 --fits section,statement --photo --history .taste-skill/history.json   # every kind
   node -e "for(const l of process.argv.slice(1)){const o=l.split('|');console.log(o[Math.floor(Math.random()*o.length)])}" <the kind's lists, below>
   ```

   Run every command from the project folder (the deal arms the gate in the folder it runs in, or joins the build already open one or two folders up). The lists, in order nav, footer, close, rhythm, buttons, mark (`sections.md` sections 2 and 3):
   - software: `"nav-mega|nav-cards|nav-centre" "footer-dark|footer-statement|footer-columns" "close-type|close-word" "dark-band|surface-pairs|space" "solid|pill|tonal|arrow" "wordmark|initial|arc|ring|stack|dots"`
   - gaming: `"nav-mega|nav-centre|nav-cards" "footer-dark|footer-statement" "close-word|close-type" "dark-band|media-band|space" "solid|pill|block" "wordmark|initial|arc|ring|stack|dots"`
   - product and hardware: `"nav-cards|nav-split|nav-mega" "footer-columns|footer-dark" "close-photo|close-type|close-word" "dark-band|brand-band" "arrow|solid|block|pill" "wordmark|initial|arc|ring|stack|dots"`
   - service: `"nav-mega|nav-split|nav-centre" "footer-visit|footer-dark|footer-columns" "close-type|close-photo" "surface-pairs|dark-band|space" "solid|tonal|block|arrow" "wordmark|initial|arc|ring|stack|dots"`
   - place: the whole line in `sections.md` section 4, Place (The deal), read in its order.

   A product or hardware with no photographs deals `--has photo` for its stand-ins; `--has object` only for a cut-out or a render the brief asks for (always the `product` hero, its widest view across the wrap, no box); a game without art files passes `--has setting` (the `photo` hero, its name over a stand-in of its setting; a game always passes `--has`). A product page is dealt only the product, photo and film heroes. A place's hero is printed, never dealt (`--type place`). A dealt part that needs a photograph the page lacks is dealt again (`sections.md` section 2). Take the first palette and pairing printed (the next only when the first clashes with the client's own logo or photographs, or the pairing fails `hero-lines`, said on plan line 2); the client's own colours go through `start.mjs brand` instead (`sections.md` section 4, Look); never violet: deal again. Keep the `:root` block as printed. Radius: `sharp` for fintech and developer tools, `soft` by default, `round` for consumer apps, square on a place. On tech only: the lit ground (`<html data-ground>`: `sand|sky|sage` through the one-liner), the CSS grounds (`backgrounds.md`) and the one effect (`effects-usage.md`). Write every result on plan line 2 and in the comment at the top of `<body>`, and build exactly that (a short page drops what it has no section for).

5. **Build.** In `starter.html`: set `<html lang data-type data-radius data-buttons data-motion>` (lang: the brief's language), the three metas, the head block (title, description, og, icon, theme-color: `system.md`, Head) and the nav class; keep the skip link and the `m-enter` head line; copy only the `<section class="hero …" data-enter>` of `assets/layout/hero-<id>.html` (never its nav, other sections, footer or credit line; every word and picture becomes the client's); move the dealt close and footer out of their `<template>`s and delete the rest. Every section is `main > section` with one `.wrap`, its h2 first, `--h: 1` or `2`. Build each to its recipe with the system's classes and tokens; write page CSS only where a reference says page CSS (inside a visual, `--p-h`, `.wall`, `.rail`, `.device`). Paste UI from `assets/ui/<name>/fragment.html` and rewrite every name, number and logo to the client's (kit icons become `data-icon`, `cards.md`); a diagram card is `data-diagram="<preset>"` with the client's labels; run `icons.mjs scan index.html --out assets/icons --colour` last, so every icon the page names is a local file. Mount an effect, object, moment or scene exactly as its reference says, never from your own script. A moment's section is copied from `assets/moments/_demo/in-page.html` (place: photo-chapters, word-highlight) or `in-page-service.html` (pinned-chapters, picture-develops film); a moment's own `demo.html` shows it alone and is not a page model. A form is the starter's `booking-form` (`system.md`, Forms). Credits: the one footer line from `photos.mjs credits`, once the markup uses the photographs (it reads the page). Copy the hero's tile from `shoot.mjs` beside the page as `share.jpg`.

Then run the check, gate, and report procedure in [Check and report](references/check-and-report.md).
## 5. Checklist

The full checklist is in [Checklist](references/checklist.md) — read it against every screenshot.
## 6. Never

- A card, row or tile that fades in on scroll; a fade-in on every section; parallax on text; scroll-jacking; random blinking.
- Stock photographs passed off as the client's product, people or place (a stand-in is listed in the report as one, never shown with another maker's name or logo); a product page that never shows the product.
- A drawn look-alike of a real logo; invented reviews, quotes, customers or figures.
- Violet or lavender in the page's own design: accent, ground, gradient, effect colour or tint (a real third-party logo keeps its own colours, `icons.md`).
- AI-tell visuals (cook ban list): eyebrow labels, monospace uppercase text, random serif fonts, beige as a ground, 01/02/03 counters, glowing orbs, shockwave rings popping out of things, decorative particles.
- Copying a reference site's code, copy, pictures or signature effect.
- Deleting or editing the kit's own files (`assets/`, `scripts/`) to clear a check: a check that flags a kit file is reported, and the page is checked again after any change.

## References

All in `references/`; section 3 names the one each asset needs.

## Provenance

Adapted from leonxlnx/taste-skill (MIT).

Library adaptation: the Claude Code Stop hook was removed; run `node <skill>/scripts/gate.mjs` manually before declaring done. On Debian/Linux install Node and Chrome from your distro or NodeSource, on Windows use the Node installer and Chrome/Edge.
