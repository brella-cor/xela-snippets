def sample_normal(n, *, loc=0.0, scale=1.0, rng=None):
    return _rng(rng).normal(loc, scale, size=_n(n))

def sample_exponential(n, *, scale=1.0, rng=None):
    return _rng(rng).exponential(scale, size=_n(n))

def sample_uniform(n, *, low=0.0, high=1.0, rng=None):
    return _rng(rng).uniform(low, high, size=_n(n))

def sample_student_t(n, *, df=5.0, loc=0.0, scale=1.0, rng=None):
    return loc + scale * _rng(rng).standard_t(df, size=_n(n))

def sample_gamma(n, *, shape=1.0, scale=1.0, rng=None):
    return _rng(rng).gamma(shape, scale, size=_n(n))

def sample_beta(n, *, a=1.0, b=1.0, rng=None):
    return _rng(rng).beta(a, b, size=_n(n))

def sample_lognormal(n, *, mean=0.0, sigma=1.0, rng=None):
    return _rng(rng).lognormal(mean, sigma, size=_n(n))

def sample_laplace(n, *, loc=0.0, scale=1.0, rng=None):
    return _rng(rng).laplace(loc, scale, size=_n(n))