# Gen-2 Extreme Tuning: Bypassing BIOS Limitations

For AMD Ryzen AI 9 370 (Strix Point)

When the OEM BIOS locks out Precision Boost Overdrive (PBO) or VRAM allocation, we must use third-party "Out-of-BIOS" tools to unlock the 16GB VRAM / 24-thread potential required for high-throughput computational workflows.

## 1. The Smokeless UMAF Bypass (BIOS Level)

For laptops with locked BIOS menus, Smokeless UMAF (Universal Menu Access Form) is the method to hard-allocate 16GB of VRAM.

*   **Instruction:** Create a FAT32 USB drive with the UMAF EFI files.
*   **VRAM Path:** Navigate to `AMD CBS -> NBIO Common Options -> GFX Configuration`.
*   **Setting:** Change `Integrated Graphics Controller` to `Forces` and `UMA Mode` to `UMA_SPECIFIED`, then set `UMA Frame Buffer Size` to `16G`.

## 2. OS-Level Power Tuning (Gentoo Native - RyzenAdj)

Override the 33W or 45W "Balanced" limits forced by laptop firmware to sustain 24-thread compilation and RCOD processing.

*   **Package:** `sys-power/ryzenadj` (from the guru overlay).
*   **Target Profile:** 54W Sustained (STAPM).
*   **Command:**
    ```bash
    ryzenadj --stapm-limit=54000 --fast-limit=65000 --slow-limit=54000 --tctl-temp=95
    ```
    *Note: Tuning the APU Skin Temperature Limit (STAPM) is essential for high-throughput computational workflows to prevent the GPU from throttling during load spikes.*

## 3. Undervolting for Thermal Headroom

Use the Curve Optimizer via UMAF or `ruv-gui` on Linux to apply a Global Negative Offset (e.g., -15 or -20). This reduces heat and allows higher sustained boost clocks on the Zen 5 performance cores.

## 4. Advanced P-State Scaling (amd-pstate-epp)

Modern Linux kernels (6.11+) use the `amd-pstate` driver.
*   Add `amd_pstate=active` to the GRUB command line.
*   Use `power-profiles-daemon` to switch between `performance` and `powersave` based on load.