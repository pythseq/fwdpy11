#
# Copyright (C) 2017 Kevin Thornton <krthornt@uci.edu>
#
# This file is part of fwdpy11.
#
# fwdpy11 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# fwdpy11 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with fwdpy11.  If not, see <http://www.gnu.org/licenses/>.
#
import unittest
import fwdpy11 as fp11


class testSlocusPop(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.pop = fp11.SlocusPop(1000)

    def test_N(self):
        self.assertEqual(self.pop.N, 1000)

    def test_generation(self):
        self.assertEqual(self.pop.generation, 0)

    def test_fitnesses(self):
        # All fitnesses should be 1
        self.assertEqual(
            sum([i.w for i in self.pop.diploid_metadata]),
            float(self.pop.N))

    def test_labels(self):
        # All diploids should be labeled 0 to pop.N-1
        self.assertEqual(
            [i.label for i in self.pop.diploid_metadata],
            [i for i in range(self.pop.N)])

    def test_genetic_values(self):
        self.assertEqual(sum([i.g for i in self.pop.diploid_metadata]), 0.0)

    def test_e_values(self):
        self.assertEqual(sum([i.e for i in self.pop.diploid_metadata]), 0.0)


class testSlocusPopExceptions(unittest.TestCase):
    def testNzero(self):
        with self.assertRaises(ValueError):
            fp11.SlocusPop(0)


class testSampling(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        from quick_pops import quick_nonneutral_slocus
        self.pop = quick_nonneutral_slocus()
        self.rng = fp11.GSLrng(42)

    def testRandomSample(self):
        import fwdpy11.sampling
        s = self.pop.sample(rng=self.rng, nsam=10)
        x = fwdpy11.sampling.matrix_to_sample(s)
        self.assertTrue(type(x) is list)

    def testDefinedSample(self):
        self.pop.sample(individuals=range(10))

        with self.assertRaises(IndexError):
            """
            Internally, we should catch cases where i >= N
            """
            self.pop.sample(individuals=range(self.pop.N, self.pop.N + 10))

        with self.assertRaises(Exception):
            """
            pybind11 disallows conversion of negative
            numbers to a list of unsigned types.
            """
            self.pop.sample(individuals=range(-10, 10))


class testPythonObjects(unittest.TestCase):
    @classmethod
    def setUp(self):
        from quick_pops import quick_slocus_qtrait_pop_params
        self.pop, self.pdict = quick_slocus_qtrait_pop_params()
        self.rng = fp11.GSLrng(101)

    def testParentalData(self):
        from fwdpy11.model_params import ModelParams
        from fwdpy11.wright_fisher import evolve
        params = ModelParams(**self.pdict)
        evolve(self.rng, self.pop, params)
        parents = [i.parents for i in self.pop.diploid_metadata]
        for i in parents:
            self.assertTrue(i is not None)
            self.assertTrue(len(i) == 2)
            self.assertTrue(i[0] < self.pop.N)
            self.assertTrue(i[1] < self.pop.N)

    def testMutationLookupTable(self):
        from fwdpy11.model_params import ModelParams
        from fwdpy11.wright_fisher import evolve
        params = ModelParams(**self.pdict)
        evolve(self.rng, self.pop, params)
        lookup = self.pop.mut_lookup
        for i in range(len(self.pop.mcounts)):
            if self.pop.mcounts[i] > 0:
                self.assertTrue(self.pop.mutations[i].pos in lookup)
                self.assertTrue(i in lookup[self.pop.mutations[i].pos])

    def testMutationIndices(self):
        from fwdpy11.model_params import ModelParams
        from fwdpy11.wright_fisher import evolve
        params = ModelParams(**self.pdict)
        evolve(self.rng, self.pop, params)
        lookup = self.pop.mut_lookup
        for key, val in lookup.items():
            indexes = self.pop.mutation_indexes(key)
            self.assertTrue(indexes is not None)
            for i in indexes:
                self.assertTrue(i in val)

    def testEmptyMutationLookupTable(self):
        """
        This test does not use the class fixture.
        Instead, we use an empty pop object.
        """
        pop = fp11.SlocusPop(100)
        self.assertTrue(pop.mut_lookup is None)


if __name__ == "__main__":
    unittest.main()
