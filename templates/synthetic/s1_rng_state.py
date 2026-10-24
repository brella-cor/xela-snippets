import numpy as np
from scipy import stats
from scipy.special import expit, softmax

RNG = np.random.default_rng() # No fixed seed imposed by the toolkit.

def _rng(rng=None):
    return RNG if rng is None else rng

def _n(n):
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)):
        raise TypeError("n must be an integer")
    if n < 1:
        raise ValueError("n must be positive")
    return int(n)

# In an EXPERIMENT cell: choose SEED, then assign RNG = default_rng(SEED).
# Suggested exploratory seed: 42; the model exercise supplies its seed.
# Pass rng=another_generator when isolating a separate random stream.