6. **Check and look.** Only the skill's scripts, each running one headless Chrome with WebGL on the CPU, closed by its own PID, one at a time in the foreground with a 10-minute timeout; never in the background, a windowed browser or a browser tool. Each serves the page file itself over http on 127.0.0.1 (never `file://`), so no server is needed; for a built page whose links start at the site root (`/_astro/page.css`), pass `--root` with the build folder (`dist`). `--profile <dir>` is the Chrome profile: a folder of its own in the OS temp folder or the project's `.taste-skill` folder (`.taste-skill/chrome-check`), never outside the project (no `../`); a relative one leading out is replaced by `.taste-skill/chrome-<script>`. Then:

   ```bash
   node <skill>/scripts/copy-lint.mjs index.html --kind <kind>
   node <skill>/scripts/consistency.mjs index.html --widths 1440,1024,820,768,390 --rhythm-widths 1440,820,768,390 --profile <dir> --page <kind> --category "<what is sold>" --primary "<main action>"
   node <skill>/assets/layout/check.mjs --url index.html --profile <dir> --sizes 1440x900,1024x768,820x1180,768x1024,390x844 --shots shots/layout
   node <skill>/scripts/shoot.mjs --url index.html --w 1440 --out shots/1440.png --profile <dir>
   node <skill>/scripts/perf.mjs index.html --profile <dir>
   ```

   Shoot 1024, 820x1180, 768x1024 and 390 as well. Every `check.mjs` finding fails the page (no `--no-stress`). copy-lint opens no browser and takes under a second. Fix every FAIL (a copy-lint WARN too, or say why it stays) and read the copy aloud (`copy-voice.md` section 6); shoot again and read every screenshot against the checklist. In the fix rounds run `consistency.mjs --quick --widths 1440,390`. Then the gate, which runs the checker at 1440 and 390 every time, walks the page at 320 for overflow, collide and tap-size, and runs copy-lint, whose FAILs block like the checker's:

   ```bash
   node <skill>/scripts/gate.mjs index.html
   ```

   Fix what it lists and run it again until its last line is `GATE: PASS` or `GATE: OPEN`, three rounds at most (on agents with a Stop hook it also runs when you finish; otherwise run it manually before declaring done. A stop before your first gate run is no round; to ask the user something after a block, just stop again). When the user tells you to stop, or to ship the page as it is, run `gate.mjs --done "<what they said>"` (`GATE: DONE`) and report the open FAILs. `GATE: SETUP` (no page yet, a framework's source shell, a page that is not local): arm what a browser can open (step 1) and run it again. `GATE: ERROR` (the checks could not run) or `GATE: OFF`: put the line in the report and finish; do not rerun. Never edit the kit's files or hide anything from the checker. A FAIL you judge false is waived in `.taste-skill/waivers.json` with its reason, never fixed by gaming the check (`references/gate.md`); a word from the client's own copy that copy-lint FAILs is waived hit by hit, the brief as the reason (a word inside the client's name, as the logo or the title writes it, is not counted: one WARN).

7. **Report:** the `GATE:` line first, then every waiver with its reason and every open FAIL; the kind, the deal (palette and why it fits, pairing, hero, grounds, effect, moments, scene); the voice card in one line and every copy-lint WARN kept, with why; the checker, layout and perf results; what you could not check; every assumed fact (the checker's `assumed` list) and the coined name's search; the form's `.example` stand-in and the canonical domain still to come; the photographs and art the client must supply, every stand-in frame among them (library and live search); every client slot, its file and its stand-in.

