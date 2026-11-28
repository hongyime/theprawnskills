---
name: ctf-crypto
description: >-
  When to read: a CTF challenge involves encryption, hashing, signatures, or crypto math. Use
  for: cryptography attack techniques — RSA, AES, ECC, lattices, Coppersmith, Pollard, Wiener,
  padding oracle, GCM, and stream/block cipher weaknesses. Does: one-liner per technique; full
  details with code in supporting files.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---


# CTF Cryptography

Quick reference for crypto CTF challenges. One-liner per technique; full details with code in the supporting files.

## Prerequisites

**Python packages (all platforms):**
```bash
pip install pycryptodome z3-solver sympy gmpy2 hashpumpy fpylll py_ecc
# Coppersmith (optional): pip install coppersmith
```

**Linux (apt):**
```bash
apt install hashcat
```

**macOS (Homebrew):**
```bash
brew install hashcat
```

**Manual install:**
- SageMath (optional, legacy fallbacks only) — `apt install sagemath` / `brew install --cask sage`
- RsaCtfTool — `git clone https://github.com/RsaCtfTool/RsaCtfTool` (automated RSA attacks)
- crypto-attacks (Coppersmith) — `git clone https://github.com/jvdsn/crypto-attacks ~/.ctf-tools/crypto-attacks` + `pip install -r ~/.ctf-tools/crypto-attacks/requirements.txt`

> **Note:** `gmpy2` needs libgmp — `apt install libgmp-dev` / `brew install gmp`.

## Additional Resources

- [classic-ciphers.md](classic-ciphers.md) — Vigenere, Atbash
- [modern-ciphers.md](modern-ciphers.md) — AES (CFB-8, ECB)
- [modern-ciphers-2.md](modern-ciphers-2.md) — Blum-Goldwasser oracle, hash length extension
- [modern-ciphers-3.md](modern-ciphers-3.md) — Custom hash reversal, CRC32 brute-force
- [modern-ciphers-4.md](modern-ciphers-4.md) — ChaCha20-Poly1305 nonce reuse, partitioning-oracle AEAD lattice
- [stream-ciphers.md](stream-ciphers.md) — LFSR (Berlekamp-Massey, correlation
- [rsa-attacks.md](rsa-attacks.md) — Small e, common modulus
- [rsa-attacks-2.md](rsa-attacks-2.md) — RSA p=q bypass, cube root CRT
- [ecc-attacks.md](ecc-attacks.md) — Small subgroup, invalid curve
- [dh-attacks.md](dh-attacks.md) — Trivial g (0/1/p-1), Pohlig-Hellman (p-1 smooth)
- [zkp-and-advanced.md](zkp-and-advanced.md) — ZKP 3-coloring, Z3 guide
- [prng.md](prng.md) — MT19937, MT float recovery via GF(2) matrix
- [prng-attacks.md](prng-attacks.md) — MT subset-sum seed recovery, MT19937 constraint propagation
- [historical.md](historical.md) — Lorenz SZ40/42, book cipher implementation
- [advanced-math.md](advanced-math.md) — Isogenies, Pohlig-Hellman
- [lattice-and-lwe.md](lattice-and-lwe.md) — LLL/BKZ/Babai, HNP from partial/biased nonces
- [post-quantum.md](post-quantum.md) — ML-KEM (Kyber), ML-DSA
- [exotic-crypto.md](exotic-crypto.md) — Braid group DH / Alexander polynomial, monotone inversion
- [exotic-crypto-2.md](exotic-crypto-2.md) — BB-84 QKD MITM, ElGamal trivial DLP

---

## When to Pivot

- Binary, obfuscated client, or weird VM → `/ctf-reverse`.
- Packet carving, disk recovery, stego first → `/ctf-forensics`.
- Exploit after crypto is solved → `/ctf-pwn` / `/ctf-web`.
- Adversarial ML, model extraction, neural ciphers → `/ctf-ai-ml`.
- Encoding puzzle, esoteric cipher, or polyglot trick → `/ctf-misc`.

## Quick Start Commands

```bash
# Identify cipher type
python3 -c "from Crypto.Util.number import *; n=<N>; print(f'bits={n.bit_length()}')"

# RSA quick check
python3 -c "from sympy import factorint; print(factorint(<n>))"  # Small factors?
openssl rsa -pubin -in key.pub -text -noout  # Extract n, e from PEM

# Quick factorization tools
python3 RsaCtfTool.py -n <n> -e <e> --uncipher <c>

# XOR analysis
python3 -c "from pwn import xor; print(xor(bytes.fromhex('<hex>'), b'flag{'))"

# Hash identification
hashcat --identify '<hash>'
```

## Classic Ciphers

- **Caesar:** frequency analysis or brute force 26 keys.
- **Vigenere:** known-plaintext attack with flag prefix; key from `(ct - pt) mod 26`.
- **Atbash:** A↔Z substitution; "Abashed" hints in challenge name.
- **Substitution wheel:** brute force all rotations of inner/outer mapping.
- **Multi-byte XOR:** split by key position, frequency-analyze each column (space = 0x20).
- **Cascade XOR:** brute force first byte (256 attempts), rest follows.
- **XOR rotation (power-of-2):** even/odd bits never mix; only 4 candidate states.
- **Weak XOR verification:** single-byte XOR check, 1/256 pass rate; brute force with budget.
- **Deterministic OTP:** known-plaintext XOR recovers keystream.
- **OTP key reuse (many-time pad):** `C1 XOR C2 XOR known_P = unknown_P`; crib dragging with no known plaintext.
- **Homophonic (variable-length):** multi-char groups map to single plaintext chars; identical sub-n-gram frequencies → symbols.
- **Grid permutation cipher:** 5x5 grid, independent row/column permutations → 5! × 5! = 14,400.
- **Image-based Caesar shift:** pixel rows/columns shifted by per-strip offsets; ASCII flag from shift amounts.
- **Polybius square cipher:** 5x5 grid maps letter pairs to plaintext.
- **XOR key recovery via file format headers:** file claims PDF/PNG/ZIP but `file` reports "data". XOR first bytes against expected magic bytes.

## Modern Cipher Attacks

- **AES-ECB:** byte-at-a-time suffix recovery (256 queries/byte, FeatherDuster `ecb_cpa_decrypt`); cut-and-paste forges JSON fields.
- **AES-CBC:** bit flipping changes plaintext; padding oracle decrypts without key.
- **CBC IV forgery + block truncation:** XOR IV bytes to change block 0; strip trailing blocks.
- **Padding oracle to CBC bitflip RCE:** chain padding oracle with bitflipping → command injection.
- **AES-CFB-8:** static IV, 8-bit feedback — state reconstruction after 16 known bytes.
- **CBC-MAC/OFB-MAC:** XOR keystream forgery: `new_sig = old_sig XOR block_diff`.
- **S-box collisions:** non-permutation S-box → 4,097-query key recovery.
- **GF(2) elimination:** linear hash functions (XOR + rotations) via Gaussian elimination over GF(2).
- **Padding oracle:** byte-by-byte decryption by modifying previous block, testing padding validity. ~4096 queries/16-byte block.
- **LFSR stream ciphers:** Berlekamp-Massey recovers feedback polynomial from 2L keystream bits.
- **Galois LFSR tap recovery:** XOR known file header with ciphertext → keystream; `(state >> 1) XOR next_state` for LSB=1 recovers tap mask.
- **OFB with invertible RNG:** known plaintext leaks RNG state; bijective transition → run RNG backwards.
- **Weak key derivation:** AES key from `SHA256(public_key) XOR seed` recoverable without private key.
- **HMAC-CRC linearity:** CRC linear over GF(2); key recoverable from one message-MAC pair.
- **DES weak keys in OFB:** 4 weak keys make encryption self-inverse; keystream cycles with period 2.
- **Square attack (reduced-round AES):** 4-round AES, integral cryptanalysis: 256-plaintext lambda set, XOR-sum = 0.
- **AES-GCM nonce reuse:** same nonce = CTR keystream reuse + GHASH key recovery. Tool: `nonce-disrespect`.
- **SRP protocol bypass:** send `A = 0` or `A = n` → shared secret 0.
- **Modified AES S-Box brute force:** custom S-Box, only 16 unique outputs; brute-force key bytes.
- **Rabin LSB parity oracle:** `c = m^2 mod n` with LSB oracle → binary search in `log2(n)` queries.
- **Noisy RSA LSB oracle:** sporadic errors — run standard attack, inspect charset, flip oracle results at error positions.
- **PBKDF2 pre-hash bypass:** HMAC pre-hashes keys > 64 bytes. Login with `SHA1(password)`.
- **MD5 multi-collision (fastcol):** chain `fastcol` runs for 2^k files with identical MD5.
- **Custom hash state reversal:** hash leaks intermediate states — invert state update per block, brute-force each block.
- **CRC32 brute-force (small payloads):** ZIP CRC32 headers unencrypted; brute-force files ≤ 6 bytes.
- **Custom MAC forgery via XOR block cancellation:** MAC key stream repeats periodically — three queries where filler blocks cancel.
- **HMAC key recovery (XOR + addition):** flawed `sha256((key XOR msg) + msg)`: `msg=0` gives `sha256(key)`; `msg=2^i` tests bit `i`.
- **AES-CBC ciphertext forging (error-message oracle):** server leaks decrypted bytes in errors; zero blocks reveal intermediate state, XOR to forge.
- **Affine over composite modulus:** `c = A*x+b (mod M)`, M composite. CRT inversion per prime factor.
- **Custom linear MAC forgery:** XOR-based signature linear in secrets. ~5 known pairs recover them.
- **Manger oracle (RSA threshold):** RSA multiplicative + binary search on `m*s < 2^128`. ~128 queries.
- **AES key recovery via zeroing oracle:** integer overflow in key slot indexing allows selective byte zeroing.
- **Sponge hash MITM collision:** sponge rate < state size, uncontrolled state bytes enable MITM.
- **CRC32 collision forgery:** CRC32 is linear — append 4 chosen bytes to force any target CRC32.
- **Blum-Goldwasser bit-extension oracle:** extend ciphertext one bit per query to leak plaintext via parity.
- **Hash length extension:** Merkle-Damgard `hash(SECRET || user_data)` — append data, valid hash without secret.
- **Compression oracle (CRIME-style):** compression before encryption leaks plaintext via ciphertext length.
- **RC4 second-byte bias:** second output byte biased toward `0x00` (1/128 vs 1/256). ~2048 samples distinguish RC4.
- **RSA homomorphic signature forgery:** unpadded RSA: `S(a) * S(b) mod n = S(a*b) mod n`. Sign factors, multiply.

## RSA Attacks

- **Small e with small message:** take eth root.
- **Common modulus:** extended GCD attack.
- **Wiener's attack:** small d.
- **Fermat factorization:** p and q close together.
- **Pollard's p-1:** smooth p-1.
- **Hastad's broadcast:** same message, multiple e=3 encryptions.
- **Consecutive primes:** q = next_prime(p); first prime below sqrt(N).
- **Multi-prime:** factor N with sympy; phi from all factors.
- **Restricted-digit primes:** digit-by-digit factoring from LSB.
- **Coppersmith structured primes:** partially known prime; small_roots via coppersmith lib.
- **Manger oracle (simplified):** phase 1 doubling + phase 2 binary search; ~128 queries.
- **Manger on RSA-OAEP (timing):** Python `or` short-circuit skips PBKDF2 when Y != 0 → fast/slow oracle.
- **Polynomial hash (trivial root):** `g(0) = 0`; craft suffix for `msg = 0 (mod P)`, signature = 0.
- **Polynomial CRT in GF(2)[x]:** ~20 remainders `r = flag mod f`, CRT combine.
- **RSA p=q validation bypass:** set `p=q`; wrong `phi=(p-1)^2`, test decryption fails, leaking ciphertext.
- **RSA cube root CRT (gcd(e,phi)>1):** primes ≡ 1 mod e — eth roots per-prime via `nthroot_mod`.
- **Factoring from phi(n) multiple:** any multiple of `phi(n)` (e.g. `e*d-1`) enables factoring via Miller-Rabin square roots.
- **Weak keygen via base representation:** primes `p = kp*B + tp`, small kp → mixed-radix; brute-force kp*kq.
- **RSA with gcd(e,phi)>1:** `e' = e/g`, `d' = e'^(-1) mod phi`, partial decrypt to `m^g`.
- **RSA partial key recovery (dp/dq/qinv):** partial PEM leak allows O(e) prime recovery.
- **RSA-CRT fault attack:** faulty CRT signature leaks factor via `gcd(s^e - m, n)` (Bellcore).
- **RSA homomorphic decryption bypass:** query oracle with `c * r^e mod n`, divide result by `r`.
- **RSA small prime CRT decomposition:** `n` with many small prime factors — trial division, `m mod p_i` per prime.
- **Hastad broadcast with linear padding:** recipients apply known affine `a_i*m+b_i`; CRT + small_roots.
- **RSA Montgomery reduction timing attack:** leaked extra-subtraction counts reveal private key bits MSB-to-LSB.
- **Bleichenbacher low-exponent signature forgery:** e=3, cube root with correct padding prefix.
- **Franklin-Reiter related message attack (e=3):** two ciphertexts `m+pad1`, `m+pad2`; polynomial GCD.
- **RSA signature bypass (e=1, crafted modulus):** verifier accepts user-supplied `(n, e)`; set `e=1`, `n = sig - PKCS1_pad(msg)`.
- **Coppersmith on linearly-related primes:** `q ~ k*p` — approximate `q ~ sqrt(k*n)`, small_roots on error term.

Basics: `phi=(p-1)*(q-1)`, `d=inverse(e,phi)`, `m=pow(c,d,n)`.

## Elliptic Curve Attacks

- **Small subgroup:** check curve order for small factors; Pohlig-Hellman + CRT.
- **Invalid curve:** send points on weaker curves if validation missing.
- **Singular curves:** discriminant = 0; DLP maps to additive/multiplicative group.
- **Smart's attack:** anomalous curves (order = p); p-adic lift solves DLP in O(1).
- **Baby-step giant-step (BSGS):** general DLP in O(sqrt(n)) time/space. Pohlig-Hellman for smooth-order groups. sympy/fpylll.
- **Fault injection:** compare correct vs faulty output; recover key bit-by-bit.
- **Clock group (x^2+y^2=1):** order = p+1 (not p-1!); Pohlig-Hellman when p+1 smooth.
- **Isogenies:** graph traversal via modular polynomials; pathfinding via LCA.
- **ECDSA nonce reuse:** same `r` in two signatures leaks nonce `k` and private key `d`.
- **Braid group DH:** Alexander polynomial multiplicative under braid concatenation.
- **Ed25519 torsion side channel:** cofactor h=8 leaks scalar bits when derivation uses `key = master * uid mod l`.
- **Tropical semiring residuation:** tropical (min-plus) DH broken — residual `b* = max(Mb[i] - M[i][j])`.
- **FPE Feistel brute-force:** 16-bit round key brute-forceable; remaining affine GF(2) layer.
- **Icosahedral symmetry cipher:** dodecahedron face permutations form order-120 group; lookup table via API probing.
- **Goldwasser-Micali replication oracle:** GM encrypts one bit per ciphertext; replaying one value N times forces all-zero/all-one key. 128 queries recover full AES key.
- **DSA nonce reuse:** same r in two DSA signatures leaks private key.
- **DSA limited k brute force:** nonce `k` small (e.g. 20-bit) — brute-force all `k`.
- **ECC shared prime GCD:** multiple curves sharing a prime factor in modulus; `gcd(n1, n2)` reveals it.
- **DSA key recovery via MD5 collision on k-generation:** nonce `k` from `MD5(prefix+counter)` — `fastcoll` forces nonce reuse.
- **BB-84 QKD MITM:** simulated BB-84 without authenticated classical channels allows full MITM.

## Diffie-Hellman Attacks

- **Trivial g:** try `g = 0, 1, p-1`, peers `A = 0, 1, p-1, p` (unvalidated range checks → known-constant secrets).
- **Pohlig-Hellman:** factor `p-1`; smooth means full DLP via BSGS per subgroup + CRT.
- **Small-subgroup confinement / Lim-Lee:** static key + composite `p-1` with small factors; send order-`r` element, brute `b mod r`.
- **X25519 low-order:** cofactor 8 + clamping: small-order `u` forces all-zero `K`; probe `u = 0, 1`.

## Lattice / LWE Attacks

- **Quick triage:** modular linear equations + hidden quantity small, sparse, biased, or partially leaked → lattice.
- **LLL / BKZ / Babai:** fpylll LLL/BKZ/Babai/CVP — start LLL, BKZ when LLL almost works.
- **HNP from partial nonce leakage:** partial/biased ECDSA/Schnorr nonces reduce to Hidden Number Problem lattices.
- **Truncated LCG state recovery:** high/low-bit leakage from affine recurrences is HNP in disguise.
- **LWE via CVP (Babai):** lattice `[q*I | 0; A^T | I]`, Babai/CVP, project to ternary {-1,0,1}.
- **Ring-LWE / Module-LWE recognition:** polynomial/negacyclic structure — CTFs weaken it with tiny coefficients or leakage.
- **Orthogonal lattices:** hidden subset/subspace problems → recover orthogonal lattice first.
- **LLL for approximate GCD:** fpylll LLL.reduction — short vector reveals hidden factors.
- **Subset sum / knapsack:** binary knapsack and low-density subset-sum are classic lattice territory.
- **Multi-layer challenges:** geometry → subspace recovery → LWE → AES-GCM decryption chain.


## ZKP & Constraint Solving

- **ZKP cheating:** impossible problems (3-coloring K4) — find hash collisions or predict PRNG salts.
- **Graph 3-coloring:** `nx.coloring.greedy_color(G, strategy='saturation_largest_first')`.
- **Z3 solver:** BitVec for bit-level, Int for arbitrary precision.
- **Garbled circuits (free XOR):** XOR three truth table entries to recover global delta.
- **Bigram substitution:** OR-Tools CP-SAT with automaton constraint for known plaintext structure.
- **Trigram decomposition:** positions mod n form independent monoalphabetic ciphers.
- **Shamir SSS (deterministic coefficients):** one share + seeded RNG = univariate equation in secret.
- **Race condition (TOCTOU):** synchronized concurrent requests bypass `counter < N` checks.
- **Groth16 broken setup (delta==gamma):** forge A=alpha, B=beta, C=-vk_x; check verifier constants.
- **Groth16 proof replay:** unconstrained nullifier + no tracking = infinite replays.
- **DV-SNARG forgery:** with verifier oracle access, learn secret v values from unconstrained pairs → forge via CRS cancellation.
- **Shamir SSS reused polynomial coefficients:** same random coefficients for every secret byte — subtracting shares cancels all randomness.

## Introspective CRC via GF(2) Linear Algebra

Self-referential CRC: find ASCII string whose CRC equals itself. CRC is linear over GF(2) — solvable linear system. See advanced-math.md.

## Bleichenbacher RSA Padding Oracle (ROBOT)

RSA PKCS#1 v1.5 padding validation oracle → adaptive chosen-ciphertext recovery. ~10K queries for RSA-2048. See modern-ciphers.md.

## Birthday Attack / Meet-in-the-Middle

n-bit hash collision in ~2^(n/2) attempts. Meet-in-the-middle breaks double encryption in O(2^k) instead of O(2^(2k)).

## C srand/rand Prediction via ctypes

**Pattern:** binary uses `srand(time(NULL))` + `rand()` for keys/XOR masks. Use `ctypes.CDLL('./libc.so.6')` to call C's `srand(int(time()))` and `rand()` directly.

## V8 XorShift128+ (Math.random) State Recovery

**Pattern:** V8 uses xs128p PRNG for `Math.random()`. Given 5-10 consecutive outputs of `Math.floor(CONST * Math.random())`, recover state with Z3 QF_BV solver. Values reversed (LIFO cache). Tool: `d0nutptr/v8_rand_buster`.

## MT State Recovery from Float Outputs

**Pattern:** server exposes `random.random()` floats. Floats yield only ~8 usable bits each (untemper needs 624 × 32-bit ints). Precomputed GF(2) magic matrix (`not_random`) recovers full MT state from 3360+ observations. See prng.md.

## Chaotic PRNG (Logistic Map)

- **Logistic map:** `x = r * x * (1 - x)`, `r ≈ 3.99-4.0`; brute-force high-precision decimal seeds.
- **Keystream:** `struct.pack("<f", x)` per iteration; XOR ciphertext.

## SPN S-box Intersection Attack

Divide-and-conquer SPN key recovery: attack each S-box position independently, intersect valid key candidates. See modern-ciphers-3.md.

## Useful Tools

- **quipqiup.com:** automated substitution cipher solver.
