# Omega Protocol Gen-2: Strix Point Build Guide

Welcome to the official build repository for the Gen-2 Omega Protocol. This guide documents the exact environment, hardware-to-software isolation, and Gentoo Linux compilation path required to build this highly specialized system.

This build leverages the AMD Ryzen™ AI 9 HX 370 (Strix Point), optimizing for high-throughput computational simulations, parallel processing, and extreme memory management using the XDNA 2 NPU.

## 💻 1. Hardware Profile & Resource Allocation

This system operates as a portable supercomputing node. Resource allocation is aggressive and specifically tuned for hybrid-core compiling and in-memory NPU workflows.

*   **CPU:** AMD Ryzen AI 9 HX 370 (Zen 5 / Zen 5c) — 12 Cores / 24 Threads.
*   **GPU/NPU:** Radeon 890M (RDNA 3.5) + XDNA 2 (50 TOPS capability).
*   **Physical RAM (32GB Total):**
    *   **16GB allocated to VRAM/NPU:** Locked for hardware acceleration and zero-latency tensor processing.
    *   **16GB allocated to System RAM:** Dedicated to OS overhead and the Gentoo compilation thread pool.
*   **Swap / Virtual Memory Hierarchy:**
    *   **Tier 1:** 10GB ZRam (Priority 100) – Handles rapid, high-speed memory compression to prevent compilation crashing.
    *   **Tier 2:** 64GB SSD Swap File (Priority -2) – Deep fallback storage.

## ⚙️ 2. Hardware Tuning & Overclocking Profile

To sustain the extreme thermal loads required by 24-thread compilation and high-throughput computational workflows, we apply specific "Out-of-BIOS" power limits.

See the full [TUNING_GUIDE.md](TUNING_GUIDE.md) for how to bypass OEM restrictions, including:
*   **Smokeless UMAF:** Hard-allocating the 16GB VRAM.
*   **OS-Level Power Tuning (RyzenAdj):** Setting a sustained 54W STAPM limit to prevent the GPU/NPU split from starving the CPU voltage during load spikes.
*   **Core Affinity:** Locking intense calculations to the high-performance Zen 5 cores (CPU 0-7) to avoid the slower Zen 5c efficiency cores.

## 🧠 3. Deployment Status

*   **Target Environment:** KDE Plasma 6 (Wayland) on Gentoo Linux.
*   **Validated Architecture:** Zen 5 / Zen 5c hybrid.

---
*Optimized for Perspective Manifold v29.0. Validated on Zen 5 Architecture.*