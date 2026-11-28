---
name: ctf-misc
description: >-
  When to read: a CTF challenge fits no main category. Use for: miscellaneous techniques —
  encoding puzzles, pyjails, bash jails, RF/SDR, DNS oddities, unicode tricks, esoteric
  languages, QR/audio puzzles, and constraint solving. Does: fallback for genuine cross-category
  or edge-case challenges; prefer a specific skill first when the challenge is mainly web, pwn,
  reverse, forensics, malware, OSINT, or crypto.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch Skill
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# CTF Miscellaneous

Quick reference for miscellaneous CTF challenges; full details in the supporting files.

## Prerequisites

**Python packages (all platforms):**
```bash
pip install "pwntools==4.15.0" "segno==1.6.6" z3-solver Pillow numpy requests dnslib
```

**Linux (apt):**
```bash
apt install libzbar0 qrencode ffmpeg
```

**macOS (Homebrew):**
```bash
brew install ffmpeg qrencode
```

**Manual install:**
- SageMath — Linux: `apt install sagemath`, macOS: `brew install --cask sage`

## Additional Resources

- [pyjails.md](pyjails.md) — Python jail escapes, quines, repunits, func_globals, f-string injection
- [bashjails.md](bashjails.md) — Bash jail escapes, HISTFILE, bash -v, ctypes.sh
- [encodings.md](encodings.md) — Encodings, QR codes, esolangs, UTF-16, BCD, auto-decoding
- [encodings-advanced.md](encodings-advanced.md) — Verilog/HDL, Gray code, RTF, SMS PDU, UTF-9, hex Sudoku, TOPKEK, MaxiCode
- [audio.md](audio.md) — Audio stego: Morse extraction, spectrogram, SSTV, envelope timing
- [rf-sdr.md](rf-sdr.md) — RF/SDR/IQ: QAM-16, carrier recovery, timing sync
- [dns.md](dns.md) — DNS: ECS spoofing, NSEC walking, IXFR, rebinding, tunneling
- [games-and-vms.md](games-and-vms.md) — WASM patching, Roblox, PyInstaller, marshal, Python env RCE, Z3, K8s RBAC, MRO escape
- [games-and-vms-2.md](games-and-vms-2.md) — Cookie checkpoint brute-forcing, Flask cookie leakage, WebSocket, time-only bypass, De Bruijn, Brainfuck, WASM memory
- [games-and-vms-3.md](games-and-vms-3.md) — memfd_create binaries, crypto games, ROM-switching, marshal injection, Benford bypass, oracle relay, emoji C jail, BuildKit secrets, Docker escape, Levenshtein oracle, taint bypass
- [games-and-vms-4.md](games-and-vms-4.md) — XSLT as VM, MAX_SAFE_INTEGER, DSL oracle, blind SQLi via timeout, OEIS, QR reassembly, Fibonacci/Tribonacci, Selenium + Tesseract CAPTCHA, Brainfuck→Piet
- [linux-privesc.md](linux-privesc.md) — Sudo wildcard injection, sudoers.d pcap, monit injection, Apache -d, backup cronjob SUID, PostgreSQL RCE, NFS, SSH tunneling, PaperCut, Squid, Zabbix
- [ctfd-navigation.md](ctfd-navigation.md) — CTFd API without browser: token auth, listing, downloads, submission, scoreboard, Python client

---

## When to Pivot

- Crypto/number theory centred → `/ctf-crypto`.
- Real binary exploit (not jail, toy VM, encoding) → `/ctf-pwn` or `/ctf-reverse`.
- Mostly files, images, audio, captures needing recovery first → `/ctf-forensics`.
- ML/AI techniques (model attacks, adversarial examples, LLM jailbreaks) → `/ctf-ai-ml`.
- NodeJS sandbox uses **vm2** (`npm ls vm2`): check **CVE-2023-37466** via `Promise[@@species]` with `nesting:true`; see `ctf-web/js-sandbox`.

## Quick Start Commands

```bash
# File identification
file mystery_file
xxd mystery_file | head -5

# Encoding detection
echo '<data>' | base64 -d
echo '<hex>' | xxd -r -p

# QR code
zbarimg qr.png
python3 -c "from pyzbar.pyzbar import decode; from PIL import Image; print(decode(Image.open('qr.png')))"

# Z3 constraint solving
python3 -c "from z3 import *; x=BitVec('x',32); s=Solver(); s.add(x^0xdead==0xbeef); s.check(); print(s.model())"

# Python jail test
python3 -c "__import__('os').system('id')"
```

## General Tips

- Read all files; check metadata, hidden content, encoding.
- Power Automate scripts may hide API calls.
- Binary-search multiple guesses.

## Common Encodings

```bash
# Base64
echo "encoded" | base64 -d

# Base32
echo "OBUWG32D..." | base32 -d

# Hex
echo "68656c6c6f" | xxd -r -p

# ROT13
echo "uryyb" | tr 'a-zA-Z' 'n-za-mN-ZA-M'
```

**Identify by charset:** Base64 `A-Za-z0-9+/=`; Base32 `A-Z2-7=`; Hex `0-9a-fA-F`. Caesar brute force, URL encoding: [encodings.md](encodings.md).

## IEEE-754 Float Encoding (Data Hiding)

**Pattern:** float32 values hide raw bytes — reinterpret → ASCII.

```python
import struct
floats = [1.234e5, -3.456e-7, ...]  # Whatever the challenge gives
flag = b''
for f in floats:
    flag += struct.pack('>f', f)
print(flag.decode())
```

**Variations:** double `'>d'`, little-endian `'<f'`, mixed.

## USB Mouse PCAP Reconstruction

**Pattern:** USB HID mouse traffic captures on-screen keyboard typing. USB-Mouse-Pcap-Visualizer: click coordinates (falling edges), cumsum deltas, overlay on OSK image.

## Archive Extraction

```bash
7z x archive.7z
tar -xzf archive.tar.gz
tar -xjf archive.tar.bz2
tar -xJf archive.tar.xz
```

### Nested Archive Script
```bash
while f=$(ls *.tar* *.gz *.bz2 *.xz *.zip *.7z 2>/dev/null|head -1) && [ -n "$f" ]; do
    7z x -y "$f" && rm "$f"
done
```

## QR Codes

```bash
zbarimg qrcode.png       # Decode
qrencode -o out.png "data"
```

**MaxiCode:** hexagonal 2D barcode; decode with `zxing` (Java) — [encodings-advanced.md](encodings-advanced.md).
**TOPKEK:** `KEK=0`, `TOP=1`, `!` suffix = repeat count ([encodings-advanced.md](encodings-advanced.md)).
QR structure, repair, reassembly: [encodings.md](encodings.md).

## Audio Challenges

```bash
# Spectrogram (hidden text/images in frequency domain)
sox audio.wav -n spectrogram -o spec.png
sox audio.wav -n spectrogram -o spec.png -x 2048 -y 1025  # higher resolution

# Channel inspection
python3 -c "import wave; w=wave.open('audio.wav'); print(f'channels={w.getnchannels()}, rate={w.getframerate()}, width={w.getsampwidth()}')"

# SSTV (Slow Scan TV decoder)
qsstv                          # GUI
```

**Morse extraction:** beeps on one stereo channel. Split channels (L=even, R=odd); detect channel by peak-to-mean envelope ratio; RMS envelope (50ms), threshold; dots ~100–150ms, dashes ~250–350ms; gaps group characters. Script: [audio.md](audio.md).
**DTMF:** keypad tones → digits → multi-tap letters ([encodings-advanced.md](encodings-advanced.md)).
**Music note stego:** note pairs encode nibbles via scale degrees ([encodings-advanced.md](encodings-advanced.md)).
Full audio analysis: [audio.md](audio.md).

## RF / SDR / IQ Signal Processing

IQ formats, QAM-16 demod, carrier/timing recovery: [rf-sdr.md](rf-sdr.md).
**Quick reference:** **cf32**: `np.fromfile(path, dtype=np.complex64)` | **cs16**: int16 reshape(-1,2) | **cu8**: RTL-SDR raw. Circles = constant offset; spirals = drifting frequency + gain instability. 4-fold DD carrier ambiguity — try 0/90/180/270.

## pwntools Interaction

```python
from pwn import *

r = remote('host', port)
r.recvuntil(b'prompt: ')
r.sendline(b'answer')
r.interactive()
```

## Python Jail Quick Reference

- **Oracle pattern:** `L()` = length, `Q(i,x)` = compare, `S(guess)` = submit.
- **Walrus bypass:** `(abcdef := "new_chars")` reassigns constraint vars.
- **Decorator bypass:** `@__import__` + `@func.__class__.__dict__[__name__.__name__].__get__` (no-call, no-quotes).
- **String join:** `open(''.join(['fl','ag.txt'])).read()` when `+` is blocked.

See [pyjails.md](pyjails.md) for full techniques.

## Z3 / Constraint Solving

```python
from z3 import *
flag = [BitVec(f'f{i}', 8) for i in range(FLAG_LEN)]
s = Solver()
# Add constraints, check sat, extract model
```

YARA rules, type systems, boolean gate SAT: [games-and-vms.md](games-and-vms.md).

## Hash Identification

MD5: `0x67452301` | SHA-256: `0x6a09e667` | MurmurHash64A: `0xC6A4A7935BD1E995`

## SHA-256 Length Extension Attack

MAC = `SHA-256(SECRET || msg)`; known msg/hash → forge via `hlextend`. Vulnerable: SHA-256, MD5, SHA-1. NOT: HMAC, SHA-3.

```python
import hlextend
sha = hlextend.new('sha256')
new_data = sha.extend(b'extension', b'original_message', len_secret, known_hash_hex)
```

## Technique Quick References

- **PyInstaller:** `pyinstxtractor.py packed.exe`.
- **Marshal:** `marshal.load(f)`, then `dis.dis(code)`.
- **Python env RCE:** `PYTHONWARNINGS=ignore::antigravity.Foo::0` + `BROWSER="cmd"`.
- **WASM patching:** `wasm2wat` → flip minimax → `wat2wasm`.
- **Float precision:** large multipliers amplify FP errors.
- **K8s RBAC bypass:** SA token → impersonate → hostPath mount.
- **Cookie checkpoint:** save cookies, restore on failure.
- **Flask cookie game state:** `flask-unsign -d -c '<cookie>'` decodes unsigned sessions.
- **WebSocket teleport:** modify `player.x`/`player.y`, call verifier.
- **Time-only validation:** `time.sleep(required_seconds)`, submit win.
- **Quine context detection:** quine prints itself (passes validation); payload runs only in server process.
- **Repunit decomposition:** target as sum of repunits (1, 11, 111, …) using only `1` and `+`.
- **De Bruijn sequence:** B(k, n) contains all k^n n-length strings; append first n-1 chars.
- **Brainfuck instrumentation:** track tape cells, brute-force flag char-by-char.
- **WASM memory manipulation:** patch linear memory at runtime, set game state.
- **Lua sandbox escape:** `os["execute"]` indexing or `loadstring` alias.
- **C code jail via emoji + gadgets:** `(😃==😃)` = 1, build integers, embed gadgets in `add eax, imm32`.
- **Emulator ROM-switching:** `/load` replaces ROM, preserves CPU state; combine INIT of one ROM with display code of another.
- **BuildKit daemon exploitation:** exposed gRPC allows nested `buildctl build` with `--mount=type=secret`.
- **Docker container escape:** host device mount, docker.sock escape, CAP_SYS_ADMIN release_agent.
- **Taint bypass via type coercion:** if-expression secrecy depends on return type, not condition — coerce functions to private type.
- **Shredded document reassembly:** strip edge as bitmask (dark=1); XOR + popcount Hamming distance, greedy placement.
- **f-string config injection:** store payload as config value, create key `eval(stored_key)` → RCE.
- **Hex Sudoku + QR assembly:** 4 QR codes encode 16x16 hex Sudoku quadrants; solve, read diagonal as hex pairs.
- **Z3 boolean gate network SAT:** 250 gates over 125 input bits; model each gate, require all outputs True.

## 3D Printer Video Nozzle Tracking (LACTF 2026)

**Pattern (flag-irl):** video of 3D printer fabricating nameplate; flag is the printed text. Track nozzle X/Y, filter print moves (top/text layer only), plot 2D histogram → letters:
```python
# Text-layer frames (e.g., 26100-28350); track head X, bed X (physical Y);
# filter extrusion moves; plot 2D scatter/histogram -> letters appear
```

## Discord API Enumeration (0xFun 2026)

Flags hidden in Discord metadata (roles, animated emoji, embeds). Invoke `/ctf-osint`.

---

## SUID Binary Exploitation (0xFun 2026)

```bash
# Find SUID binaries
find / -perm -4000 2>/dev/null

# Cross-reference with GTFObins
# xxd: xxd flag.txt | xxd -r
# vim: vim -c ':!cat /flag.txt'
```

**Reference:** https://gtfobins.github.io/

---

## Linux Privilege Escalation Quick Checks

```bash
# GECOS field passwords
cat /etc/passwd  # 5th field

# ACL permissions
getfacl /path/to/restricted/file

# Sudo permissions
sudo -l
```

## Docker Group Privilege Escalation (H7CTF 2025)

User in the `docker` group = root: the socket allows privileged containers mounting the host filesystem.

```bash
id  # check groups
docker run -v /:/mnt --rm -it alpine chroot /mnt /bin/sh
cat /root/flag.txt
```

**Reference:** https://gtfobins.github.io/gtfobins/docker/

## Sudo Wildcard Parameter Injection (Dump HTB)

Sudo `fnmatch()` matches `*` across argument boundaries — inject flags (`-Z root`, `-r`, second `-w`). Craft pcap with valid sudoers entries; sudo's parser recovers from binary junk, unlike cron's.

## Monit Process Command-Line Injection (Zero HTB)

Root monit extracts command lines via `pgrep -lfa`, executes a modified version. Fake process via `perl -e '$0 = "..."'` with injected flags. Apache `-d` last-wins overrides ServerRoot; `-E` captures output; `Include /root/flag` parse error reveals content.

## PostgreSQL RCE and File Read (Slonik HTB)

`COPY (SELECT '') TO PROGRAM 'cmd'` = OS commands as postgres; `pg_read_file('/path')` reads files. Credentials in `pg_basebackup` archives (`global/1260`). SSH tunnel: `ssh -fNL 25432:/var/run/postgresql/.s.PGSQL.5432`.

## Backup Cronjob SUID Abuse (Slonik HTB)

Root cronjob copying directories preserves SUID but changes ownership to root. Place SUID bash in source dir → backup copies it as root-owned SUID; run `bash -p`.

## PaperCut Print Deploy Privesc (Bamboo HTB)

Root process runs scripts from user-owned directory; modify `server-command`, trigger via Mobility Print API refresh.

---

## CTFd Platform Navigation (No Browser)

Detect CTFd via `curl -s "$CTF_URL/api/v1/" | head -5`. **Ask the user for their API token** (CTFd Settings > Access Tokens); use `Authorization: Token $CTF_TOKEN`.

```bash
export CTF_URL="https://ctf.example.com" CTF_TOKEN="ctfd_your_token_here"
curl -s -H "Authorization: Token $CTF_TOKEN" "$CTF_URL/api/v1/challenges" | jq -r '.data[] | "\(.id)\t\(.value)pts\t\(.category)\t\(.name)"'
curl -s -X POST -H "Authorization: Token $CTF_TOKEN" -H "Content-Type: application/json" "$CTF_URL/api/v1/challenges/attempt" -d "{\"challenge_id\": $CID, \"submission\": \"flag{...}\"}"
```

Full workflow, Python client, login, hints, downloads: [ctfd-navigation.md](ctfd-navigation.md).

---

## Useful One-Liners

```bash
grep -rn "flag{" .
strings file | grep -i flag
python3 -c "print(int('deadbeef', 16))"
```

## Keyboard Shift Cipher

**Pattern (Frenzy):** chars shifted on QWERTY layout. Decode with [dCode Keyboard Shift Cipher](https://www.dcode.fr/keyboard-shift-cipher) (automatic mode).

## Pigpen / Masonic Cipher

**Pattern (Working For Peanuts):** geometric symbols = letters by grid positions ("Peanuts" comic). Map symbols to Pigpen grid or use online decoder.

## ASCII in Numeric Data Columns

**Pattern (Cooked Books):** CSV numeric values (48-126) are ASCII codes.

```python
import csv
with open('data.csv') as f:
    reader = csv.DictReader(f)
    flag = ''.join(chr(int(row['Times Borrowed'])) for row in reader)
print(flag)
```

**CyberChef:** "From Decimal", line feed delimiter.

## Backdoor Detection in Source Code

**Pattern (Rear Hatch):** hidden command prefix triggers `system()`. E.g. `strncmp(input, "exec:", 5)` → `system(input + 5)`; hex-encoded comparisons (`\x65\x78\x65\x63\x3a` = "exec:"); hidden conditions in admin functions.

## DNS Exploitation Techniques

**ECS spoofing**: `dig @server flag.example.com TXT +subnet=10.13.37.1/24` (try leet IPs). **NSEC walking**: follow NSEC chain. **IXFR**: `dig @server domain IXFR=0` when AXFR blocked. **DNS rebinding**: low-TTL alternating resolution. **DNS tunneling**: data via subdomains or TXT. Full details: [dns.md](dns.md).

## Unicode Steganography

### Variation Selectors Supplement (U+E0100-U+E01EF)
**Patterns (Seen & emoji, Nullcon 2026):** invisible Variation Selectors encode ASCII via codepoint offset.

```python
# Extract hidden data from variation selectors after visible character
data = open('README.md', 'r').read().strip()
hidden = data[1:]  # Skip visible emoji character
flag = ''.join(chr((ord(c) - 0xE0100) + 16) for c in hidden)
```

**Detection:** invisible chars, non-zero length; check `[hex(ord(c)) for c in text]` for `0xE0100-0xE01EF` / `0xFE00-0xFE0F`.

### Unicode Tags Block (U+E0000-U+E007F) (UTCTF 2026)

**Pattern (Hidden in Plain Sight):** invisible Unicode Tags in URLs, filenames, or text; each maps to ASCII by subtracting `0xE0000` (URL-encoded as 4-byte UTF-8). Zero-width; text looks normal but byte length is suspiciously long.

```python
import urllib.parse

url = "https://example.com/#%F3%A0%81%B5%F3%A0%81%B4..."
decoded = urllib.parse.unquote(urllib.parse.urlparse(url).fragment)

flag = ''.join(
    chr(ord(ch) - 0xE0000)
    for ch in decoded
    if 0xE0000 <= ord(ch) <= 0xE007F
)
print(flag)
```


## UTF-16 Endianness Reversal

**Pattern (endians):** text "turned to Japanese" — UTF-16 endianness mojibake.

```python
# If encoded as UTF-16-LE but decoded as UTF-16-BE:
fixed = mojibake.encode('utf-16-be').decode('utf-16-le')
```

**Identification:** CJK characters, "translation"/"endian" hints.

## Cipher Identification Workflow

1. **ROT13** — garbled English
2. **Base64** — `A-Za-z0-9+/=`, title hints "64"
3. **Base32** — `A-Z2-7=` uppercase only
4. **Atbash** — title hints, 1:1
5. **Pigpen** — geometric symbols
6. **Keyboard Shift** — text looks like adjacent keys
7. **Substitution** — frequency analysis

**Auto-identify:** [dCode Cipher Identifier](https://www.dcode.fr/cipher-identifier)

## HISTFILE Trick for Restricted Shell File Reads (BCTF 2016)

Read files without cat/less/head: `HISTFILE=/flag /bin/bash && history`, `bash -v flag.txt` (verbose mode), or `ctypes.sh` `dlcall` (direct C calls).

## Levenshtein Distance Oracle Attack (SunshineCTF 2016)

Oracle returns edit distance. Length from empty string, present chars from single-char repeats, binary search positions. O(n log n) queries.

## SECCOMP High-Bit File Descriptor Bypass (33C3 CTF 2016)

`close(0x8000000000000002)` passes 64-bit SECCOMP check (≠ 2) but kernel truncates to 32-bit (== 2), closing fd 2; next `open()` returns fd 2 for arbitrary file. BPF/kernel width mismatch.

## rvim Jail Escape via Python3 (BKP 2017)

`rvim` blocks `:!` but `:python3 import os; os.system("cmd")` executes commands; check `:version` for `+python3`/`+lua`/`+ruby`.
