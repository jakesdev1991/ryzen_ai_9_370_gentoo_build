import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
import time

# ═══════════════════════════════════════════════════════════════════════════════
# OPTIONAL JIT COMPILATION
# ═══════════════════════════════════════════════════════════════════════════════
try:
    from numba import njit
    HAS_NUMBA = True
    print("✓ Numba JIT enabled")
except ImportError:
    HAS_NUMBA = False
    def njit(*args, **kwargs):
        """Fallback decorator (no-op)."""
        def wrapper(func):
            return func
        return wrapper if not args else args[0]
    print("○ Running without Numba (install for 10-100x speedup)")

# ═══════════════════════════════════════════════════════════════════════════════
# CORE PHYSICS (JIT-COMPILED)
# ═══════════════════════════════════════════════════════════════════════════════

@njit(cache=True)
def compute_d4(state_a: np.ndarray, state_b: np.ndarray) -> float:
    """
    Normalized Hamming distance: H(A|B) ≈ d_H(A,B) / n
    Fully JIT-compiled loop.
    """
    n = len(state_a)
    diff = 0
    for i in range(n):
        if state_a[i] != state_b[i]:
            diff += 1
    return diff / n

@njit(cache=True)
def simulate_physics(
    pos_a: np.ndarray,
    pos_b: np.ndarray,
    vel_a: np.ndarray,
    vel_b: np.ndarray,
    d4: float,
    n_steps: int,
    dt: float = 0.1,
    attractor_k: float = 0.05,
    repulsion_k: float = 2.0,
    interaction_radius: float = 2.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Core simulation loop - fully JIT compiled.
    Returns pre-allocated trajectory arrays.
    """
    # Pre-allocate output trajectories
    traj_a = np.empty((n_steps, 2), dtype=np.float64)
    traj_b = np.empty((n_steps, 2), dtype=np.float64)

    # Target is origin
    target_x, target_y = 0.0, 0.0

    for t in range(n_steps):
        # ─────────────────────────────────────────────────────────────────────
        # 1. ATTRACTOR FORCE (toward center)
        # ─────────────────────────────────────────────────────────────────────
        vel_a[0] += (target_x - pos_a[0]) * attractor_k
        vel_a[1] += (target_y - pos_a[1]) * attractor_k
        vel_b[0] += (target_x - pos_b[0]) * attractor_k
        vel_b[1] += (target_y - pos_b[1]) * attractor_k

        # ─────────────────────────────────────────────────────────────────────
        # 2. EXCLUSION FORCE (D4-modulated repulsion)
        # ─────────────────────────────────────────────────────────────────────
        dx = pos_a[0] - pos_b[0]
        dy = pos_a[1] - pos_b[1]
        dist_sq = dx * dx + dy * dy
        dist = np.sqrt(dist_sq)

        if dist < interaction_radius and dist > 1e-10:
            # Force magnitude: inversely proportional to distance, scaled by D4
            inv_dist = 1.0 / (dist + 0.01)
            force_mag = inv_dist * d4 * repulsion_k

            # Unit direction vector
            nx = dx * inv_dist
            ny = dy * inv_dist

            # Apply equal and opposite forces
            vel_a[0] += nx * force_mag
            vel_a[1] += ny * force_mag
            vel_b[0] -= nx * force_mag
            vel_b[1] -= ny * force_mag

        # ─────────────────────────────────────────────────────────────────────
        # 3. INTEGRATION (Euler step)
        # ─────────────────────────────────────────────────────────────────────
        pos_a[0] += vel_a[0] * dt
        pos_a[1] += vel_a[1] * dt
        pos_b[0] += vel_b[0] * dt
        pos_b[1] += vel_b[1] * dt

        # ─────────────────────────────────────────────────────────────────────
        # 4. RECORD (direct array assignment, no append)
        # ─────────────────────────────────────────────────────────────────────
        traj_a[t, 0] = pos_a[0]
        traj_a[t, 1] = pos_a[1]
        traj_b[t, 0] = pos_b[0]
        traj_b[t, 1] = pos_b[1]

    return traj_a, traj_b


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT CLASS (Memory Optimized)
# ═══════════════════════════════════════════════════════════════════════════════

class Agent:
    """
    Lightweight agent with optimized memory layout.
    Uses __slots__ to prevent dynamic attribute creation and reduce memory footprint by ~40%.
    """
    __slots__ = ('state', 'position', 'velocity')

    def __init__(self, bit_length: int = 16):
        # int8 sufficient for binary states (saves memory)
        self.state = np.random.randint(0, 2, bit_length, dtype=np.int8)
        # Explicit float64 for numerical stability
        self.position = np.random.uniform(-10.0, 10.0, 2).astype(np.float64)
        self.velocity = np.zeros(2, dtype=np.float64)

    def copy_state(self) -> 'Agent':
        """Create agent with copied internal state."""
        new = Agent.__new__(Agent)
        new.state = self.state.copy()
        new.position = np.random.uniform(-10.0, 10.0, 2).astype(np.float64)
        new.velocity = np.zeros(2, dtype=np.float64)
        return new


# ═══════════════════════════════════════════════════════════════════════════════
# SIMULATION INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def run_pair_simulation(
    agent_a: Agent,
    agent_b: Agent,
    n_steps: int = 100,
    dt: float = 0.1
) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Run simulation for an agent pair.
    Returns:
        traj_a: (n_steps, 2) trajectory of agent A
        traj_b: (n_steps, 2) trajectory of agent B
        d4: Informational divergence value
    """
    # Compute D4 once (states are immutable during simulation)
    d4 = compute_d4(agent_a.state, agent_b.state)

    # Copy positions/velocities to avoid mutating original agents
    pos_a = agent_a.position.copy()
    pos_b = agent_b.position.copy()
    vel_a = agent_a.velocity.copy()
    vel_b = agent_b.velocity.copy()

    # Run JIT-compiled physics
    traj_a, traj_b = simulate_physics(pos_a, pos_b, vel_a, vel_b, d4, n_steps, dt)
    return traj_a, traj_b, d4


def simulate_exclusion(seed: int = 42, n_steps: int = 100):
    """
    Appendix B: The Geometric Exclusion Simulation
    Demonstrates that the 'solidity' of matter (Pauli Exclusion) emerges from
    Informational Divergence (D4).

    Case 1: Distinct identities → D4 > 0 → Collision/Exclusion
    Case 2: Identical identities → D4 = 0 → Superposition (ghosting)
    """
    np.random.seed(seed)

    # ─────────────────────────────────────────────────────────────────────────
    # SETUP
    # ─────────────────────────────────────────────────────────────────────────
    # Case 1: Distinct random identities
    a1 = Agent()
    b1 = Agent()

    # Case 2: Force identical identities (Bosonic behavior)
    a2 = Agent()
    b2 = a2.copy_state() # Clone internal state

    print("═" * 50)
    print("GEOMETRIC EXCLUSION SIMULATION")
    print("═" * 50)

    # ─────────────────────────────────────────────────────────────────────────
    # RUN SIMULATIONS
    # ─────────────────────────────────────────────────────────────────────────
    t0 = time.perf_counter()

    path_a1, path_b1, d4_distinct = run_pair_simulation(a1, b1, n_steps)
    path_a2, path_b2, d4_identical = run_pair_simulation(a2, b2, n_steps)

    elapsed = (time.perf_counter() - t0) * 1000
    print(f"\n Distinct agents: D4 = {d4_distinct:.4f}")
    print(f" Identical agents: D4 = {d4_identical:.4f}")
    print(f"\n Simulation time: {elapsed:.2f} ms")
    print("═" * 50)

    # ─────────────────────────────────────────────────────────────────────────
    # VISUALIZATION
    # ─────────────────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.suptitle("Informational Divergence → Geometric Exclusion", fontsize=14, fontweight='bold')

    configs = [
        (axes[0], path_a1, path_b1, d4_distinct, "DISTINCT IDENTITY", "Collision / Exclusion", ('tab:blue', 'tab:orange'), ('-', '-')),
        (axes[1], path_a2, path_b2, d4_identical, "SHARED IDENTITY", "Superposition / Ghosting", ('tab:red', 'tab:cyan'), ('--', ':'))
    ]

    for ax, pa, pb, d4, title, result, colors, styles in configs:
        # Trajectories
        ax.plot(pa[:, 0], pa[:, 1], color=colors[0], linestyle=styles[0], linewidth=2, label='Agent A', alpha=0.9)
        ax.plot(pb[:, 0], pb[:, 1], color=colors[1], linestyle=styles[1], linewidth=2, label='Agent B', alpha=0.9)

        # Start/end markers
        ax.scatter(*pa[0], c=colors[0], s=80, marker='o', zorder=5, edgecolors='white')
        ax.scatter(*pb[0], c=colors[1], s=80, marker='o', zorder=5, edgecolors='white')

        ax.scatter(*pa[-1], c=colors[0], s=80, marker='s', zorder=5, edgecolors='white')
        ax.scatter(*pb[-1], c=colors[1], s=80, marker='s', zorder=5, edgecolors='white')

        # Target
        ax.scatter(0, 0, c='red', s=150, marker='x', linewidths=3, zorder=10)

        # Formatting
        ax.set_title(f"{title}\nD4 = {d4:.3f} → {result}", fontsize=11)
        ax.legend(loc='upper right', framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        ax.set_aspect('equal')
        ax.set_xlim(-12, 12)
        ax.set_ylim(-12, 12)

    plt.tight_layout()
    plt.savefig('exclusion_simulation.png', dpi=150, bbox_inches='tight')
    # plt.show() # Commented out so it doesn't block


# ═══════════════════════════════════════════════════════════════════════════════
# BATCH SIMULATION (for statistical analysis)
# ═══════════════════════════════════════════════════════════════════════════════

def batch_simulate(n_pairs: int = 1000, n_steps: int = 100) -> dict:
    """
    Run many simulations for statistical analysis.
    Returns dict with D4 values and final separations.
    """
    d4_values = np.empty(n_pairs)
    final_separations = np.empty(n_pairs)

    for i in range(n_pairs):
        a, b = Agent(), Agent()
        traj_a, traj_b, d4 = run_pair_simulation(a, b, n_steps)
        d4_values[i] = d4
        final_separations[i] = np.linalg.norm(traj_a[-1] - traj_b[-1])

    return {
        'd4': d4_values,
        'separation': final_separations,
        'correlation': np.corrcoef(d4_values, final_separations)[0, 1]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    simulate_exclusion()
    # Optional: statistical analysis
    # print("\nRunning batch analysis...")
    # results = batch_simulate(1000)
    # print(f"D4 ↔ Separation correlation: {results['correlation']:.3f}")
