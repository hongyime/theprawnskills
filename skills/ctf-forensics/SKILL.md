---
name: ctf-forensics
description: >-
  When to read: a CTF challenge involves disk images, memory dumps, PCAP, or steganography. Use
  for: digital forensics and signal analysis — Volatility, network captures, crypto
  transactions, registry, Docker images, coredumps, DTMF spectrograms, and deleted-file
  recovery. Does: one-liner per technique; full details in supporting files.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# CTF Forensics & Blockchain

Quick reference for forensics CTF challenges. Each technique has a one-liner here; see supporting files for full details.

## Prerequisites

**Python packages (all platforms):**
```bash
pip install volatility3 Pillow numpy matplotlib scipy librosa scikit-learn opencv-python-headless pymongo impacket brotli exrex stegano heatshrink2
```

**Linux (apt):**
```bash
apt install binwalk foremost libimage-exiftool-perl tshark sleuthkit \
  ffmpeg steghide testdisk john pcapfix
```

**macOS (Homebrew):**
```bash
brew install binwalk exiftool wireshark sleuthkit ffmpeg \
  testdisk john-jumbo
```

**Ruby gems (all platforms):**
```bash
gem install zsteg
```

## Additional Resources

- [3d-printing.md](3d-printing.md) - 3D printing forensics (PrusaSlicer binary G-code, QOIF)
- [windows.md](windows.md) - Windows forensics (registry, SAM)
- [network.md](network.md) - Network forensics (tcpdump, TLS keylog decryption)
- [network-advanced.md](network-advanced.md) - Advanced network forensics (NTLMv2 cracking, DNS steganography)
- [peripheral-capture.md](peripheral-capture.md) - USB/HID/Bluetooth traffic reconstruction (HID mouse drawing, keyboard decoding)
- [disk-and-memory.md](disk-and-memory.md) - Core disk/memory forensics (Volatility, disk carving)
- [disk-advanced.md](disk-advanced.md) - Advanced disk/memory (deleted partitions, ZFS)
- [disk-recovery.md](disk-recovery.md) - Disk recovery (LUKS master key, BTRFS snapshots)
- [steganography.md](steganography.md) - General steganography (PDF multi-layer, SVG keyframes)
- [stego-image.md](stego-image.md) - Image steganography (JPEG DQT LSB, BMP bitplane QR)
- [stego-advanced.md](stego-advanced.md) - Advanced steganography 1: audio/signal (FFT, DTMF)
- [stego-advanced-2.md](stego-advanced-2.md) - Advanced steganography 2: video/transform (frame accumulation, Cat Map)
- [linux-forensics.md](linux-forensics.md) - Linux/app forensics (log analysis, Docker images)
- [signals-and-hardware.md](signals-and-hardware.md) - Hardware signal decoding (VGA/HDMI, UART)

---

## When to Pivot

- Encrypted blob → RSA/AES/lattice work → `/ctf-crypto`.
- Malware staging, beacon config extraction, packed samples → `/ctf-malware`.
- Web app backup or API dump, application logic → `/ctf-web`.
- Encoding puzzle, steganography trick, esoteric format → `/ctf-misc`.
- Trace infrastructure, attribute actors, public records → `/ctf-osint`.
- Compiled binary or firmware needing disassembly → `/ctf-reverse`.

## Quick Start Commands

```bash
# File analysis
file suspicious_file
exiftool suspicious_file     # Metadata
binwalk suspicious_file      # Embedded files
strings -n 8 suspicious_file
hexdump -C suspicious_file | head  # Check magic bytes

# Memory forensics (Volatility 3)
vol -f memory.dmp windows.info
vol -f memory.dmp windows.pslist
vol -f memory.dmp windows.filescan
```

## Log Analysis

```bash
grep -iE "(flag|part|piece|fragment)" server.log     # Flag fragments
grep "FLAGPART" server.log | sed 's/.*FLAGPART: //' | uniq | tr -d '\n'  # Reconstruct
sort logfile.log | uniq -c | sort -rn | head         # Find anomalies
```

## Windows Event Logs (.evtx)

**Key Event IDs:**
- 1001 - Bugcheck/reboot
- 1102 - Audit log cleared
- 4720 - User account created
- 4781 - Account renamed

**RDP Session IDs (TerminalServices-LocalSessionManager):**
- 21 - Session logon succeeded
- 24 - Session disconnected
- 1149 - RDP auth succeeded (RemoteConnectionManager, has source IP)

```python
import Evtx.Evtx as evtx
with evtx.Evtx("Security.evtx") as log:
    for record in log.records():
        print(record.xml())
```

- **NTFS Alternate Data Streams (ADS):** Hidden data in named NTFS streams, invisible to `dir`/Explorer. Detect with `fls -r image.dd | grep ":"`, extract with `icat`.

## When Logs Are Cleared

If attacker cleared event logs:
1. **USN Journal ($J)** - File operations timeline (MFT ref, timestamps, reasons)
2. **SAM registry** - Account creation from key last_modified timestamps
3. **PowerShell history** - ConsoleHost_history.txt (USN DATA_EXTEND = command timing)
4. **Defender MPLog** - Threat detections and ASR events
5. **Prefetch** - Program execution evidence
6. **User profile creation** - First login time (profile dir in USN journal)

## Steganography

```bash
steghide extract -sf image.jpg -p ""
zsteg image.png              # PNG/BMP analysis
stegsolve                    # Visual analysis
```

- **Binary border stego:** Black/white pixels in 1px image border encode bits clockwise
- **FFT frequency domain:** Image data hidden in 2D FFT magnitude spectrum; try `np.fft.fft2` visualization
- **DTMF audio:** Phone tones encoding data; decode with `multimon-ng -a DTMF`
- **Multi-layer PDF:** Check hidden comments, post-EOF data, XOR with keywords, ROT18 final layer
- **SSTV + LSB:** SSTV signal may be red herring; check 2-bit LSB of audio samples with `stegolsb`
- **SVG keyframes:** Animation `keyTimes`/`values` attributes encode binary/Morse via fill color alternation
- **PNG chunk reorder:** Fix chunk order: IHDR → ancillary → IDAT (in order) → IEND
- **File overlays:** Check after IEND for appended archives with overwritten magic bytes
- **APNG frame extraction:** Animated PNG has multiple frames; extract with `apngdis` or parse `fdAT`/`fcTL` chunks.
- **PNG height/CRC manipulation:** Modify IHDR height field, brute-force until CRC matches to reveal hidden rows.
- **Pixel coordinate chain stego:** Linked-list traversal where R=data byte, G/B=next pixel coordinates.
- **AVI frame differential:** XOR consecutive video frames to reveal hidden data in pixel differences.
- **Custom freq DTMF:** Non-standard dual-tone frequencies; spectrogram first, map custom grid to keypad digits, decode variable-length ASCII
- **JPEG DQT LSB:** Unused quantization tables (ID 2, 3) carry LSB data; extract bit 0 from each of 64 values via `Image.open().quantization`
- **Multi-track audio subtraction:** Two nearly-identical audio tracks in MKV/video; `sox -m` cancels shared content, flag in difference-signal spectrogram (5-12 kHz)
- **Packet interval timing:** Identical packets with two distinct interval values (e.g. 10ms/100ms) encode binary; compute inter-packet deltas, threshold to bits

## PDF Analysis

```bash
exiftool document.pdf        # Metadata (often hides flags!)
pdftotext document.pdf -     # Extract text
strings document.pdf | grep -i flag
binwalk document.pdf         # Embedded files
```

**Advanced PDF stego:** invisible text separators, URI annotations with escaped braces, Wiener deconvolution, vector rectangle QR codes, compressed object streams (`mutool clean -d`), document metadata fields.

## Disk / VM / Memory Forensics

```bash
# Disk images
sudo mount -o loop,ro image.dd /mnt/evidence
fls -r image.dd && photorec image.dd

# VM images (OVA/VMDK)
tar -xvf machine.ova
7z x disk.vmdk -oextracted "Windows/System32/config/SAM" -r

# Memory (Volatility 3)
vol -f memory.dmp windows.pslist
vol -f memory.dmp windows.cmdline
vol -f memory.dmp windows.netscan
vol -f memory.dmp windows.dumpfiles --physaddr <addr>

# String carving
strings -a -n 6 memdump.bin | grep -E "FLAG|SSH_CLIENT|SESSION_KEY"

# Coredump
gdb -c core.dump  # info registers, x/100x $rsp, find "flag"
```

## Windows Password Hashes

```bash
# Extract with impacket, crack with hashcat -m 1000
python -c "from impacket.examples.secretsdump import *; SAMHashes('SAM', LocalOperations('SYSTEM').getBootKey()).dump()"
```

## Bitcoin Tracing

- Use mempool.space API: `https://mempool.space/api/tx/<TXID>`
- **Peel chain:** ALWAYS follow LARGER output; round amounts indicate peels

## Uncommon File Magic Bytes

| Magic | Format | Extension | Notes |
|-------|--------|-----------|-------|
| `OggS` | Ogg container | `.ogg` | Audio/video |
| `RIFF` | RIFF container | `.wav`,`.avi` | Check subformat |
| `%PDF` | PDF | `.pdf` | Check metadata & embedded objects |
| `GCDE` | PrusaSlicer binary G-code | `.g`, `.bgcode` | See 3d-printing.md |

## Common Flag Locations

PDF metadata, image EXIF, deleted files (Recycle Bin `$R`), registry values, browser history, log fragments, memory strings.

## WMI Persistence Analysis

**Pattern (Backchimney):** WMI event subscriptions for persistence (MITRE T1546.003).

```bash
# Tool: https://github.com/davidpany/WMI_Forensics (run against a copy of OBJECTS.DATA)
python WMI_Forensics/PyWMIPersistenceFinder.py OBJECTS.DATA
```

- Look for FilterToConsumerBindings with CommandLineEventConsumer
- Base64-encoded PowerShell in consumer commands
- Event filters triggered on system events (logon, timer)

## Network Forensics Quick Reference

- **TFTP netascii:** Binary transfers corrupted; fix with `data.replace(b'\r\n', b'\n').replace(b'\r\x00', b'\r')`
- **TLS keylog decryption:** Import SSLKEYLOGFILE or RSA private key into Wireshark (Edit → Preferences → Protocols → TLS)
- **TLS weak RSA:** Extract cert, factor modulus, generate private key with `rsatool`, add to Wireshark
- **USB audio:** Extract isochronous data with `tshark -e usb.iso.data`, import as raw PCM in Audacity
- **NTLMv2 from PCAP:** Extract server challenge + NTProofStr + blob from NTLMSSP_AUTH, brute-force
- **WPA/WEP WiFi decryption:** `aircrack-ng -w wordlist capture.pcap` cracks WPA handshake; WEP cracked with enough IVs.
- **PCAP repair:** `pcapfix -d corrupted.pcap` repairs broken PCAP headers/checksums for Wireshark loading.
- **USB HID keyboard decoding:** Extract 8-byte HID reports from USB captures; byte 2 = keycode, byte 0 = modifiers (Shift).
- **dnscat2 reassembly:** Decode hex/base32 subdomain labels, strip 9-byte dnscat2 header, deduplicate retransmissions, reassemble payload.
- **USB keyboard LED exfiltration:** Host-to-device HID SET_REPORT packets toggle Caps Lock LED. Timing encodes Morse code.

## Browser Forensics

- **Chrome/Edge:** Decrypt `Login Data` SQLite with AES-GCM using DPAPI master key
- **Firefox:** Query `places.sqlite` -- `SELECT url FROM moz_places WHERE url LIKE '%flag%'`

## Additional Technique Quick References

### linux-forensics.md

- **Docker image forensics:** Config JSON preserves ALL `RUN` commands. `tar xf app.tar`, inspect config blob.
- **Linux attack chains:** Check `auth.log`, `.bash_history`, recent binaries, PCAP.
- **Git directory recovery:** `gitdumper.sh` for exposed `.git` dirs.
- **KeePass v4 cracking:** `keepass2john` lacks v4/Argon2; use `ivanmrsulja/keepass2john` fork or `keepass4brute`. Wordlists: `cewl`.
- **Git reflog/fsck squash recovery:** `git rebase --squash` leaves orphaned objects; `git fsck --unreachable --no-reflogs` recovers them.
- **Corrupted git blob repair:** Single-byte corruption changes SHA-1; brute-force each byte (256 × size), verify with `git hash-object`.
- **VBA macro cell data to binary:** Excel cells; `CByte((val-78)/3)` → ELF bytes. Reimplement in Python, never run the macro.
- **Python in-memory source recovery:** Attach `pyrasite-shell` to a running Python process; decompile `__code__` (`uncompyle6` <=3.8, `pycdc` 3.9+), dump `globals()`.

### disk-advanced.md

- **RAID 5 XOR recovery:** Two disks of a 3-disk RAID 5 → XOR to recover the third: `bytes(a ^ b for a, b in zip(disk1, disk3))`.
- **Kyoto Cabinet hash DB forensics:** Recover key ordering: insert sequential probe keys, binary-diff for each hash slot.
- **Linux ransomware + memory dump:** Raw-memory candidate scanning + magic-byte validation recovers AES key.
- **Deleted partitions:** `testdisk` or `kpartx -av`.
- **ZFS forensics:** Reconstruct labels, Fletcher4 checksums, PBKDF2 cracking.
- **APFS snapshot recovery:** `icat` with different XID offsets reads inodes across transaction IDs.
- **WordPerfect macro XOR:** `.wcm` macros; `(a+b)-2*(a&b)` = bitwise XOR.
- **HFS+ resource fork recovery:** Invisible to `binwalk`/`foremost`; HFSExplorer + 010 Editor template.
- **SQLite edit history reconstruction:** Replay insert/remove diffs to reconstruct every intermediate state.

### disk-and-memory.md

- **GIMP raw memory dump visual inspection:** Open `.dmp` in GIMP as raw RGB at monitor width (~1920); scroll for framebuffer screenshots.
- **PowerShell ransomware:** Extract scripts from minidump, find AES key, decrypt SMTP attachment.
- **BSON reconstruction:** Reassemble BSON from raw bytes; parse with `bson`.
- **TrueCrypt mounting:** `veracrypt --mount` or `cryptsetup open --type tcrypt` with known password.
- **Android forensics:** `adb pull` APK, `apktool`, check `shared_prefs/` and SQLite DBs.
- **Docker container forensics:** `docker save` layered tars; deleted files persist in earlier layers. `docker history --no-trunc` reveals secrets.
- **Cloud storage forensics:** Versioning preserves deleted objects; `list-object-versions` recovers them.
- **Windows KAPE triage:** Artifact ZIPs; PowerShell history → Amcache → MFT → registry hives.

### signals-and-hardware.md

- **Hardware signals:** VGA/HDMI TMDS/DisplayPort, Voyager audio, Saleae UART decode, Flipper Zero.
- **Caps-lock LED Morse from video:** Track LED pixel across camera frames; on/off durations encode Morse.
- **I2C protocol decoding:** Decode SDA/SCL captures to extract EEPROM/sensor data.
- **Punched card OCR:** Map hole positions to characters (IBM-29 grid).
- **Side-channel power analysis:** Average traces, max-variance sample, max-power guess at leak point.
- **Keyboard acoustic side-channel:** MFCC + KNN on keystroke audio; 10ms window.
- **Linux input_event keylogger parsing:** 24-byte `struct input_event`; filter `type==1`, `value==1`; map keycodes.
- **Serial UART from WAV audio:** Square wave encodes UART; determine baud, parse start/stop bits.
- **USB MIDI Launchpad grid reconstruction:** MIDI Note On/Off → 8x8 grid (`key = row*16 + col`); reconstruct patterns.

### peripheral-capture.md

- **USB HID mouse drawing:** Render relative movements per draw mode; skip pen lifts, scale 5-8x.

### stego-image.md

- **BMP bitplane QR:** Bitplanes 0-2 per RGB channel; hidden QR often in bit 1, not bit 0.
- **Image puzzle reassembly:** Edge-match piece borders, greedy grid placement.
- **F5 JPEG DCT detection:** ±1/±2 AC ratio drops ~3:1 → ~1:1 with F5.
- **PNG unused palette stego:** Unused PLTE entries carry data in red channel values.
- **Seed-based pixel permutation stego:** Fisher-Yates shuffle (known seed) + interleaved LSB from Y channel → hidden QR.
- **RGB parity steganography:** Sum R+G+B per pixel; even=white, odd=black renders hidden bitmap.

### stego-advanced.md

- **DeepSound audio stego with password cracking:** Extract hash with `deepsound2john.py`, crack with John, retrieve hidden files from WAV; check spectrogram too.
- **Audio FFT notes:** Dominant frequencies → note names (A-G) spell words.
- **Audio metadata octal:** Underscore-separated octal in Exiftool comment → ASCII/base64.
- **Cross-channel multi-bit LSB:** Different bit positions per RGB channel (R[0], G[1], B[2]).

### steganography.md

- **QR code reconstruction from curved reflection:** Flip, de-warp, known plaintext prefix; ECC corrects the rest.
- **Kitty terminal graphics:** `ESC_G` embeds zlib RGB image in base64 chunks; strip escapes, concatenate, decompress.
- **ANSI escape sequence stego:** Flag between ANSI color codes and braille; strip escapes/non-ASCII.
- **Autostereogram solving:** Duplicate layer, difference blend, shift ~100px horizontally to reveal hidden 3D text.
- **Two-layer byte+line interleaving:** Deinterleave even/odd bytes, then even/odd lines.
- **Multi-stream video container stego:** MP4/MKV, multiple streams; default is a red herring, flag in secondary stream. `ffprobe`, `ffmpeg -map 0:1`.

### 3d-printing.md

- **G-code visualization:** Side projections (XZ/YZ) reveal text.

### network-advanced.md

- **TCP flag covert channel:** 6 flag bits = 0-63, encoding base64.
- **Brotli decompression bomb seam:** Repeating blocks; flag breaks the pattern at a seam.
- **DNS trailing byte binary:** `0x30`/`0x31` after DNS question encode bits; 8-bit MSB-first → ASCII.
- **Fake TLS + mDNS key + printability merge:** TLS-disguised TCP hides ZIP; XOR key from mDNS TXT; merge printable characters.
- **SMB RID recycling:** Guest auth + `LsaLookupSids` with incrementing RIDs enumerates AD accounts.
- **Timeroasting (MS-SNTP):** NTP requests with machine RIDs → HMAC-MD5 hashes; hashcat -m 31300.
- **Hidden PDF objects:** Unreferenced streams not in `/Kids`; add to `/Kids`, bump `/Count`, re-render.

### disk-recovery.md

- **BTRFS snapshot recovery:** `mount -o subvol=@backup` accesses historical copies.
- **FAT16 free space recovery:** Parse FAT table; unallocated clusters (entry = 0x0000) hold data.
- **FAT16 deleted file recovery (fls/icat):** First directory-entry byte → `0xE5`; data remains. `fls -r -d`, `icat` by inode.
- **Ext2 orphaned inode recovery:** `e2fsck -y disk.img` reconnects to `/lost+found`.
- **Corrupted ZIP header repair:** Fix filename lengths in Local File Header (26) and Central Directory (28).

### stego-advanced-2.md

- **JPEG XL TOC permutation:** TOC permutation controls tile convergence order; truncate at increasing offsets to read it.
- **Video frame accumulation:** Flashing images at various positions; composite all frames (per-pixel max).
- **Reversed audio:** Garbled audio, speech played backwards; `sox audio.wav reversed.wav reverse` reveals the message.
- **Arnold's Cat Map descrambling:** Periodic chaotic transform on square images; iterate until original reappears.
- **High-resolution SSTV demodulation:** Manual FM demodulation via `arccos` + differentiation.
- **MJPEG FFD9 trailing byte stego:** Extra bytes after JPEG EOI (FFD9); split on FFD8, extract post-FFD9 data.

### network.md

- **TLS master key from coredump:** Session ID in coredump; 48 bytes before it = master key. Create pre-master-secret log.
- **Split archive reassembly from PCAP:** Same-sized MD5-named HTTP files; order by Apache timestamps, concatenate; password in TCP chat stream.

## Timeroasting / MS-SNTP Hash Extraction (Midnight 2026)

Extract crackable HMAC-MD5 hashes from MS-SNTP responses by sending NTP requests with machine account RIDs.

```bash
# Extract NTP payloads, convert to hashcat format, crack
tshark -r capture.pcapng -Y "ntp && ip.src == <DC_IP>" -T fields -e udp.payload
hashcat -m 31300 -a 0 -O hashes.txt rockyou.txt --username
```

## HTTP Exfiltration in PCAP

`tshark --export-objects http,/tmp/objects` extracts uploaded files instantly. Check multipart POST uploads, unusual User-Agent strings, exfiltrated files.

## Common Encodings

```bash
echo "base64string" | base64 -d
echo "hexstring" | xxd -r -p
# ROT13: tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

**ROT18:** ROT13 on letters + ROT5 on digits — common final layer in multi-stage forensics.
