---
name: virtualbox-guest-access
description: >-
  Operate a VirtualBox Linux guest VM from its host over SSH or VBoxManage
  guestcontrol. Use for guest VM access, "cannot SSH into the VM", host-only
  networking, guestcontrol command patterns, a VPN killswitch blocking the
  host subnet, Guest Additions health, and installing tooling inside a guest.
  Applies to any CLI agent, not one specific harness.
license: MIT
metadata:
  author: Local setup
  version: "1.1.0"
  platform: VirtualBox host and Linux guest
---

# VirtualBox Linux Guest Access

Two independent channels reach a guest. Pick deliberately: SSH is fast but
depends on guest networking; `guestcontrol` is slow but survives a broken
network.

## When to use

Use when running commands, installing tooling, or diagnosing access to a
VirtualBox Linux guest from its host. Use `systematic-debugging` for an
unexplained in-guest application failure and `homelab-pihole-dns` for DNS
resolver questions. This skill is not a VM provisioner, does not create VMs,
and contains no credentials.

## Channel selection

| Situation | Channel |
|---|---|
| Normal work, many commands, file transfer | SSH (`ssh`, `scp`) |
| SSH not yet configured, or guest networking broken | `VBoxManage guestcontrol` |
| Both unresponsive | `VBoxManage controlvm <vm> screenshotpng` to see the console |
| Checking whether the guest is even alive | `VBoxManage showvminfo <vm> --machinereadable` (hypervisor-level, never blocked by guest state) |

Resolve `VBoxManage` on the host; it is frequently absent from `PATH`:

```powershell
$exe = if (Get-Command VBoxManage -ErrorAction SilentlyContinue) {
  "VBoxManage"
} else {
  "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
}
```

## guestcontrol command patterns

Inline multi-line bash passed through PowerShell then VBoxManage then guest
bash breaks unpredictably. Write a script, copy it, run it:

```powershell
& $exe guestcontrol "<vm-name>" copyto --username <user> --password <password> `
  "C:\path\local\task.sh" "/home/<user>/task.sh"
& $exe guestcontrol "<vm-name>" run --username <user> --password <password> `
  -- /bin/bash /home/<user>/task.sh
```

| Rule | Reason |
|---|---|
| Never pass `--exe` | Combined with a program name after `--` it produces "cannot execute binary file" |
| Put the program directly after `--` | `-- /bin/bash script.sh`, or `-- /usr/bin/id` for a bare command |
| Allow 20-40s per call minimum | Fixed session-setup overhead, before the command itself runs |
| Batch one phase per script | Each call pays the overhead again |
| Pipe the sudo password inside the script | `echo '<password>' \| sudo -S -k <cmd>`; sudo does not stay cached across calls |

`GuestAdditionsRunLevel` is the health signal: `0` means the guest service is
down or mid-boot, `2` means ready. A `0` climbing to `2` indicates the guest is
booting, not hung.

## SSH bootstrap and its failure modes

Install the server in-guest, add a public key, then verify from the host.
Diagnose in this order when key auth fails:

| Symptom | Cause |
|---|---|
| Connection timed out or refused, no log entry in guest | Firewall or VPN killswitch dropping the host subnet |
| Server log shows "Accepted key" then client closes immediately | Client cannot sign: the private key has a passphrase and `BatchMode=yes` blocks the prompt |
| Generic "Permission denied (publickey)" with a preauth reset | An `AuthorizedKeysCommand` drop-in in `sshd_config.d/` failing before the plain `authorized_keys` file is consulted |
| Key correct, permissions correct, still denied | Check `sshd -T` effective config, not just `sshd_config`; drop-ins override it |

Generate a genuinely passphrase-less key from Windows. PowerShell mangles
`-N '""'` into a real passphrase, which then fails silently under
`BatchMode=yes`:

```powershell
cmd /c 'ssh-keygen -t ed25519 -f "C:\Users\<user>\.ssh\id_ed25519_<guest>" -N "" -C "<host>-to-<guest>"'
ssh-keygen -y -f "C:\Users\<user>\.ssh\id_ed25519_<guest>" -P ""
```

The second command must print the public key. If it reports an incorrect
passphrase, the key is unusable for non-interactive auth; regenerate it.

## Guest environment traps

| Trap | Handling |
|---|---|
| Login shell may be `zsh`, not `bash` | Confirm with `getent passwd <user>`. `PATH` and env exports written to `~/.bashrc` are silently ignored by zsh; write to `~/.zshrc` |
| `zsh -l -c` does not source `~/.zshrc` | Verify interactive config with `zsh -i -c`; login shells read `~/.zprofile` / `~/.zshenv` |
| A VPN client killswitch can default-drop the host-only subnet | Fix through the VPN's own allowlist, not by editing `nft`/`iptables` rules it will regenerate |
| Unattended upgrades may reboot the guest mid-task | An orderly `systemd-shutdown` entry in the previous boot's log confirms a reboot rather than a crash; files on disk survive |
| Long installs die when the host SSH client times out | Detach in-guest: `nohup <cmd> > /tmp/<name>.log 2>&1 &`, then poll the log |
| A CLI that reads stdin hangs over SSH with no PTY | Use `ssh -n`, or redirect in-guest with `< /dev/null` |

Check accumulating CPU time to distinguish a slow process from a deadlocked
one. A genuinely stuck process accumulates none:

```powershell
ssh -n <alias> 'ps -p <pid> -o pid,etime,time,pcpu,stat,cmd'
```

## Networking

A host-only adapter gives direct host-to-guest addressing; NAT alone does not
without port forwarding. Both host and guest need an address on the host-only
subnet. Confirm the host side exists before blaming the guest:

```powershell
Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.InterfaceAlias -like "*Host-Only*" } |
  Select-Object InterfaceAlias, IPAddress
```

Record a host `~/.ssh/config` entry once working so later sessions skip
rediscovery.

## Report

State which channel was used, the commands run, and evidence from actual
output. A completed install is not a working install until the installed
binary has been executed successfully in the guest. Note any reboot observed,
and whether an allowlist or config change was made that the user should keep.

## Prerequisites and provenance

Requires VirtualBox with Guest Additions running in the guest and host
administrator access sufficient to run `VBoxManage`. Guest credentials and SSH
keys are supplied per session and are deliberately absent from this skill.
Load companions through `skill-router`.
