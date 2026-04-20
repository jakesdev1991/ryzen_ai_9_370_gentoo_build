# Installation & Configuration Guide

This document covers the core Gentoo installation on the Ryzen AI 9 HX 370.

## 1. The Memory Split & VRAM Bypass

The Gen-2 build requires 16GB of VRAM dedicated to the Radeon 890M. If your BIOS is locked:

*   **Preferred Method:** Use [Smokeless UMAF](TUNING_GUIDE.md) to set UMA Frame Buffer Size to `16G`.
*   **The amd-ttm Bypass (Fallback):** If UMAF is unavailable, create `/etc/modprobe.d/amdgpu.conf` and add:
    ```
    options amdgpu gttsize=16384
    ```
    This allows the kernel to dynamically "borrow" up to 16GB of system RAM.

## 2. The ZRam Strategy

With only 16GB of system RAM left for 24 threads, you must configure ZRam to prevent Out of Memory (OOM) crashes during the build.

1.  Enable ZRam: `modprobe zram`
2.  Set Size to 10GB: `zramctl --find --size 10G`
3.  Set Priority to 100: `swapon /dev/zram0 -p 100`

Ensure your 64GB SSD Swap file is set to Priority -2 in `/etc/fstab`.

## 3. The Plasma Pull

With your `/etc/portage/make.conf` configured (see `configs/make.conf`), execute the primary desktop build:

```bash
emerge --ask kde-plasma/plasma-meta
```

*(Note: This is approximately 220 packages. Watch the ZRam compression via `htop`.)*

## 4. Phase 4 Verification & Driver Lockdown

Once the 220 packages finish, do not reboot immediately.

### Finalizing the SDDM Display Manager
*   **systemd:** `systemctl enable sddm`
*   **OpenRC:** `rc-update add sddm default`

### Validating the 16GB VRAM Split
Verify the Radeon 890M has the correct address space:
```bash
dmesg | grep -i "VRAM"
```
*(If you don't see ~16384M, the BIOS allocation was overridden.)*

### NPU Check
Ensure the XDNA 2 driver is active:
```bash
lsmod | grep amdxdna
```
If empty, run: `modprobe amdxdna && echo "NPU Online"`.

### The "Human Error" Safety Guard
Verify core files exist before rebooting:
```bash
ls /usr/include/stdio.h || (echo "CRITICAL: Headers missing! Re-emerge glibc now!" && exit 1)
ls /boot/vmlinuz* || (echo "CRITICAL: Kernel image missing! Rebuild kernel now!" && exit 1)
```

## 5. The "Victory Lap" Workflow (Post-Build Finishing)

Merge configurations and clear scaffolding:
1.  `etc-update` (Review changes carefully to avoid overwriting `make.conf`).
2.  `emerge --ask --oneshot sys-devel/libtool`
3.  `env-update && source /etc/profile`
4.  `emerge --depclean`

## 6. Gentoo Plasma Post-Install - Application Suite & Services

### Write Permissions (Universal)
If your drive mounts as read-only:
`mount -o remount,rw /`

### Networking & Display Services
**Option A: systemd**
```bash
systemctl enable NetworkManager --now
systemctl enable sddm --now
```
**Option B: OpenRC**
```bash
rc-update add NetworkManager default
rc-update add sddm default
rc-service NetworkManager start
rc-service sddm start
```

### Core Application Install
`emerge --ask --verbose kde-apps/konsole kde-apps/dolphin kde-apps/kate kde-apps/ark kde-apps/okular www-client/firefox`

### User Permissions
```bash
gpasswd -a your_user wheel
gpasswd -a your_user video
gpasswd -a your_user audio
gpasswd -a your_user network
gpasswd -a your_user plugdev
```

### Hardware Note for Compiling Firefox
Compiling `www-client/firefox` with 24 threads generates extreme heat. Ensure adequate cooling.