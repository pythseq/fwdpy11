import unittest
from fwdpy11 import GSLrng
from fwdpy11.wright_fisher_qtrait import evolve, GaussianNoise
from quick_pops import quick_mlocus_qtrait_pop_params


class GaussianNoiseUpdater(GaussianNoise):
    def __init__(self, rng, sd, mean=0.0):
        self.ncalls = 0
        super(GaussianNoiseUpdater, self).__init__(rng, sd, mean)

    def update(self, generation):
        self.ncalls += 1


class testNoiseUpdater(unittest.TestCase):
    def test_noise_updater(self):
        rng = GSLrng(42)
        pop, params = quick_mlocus_qtrait_pop_params()
        n = GaussianNoiseUpdater(rng, 0.1)
        params.noise = n
        evolve(rng, pop, params)
        self.assertEqual(n.ncalls, pop.generation)


if __name__ == "__main__":
    unittest.main()
