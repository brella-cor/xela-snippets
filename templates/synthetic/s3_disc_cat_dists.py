def sample_bernoulli(n, *, p=0.5, rng=None):
    return _rng(rng).binomial(1, p, size=_n(n))

def sample_binomial(n, *, trials=1, p=0.5, rng=None):
    return _rng(rng).binomial(trials, p, size=_n(n))

def sample_poisson(n, *, rate=1.0, rng=None):
    return _rng(rng).poisson(rate, size=_n(n))

def sample_negative_binomial(n, *, mean=1.0, dispersion=1.0, rng=None):
    p = dispersion / (dispersion + mean)
    return _rng(rng).negative_binomial(dispersion, p, size=_n(n))

def sample_geometric(n, *, p=0.5, rng=None):
    return _rng(rng).geometric(p, size=_n(n))

def sample_categorical(n, *, probabilities, rng=None):
    return _rng(rng).choice(len(probabilities), size=_n(n), p=probabilities)

def sample_multinomial(n, *, trials, probabilities, rng=None):
    return _rng(rng).multinomial(trials, probabilities, size=_n(n))