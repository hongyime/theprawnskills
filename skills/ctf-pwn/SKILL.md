---
name: ctf-pwn
description: >-
  When to read: a vulnerable native target or service must become code execution. Use for:
  binary exploitation — buffer overflows, format strings, heap bugs, ROP, ret2libc, shellcode,
  kernel exploitation, seccomp bypass, and sandbox escape. Does: one-liner per technique; full
  details in supporting files. Not for understanding what a binary does (use reverse engineering
  first) or for web/forensics/crypto challenges.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# CTF Binary Exploitation (Pwn)

Quick reference for binary exploitation (pwn) CTF challenges. Each technique has a one-liner here; see supporting files for full details.

## Prerequisites

**Python packages (all platforms):**
```bash
pip install "pwntools==4.15.0" "ROPgadget==7.7" "ropper==1.13.13"
# or via script: bash ../../scripts/install_ctf_tools.sh python
```

> **Manual-only:** the CTF tools installer (`../../scripts/install_ctf_tools.sh` at the repo root) is NEVER auto-run on fleet rollout — it uses sudo and installs system packages. Run only when Bryan asks, with `--dry-run` first.

**uv alternative:**
```bash
uv venv && uv pip install "pwntools==4.15.0" "ROPgadget==7.7" "ropper==1.13.13"
```

**Linux (apt):**
```bash
apt install gdb binutils strace ltrace qemu-system-x86
```

**Optional cross-arch (ARM/MIPS — Debian/Ubuntu):**
```bash
apt install qemu-user qemu-user-static gdb-multiarch binutils-multiarch libc6-armhf-cross libc6-arm64-cross libc6-mips-cross
```

**macOS (Homebrew):**
```bash
brew install gdb binutils qemu
```

**Ruby gems (all platforms):**
```bash
gem install one_gadget seccomp-tools
```

**Manual install:**
- pwndbg — Linux: [GitHub](https://github.com/pwndbg/pwndbg), macOS: `brew install pwndbg/tap/pwndbg-gdb`
- checksec — included with pwntools (`checksec --file=binary`)

**MCP servers (optional):** WinDbg MCP ([svnscha/mcp-windbg](https://github.com/svnscha/mcp-windbg)) for Windows crash dumps, live breakpoint-driven exploitation, and kernel/driver debugging; IDA Pro MCP / Ghidra MCP for decompiling the vulnerable function — see [tools-mcp.md](tools-mcp.md).

## Additional Resources

- [overflow-basics.md](overflow-basics.md) - Stack/global buffer overflow, ret2win, canary bypass/brute force, struct pointer overwrite, signed integer bypass, parser stack overflow
- [rop-and-shellcode.md](rop-and-shellcode.md) - Core ROP chains (ret2libc, syscall ROP, rdx control), ret2csu, bad-char XOR bypass, exotic gadgets, stack pivot, shellcode stubs
- [rop-advanced.md](rop-advanced.md) - Advanced ROP: double stack pivot, SROP, seccomp bypass (incl. RETF x64→x32), .fini_array hijack, ret2vdso, blind exfiltration
- [format-string.md](format-string.md) - Format string exploitation: leaks, GOT overwrite, blind pwn, filter bypass, canary leak, __free_hook, encoded format strings
- [advanced.md](advanced.md) - Seccomp advanced techniques, UAF, JIT, ret2dlresolve, basic kernel exploitation
- [heap-techniques.md](heap-techniques.md) - House of Apple 2, Einherjar, Orange/Spirit/Lore/Force, heap grooming, custom allocators, unlink, musl heap, tcache attacks
- [heap-techniques-2.md](heap-techniques-2.md) - CTF-writeup heap variants: UAF, tcache poisoning/double-free, cross-bin attacks, unsorted-bin leaks, unsafe unlink
- [heap-fsop.md](heap-fsop.md) - FILE-structure (_IO_FILE) exploitation: stdout/stdin vtable hijacks, vtable validation bypass, unsorted-bin attacks
- [advanced-exploits.md](advanced-exploits.md) - Advanced exploits (part 1): VM/JIT, type confusion, off-by-one, ASAN, FSOP + seccomp bypass
- [advanced-exploits-2.md](advanced-exploits-2.md) - Advanced exploits (part 2): io_uring UAF, integer truncation, leakless libc, FSOP/TLS hijacks
- [advanced-exploits-4.md](advanced-exploits-4.md) - Advanced exploits (part 4): Windows SEH/CFG, ARM/Thumb, Forth, NN function-pointer OOB, unique-byte bypass
- [advanced-exploits-3.md](advanced-exploits-3.md) - Advanced exploits (part 3): OOB reads/writes, JIT sandbox escape, DNS/ELF bypasses, timing side-channel shellcode
- [advanced-exploits-5.md](advanced-exploits-5.md) - Advanced exploits (part 5): data-interpretation — Chip-8 OOB, float quicksort canary, bloom filter OOB
- [sandbox-escape.md](sandbox-escape.md) - Custom VM exploitation, FUSE/CUSE, busybox/restricted shell, sandbox bypasses
- [kernel.md](kernel.md) - Linux kernel exploitation fundamentals: setup, QEMU debug, heap spray, privesc, modprobe_path/core_pattern
- [kernel-techniques.md](kernel-techniques.md) - Kernel techniques: tty_struct kROP, userfaultfd races, SLUB internals, cross-cache attacks, addr_limit bypass
- [kernel-bypass.md](kernel-bypass.md) - Kernel protection bypass: KASLR/FGKASLR, KPTI, SMEP/SMAP, GDB module debugging
- [field-notes.md](field-notes.md) - Detailed pwn notes: heap quick reference, additional exploit notes, useful commands
- [attack-playbook.md](attack-playbook.md) - Linux userland attack playbook: recon, leak selection, primitive ranking
- [static-signals.md](static-signals.md) - Exploit-relevant static signals for exploitability assessment
- [pwnable-tw/README.md](pwnable-tw/README.md) - 43 pwnable.tw writeups with per-challenge environment, protections, and exploitation chains
- [tools-mcp.md](tools-mcp.md) - MCP server integration: WinDbg MCP (dumps, breakpoints, kd), IDA/Ghidra MCP for exploit development

---

## When to Pivot

- If you do not yet understand what the binary does, switch to `/ctf-reverse` before trying to exploit it.
- If the service is really a restricted shell, encoding puzzle, or sandbox language challenge, switch to `/ctf-misc`.
- If the exploit path depends on a web endpoint, session bug, or upload primitive more than memory corruption, switch to `/ctf-web`.
- If the vulnerability requires breaking a cryptographic primitive before exploitation, switch to `/ctf-crypto`.

## Quick Start Commands

```bash
# Binary analysis
checksec --file=binary
file binary
readelf -h binary

# Find gadgets
ROPgadget --binary binary | grep "pop rdi"
ropper -f binary --search "pop rdi"
one_gadget /lib/x86_64-linux-gnu/libc.so.6

# Debug
gdb -q binary -ex 'start' -ex 'checksec'

# Pattern for offset finding
python3 -c "from pwn import *; print(cyclic(200))"
python3 -c "from pwn import *; print(cyclic_find(0x61616168))"

# libc identification
./libc-database/find puts <leaked_addr_last_3_nibbles>
```

## Source Code Red Flags

- Threading/`pthread` -> race conditions
- `usleep()`/`sleep()` -> timing windows
- Global variables in multiple threads -> TOCTOU

## Race Condition Exploitation

```bash
bash -c '{ echo "cmd1"; echo "cmd2"; sleep 1; } | nc host port'
```

## Common Vulnerabilities

- Buffer overflow: `gets()`, `scanf("%s")`, `strcpy()`
- Format string: `printf(user_input)`
- Integer overflow, UAF, race conditions

## Protection Implications for Exploit Strategy

| Protection | Status | Implication |
|-----------|--------|-------------|
| PIE | Disabled | All addresses (GOT, PLT, functions) are fixed - direct overwrites work |
| RELRO | Partial | GOT is writable - GOT overwrite attacks possible |
| RELRO | Full | GOT is read-only - need alternative targets (hooks, vtables, return addr) |
| NX | Enabled | Can't execute shellcode on stack/heap - use ROP or ret2win |
| Canary | Present | Stack smash detected - need leak or avoid stack overflow (use heap) |

**Quick decision tree:**
- Partial RELRO + No PIE -> GOT overwrite (easiest, use fixed addresses)
- Full RELRO -> target `__free_hook`, `__malloc_hook` (glibc < 2.34), or return addresses
- Stack canary present -> prefer heap-based attacks or leak canary first

## Stack Buffer Overflow

1. Find offset: `cyclic 200` then `cyclic -l <value>`
2. Check protections: `checksec --file=binary`
3. No PIE + No canary = direct ROP
4. Canary leak via format string or partial overwrite
5. Canary brute-force byte-by-byte on forking servers (7*256 attempts max)

**ret2win with magic value:** Overflow -> `ret` (alignment) -> `pop rdi; ret` -> magic -> win(). **Stack alignment:** SIGSEGV in `movaps` = add extra `ret` gadget. **Offset:** buffer at `rbp - N`, return at `rbp + 8`, total = N + 8. **Input filtering:** assert payload avoids `memmem()` banned strings. **Gadgets:** `ROPgadget --binary binary | grep "pop rdi"`, or pwntools `ROP()` for hidden gadgets in CMP immediates. See [overflow-basics.md](overflow-basics.md) for full exploit code.

## Parser Stack Overflow (Unchecked memcpy)

**Pattern:** Custom file parser (PCAP, image, archive) allocates fixed stack buffer but input records can exceed it. `memcpy` copies before length validation, overflowing saved registers and return address. Must restore callee-saved registers: `rbx` to readable memory (BSS), loop counters to exit values, then `ret` gadget + win function. See [overflow-basics.md](overflow-basics.md#parser-stack-overflow-via-unchecked-memcpy-length-metactf-flash-2026).

## Struct Pointer Overwrite (Heap Menu Challenges)

**Pattern:** Menu create/modify/delete on structs with data buffer + pointer. Overflow name into pointer field with GOT address, then write win address via modify. See [overflow-basics.md](overflow-basics.md) for full exploit and GOT target selection table.

## Signed Integer Bypass

**Pattern:** `scanf("%d")` without sign check; negative quantity * price = negative total, bypasses balance check. See [overflow-basics.md](overflow-basics.md).

## Canary-Aware Partial Overflow

**Pattern:** Overflow `valid` flag between buffer and canary. Use `./` as no-op path padding for precise length. See [overflow-basics.md](overflow-basics.md) and [advanced.md](advanced.md) for full exploit chain.

## Global Buffer Overflow (CSV Injection)

**Pattern:** Adjacent global variables; overflow via extra CSV delimiters changes filename pointer. See [overflow-basics.md](overflow-basics.md) and [advanced.md](advanced.md) for full exploit.

## ROP Chain Building

Leak libc via `puts@PLT(puts@GOT)`, return to vuln, stage 2 with `system("/bin/sh")`. See [rop-and-shellcode.md](rop-and-shellcode.md) for full two-stage ret2libc pattern, leak parsing, and return target selection.

**DynELF libc discovery:** `pwntools.DynELF(leak_func, pointer_in_libc)` resolves libc symbols remotely without knowing the libc version. See [rop-and-shellcode.md](rop-and-shellcode.md#dynelf-automated-libc-discovery-rc3-ctf-2016).

**Constrained shellcode in small buffers:** When buffer is too small, use `read()` shellcode stub (< 20 bytes) to pull full stage-2 shellcode. See [rop-and-shellcode.md](rop-and-shellcode.md#constrained-shellcode-in-small-buffers-tum-ctf-2016).

**Raw syscall ROP:** When `system()`/`execve()` crash (CET/IBT), use `pop rax; ret` + `syscall; ret` from libc. See [rop-and-shellcode.md](rop-and-shellcode.md).

**ret2csu:** `__libc_csu_init` gadgets control `rdx`, `rsi`, `edi` and call any GOT function — universal 3-argument call without libc gadgets. See [rop-and-shellcode.md](rop-and-shellcode.md#ret2csu--__libc_csu_init-gadgets-crypto-cat).

**Bad char XOR bypass:** XOR payload data with key before writing to `.data`, then XOR back in place with ROP gadgets. Avoids null bytes, newlines, and other filtered characters. See [rop-and-shellcode.md](rop-and-shellcode.md#bad-character-bypass-via-xor-encoding-in-rop-crypto-cat).

**Exotic gadgets (BEXTR/XLAT/STOSB/PEXT):** When standard `mov` write gadgets are unavailable, chain obscure x86 instructions for byte-by-byte memory writes. See [rop-and-shellcode.md](rop-and-shellcode.md#exotic-x86-gadgets--bextrxlatstosbpext-crypto-cat).

**Stack pivot (xchg rax,esp):** Swap stack pointer to attacker-controlled heap/buffer when overflow is too small for full ROP chain. Requires `pop rax; ret` to load pivot address first. See [rop-and-shellcode.md](rop-and-shellcode.md#stack-pivot-via-xchg-raxesp-crypto-cat).

**rdx control:** After `puts()`, rdx is clobbered to 1. Use `pop rdx; pop rbx; ret` from libc, or re-enter binary's read setup + stack pivot. See [rop-and-shellcode.md](rop-and-shellcode.md).

**Canary XOR epilogue as rdx zeroing gadget:** When no `pop rdx; ret` exists, jump into the canary check epilogue `xor rdx, fs:28h` -- it zeros RDX when the canary is intact. See [rop-and-shellcode.md](rop-and-shellcode.md#stack-canary-xor-epilogue-as-rdx-zeroing-gadget-volgactf-2017).

**stub_execveat as execve alternative:** When no `pop rax; ret` exists, use `stub_execveat` (syscall 322/0x142) instead of `execve` -- send exactly 0x142 bytes so `read()` return value sets rax. See [rop-and-shellcode.md](rop-and-shellcode.md#stub_execveat-syscall-as-execve-alternative-asis-ctf-2018).

**Shell interaction:** After `execve`, `sleep(1)` then `sendline(b'cat /flag*')`. See [rop-and-shellcode.md](rop-and-shellcode.md).

## Format String Through Input Transformation

**ROT13-encoded format string:** When input is ROT13/Caesar-transformed before reaching `printf`, pre-encode the format string payload with the inverse transform so it arrives intact. See [format-string.md](format-string.md#format-string-exploit-through-rot13-encoding-sunshinectf-2018).

## Kernel Exploitation

**addr_limit bypass via failed file open:** When a kernel module sets `addr_limit = KERNEL_DS` but fails to restore it on error paths, force the error (e.g., make target file a directory) to retain kernel memory access from userspace `read()`/`write()`. See [kernel-techniques.md](kernel-techniques.md#kernel-addr_limit-bypass-via-failed-file-open-midnight-sun-ctf-2018).

## Sandbox and Emulator Escape

**CPU emulator eval injection:** When an emulator's print opcode uses `eval('"' + buf + '"')` for escape sequences, build `"+__import__("os").system("cmd")#` in emulator memory via ADD opcodes to escape the string and execute Python. See [sandbox-escape.md](sandbox-escape.md#cpu-emulator-print-opcode-python-eval-injection-midnight-sun-ctf-2018).

## Advanced Exploit Primitives

**Neural network function pointer OOB:** When a binary uses NN output as an index into a function pointer array without bounds checking, retrain weights/biases to produce an out-of-bounds index that reads a target address from the biases array. See [advanced-exploits-4.md](advanced-exploits-4.md#neural-network-output-as-function-pointer-index-oob-swampctf-2018).

**Shellcode unique-byte limit bypass via counter overflow:** When shellcode is limited to N unique bytes, spray the stack to corrupt the `seen[256]` counter, then re-execute main (skipping `memset`) so the overflowed counter allows arbitrary bytes on the second run. See [advanced-exploits-4.md](advanced-exploits-4.md#shellcode-unique-byte-limit-bypass-via-counter-overflow-blaze-ctf-2018).

## Deep-Dive Notes

Use [field-notes.md](field-notes.md) once you have confirmed the challenge is truly exploitation-heavy.
