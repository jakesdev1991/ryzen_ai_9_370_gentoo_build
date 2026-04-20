# Troubleshooting the Gen-2 Build

Hardware: AMD Ryzen AI 9 370 | Radeon 890M | XDNA 2 NPU
OS: Gentoo Linux (Plasma 6)

This document outlines the glitches, "heirs," and human errors encountered while pushing the hardware to its absolute limit (24-thread compilation on limited system RAM).

## 1. Resource & Memory Glitches (The "Step 110" Hump)

### A. The "Out of Memory" (OOM) Death Spiral
*   **Symptom:** Compilation freezes at ~50% (Step 110-140), mouse stutters, or `emerge` is killed with "Signal 9."
*   **The Cause:** Running 24 threads on 16GB of system RAM. Heavy linkers (like `qtwebengine`) require ~2GB per thread.
*   **The Fix:**
    *   Ensure your 10GB ZRam is Priority 100 via `zramctl`.
    *   **The "Wait it Out" Rule:** If it drops to the 64GB SSD swap, speed will tank by 90%. Do not hard reset. Let compression clear the buffer.
    *   **Emergency Throttle:** `MAKEOPTS="-j8" emerge --resume`

### B. Thermal Throttling / Worker Failure
*   **Symptom:** `gcc` throws an Internal Compiler Error (ICE) unrelated to code.
*   **The Cause:** Zen 5 cores hitting TjMax.
*   **The Fix:** Install `sys-power/thermald`. Use `cpupower frequency-set -g powersave` to lower the clock ceiling. Use RyzenAdj to set a 54W STAPM limit (see TUNING_GUIDE.md).

## 2. Hardware-Specific Glitches (Strix Point)

### A. Radeon 890M "Black Screen" on Boot
*   **Symptom:** Plasma finishes (220/220), but `startplasma-wayland` or SDDM fails.
*   **The Cause:** Missing `amdgpu` firmware for the Strix Point architecture.
*   **The Fix:** Emerge `sys-kernel/linux-firmware` and ensure `CONFIG_EXTRA_FIRMWARE="amdgpu/strix_*.bin"` is in your kernel.

### B. XDNA 2 NPU Not Initializing
*   **Symptom:** `dmesg | grep xdna` returns nothing.
*   **The Cause:** Blocked by BIOS-level VRAM or missing `amdxdna` driver.
*   **The Fix:** Check IOMMU windows and enable `CONFIG_IOMMU_SVA` in the kernel.

### C. The "Windows Hijack" Boot Loop
*   **The Glitch:** Restarting to access BIOS results in Windows loading instantly.
*   **The Fix:** Windows "Fast Startup" locks the kernel. Open Admin PowerShell: `shutdown /r /f /t 0` to cold reboot and catch the F2/F12 prompt.

## 3. Human Error Recovery & High-Risk Glitches

### A. Accidental File Deletion (The Panic Phase)
*   **The Mistake:** Running a cleanup script or `rm -rf` while `emerge` is running, deleting `/usr/include` or `/var/db/pkg`.
*   **The Consequence:** Build crashes instantly with missing glibc or headers.
*   **The Recovery:**
    *   *Quick Fix (if Portage lives):* `emerge --oneshot sys-libs/glibc sys-kernel/linux-headers`
    *   *Hard Fix:* Boot Gentoo LiveUSB, mount partitions, chroot, and restore from LiveUSB binaries.

### B. Skipping the Post-Build Sync
*   **The Mistake:** Hitting 220/220 and rebooting immediately.
*   **The Consequence:** Broken symlinks and GUI failures.
*   **The Recovery:** Always run `etc-update` and `env-update && source /etc/profile`.

### C. Smokeless UMAF: The Brick Warning
*   **Warning:** Changing RAM timings in UMAF can brick the device.
*   **VRAM Conflicts:** If setting 16GB causes a black screen, boot back into UMAF and lower to 8GB, or rely on the `amd-ttm` dynamic limit instead.

## 4. The "Hall of Fame": Lessons from the Trenches

A collection of battle-tested fixes for common "brute force" engineering hurdles encountered during the Strix Point deployment.

### A. The "Nesting Doll" Home Folder (NTFS Permissions)
*   **The Mistake:** Mounting an entire NTFS Windows partition directly as `/home`.
*   **The Result:** Plasma/Linux failures due to the inability to set POSIX "Owner" permissions on NTFS.
*   **The Fix:** Use a native Linux `/home` partition and create **Symbolic Links** to the Windows data directories. This maintains data access without NTFS permission restrictions.

### B. The "Read-Only" Deadlock
*   **The Mistake:** Attempting to modify files or directories while the kernel is in a "Safe Mode" read-only state.
*   **The Result:** "Permission Denied" errors even for the root user.
*   **The Fix:** Force a writeable state with: `mount -o remount,rw /`.

### C. The "Ghost Driver" Hunt (NTFS-3G)
*   **The Mistake:** Relying on `ntfs3` or standard `ntfs` kernel drivers before they are fully configured/compiled.
*   **The Result:** "Unknown filesystem type" errors during mount attempts.
*   **The Fix:** Use a network connection to `emerge sys-fs/ntfs3g` and use the userspace translator to bridge the gap.

### D. The Typo Gauntlet
*   **The Mistake:** Syntax errors in device paths (e.g., `nvme0nip3` vs `nvme0n1p3`) or extra spaces in mount strings.
*   **The Result:** "Device not found" or "Bad usage" errors that mimic hardware failure.
*   **The Fix:** Double-check TTY output. Taking a photo of the screen can help spot subtle character errors that are easy to miss when frustrated.

### E. The "Dirty" Windows Shutdown
*   **The Mistake:** Leaving Windows in "Fast Startup" (hibernated) mode.
*   **The Result:** The NTFS partition remains "locked," and Linux refuses to mount it for writing to prevent data corruption.
*   **The Fix:** Use the `force` and `remove_hiberfile` flags in the mount command, or properly shut down Windows using `shutdown /r /f /t 0`.