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
import fwdpy11
import unittest
import pickle
import discrete_demography_roundtrips as ddr
import numpy as np


class TestMoveOrCopyIndividuals(unittest.TestCase):
    """
    Tests functions for object construction and
    object pickling
    """

    def test_move(self):
        m = fwdpy11.move_individuals(0, 2, 1, 0.1)
        self.assertEqual(m.when, 0)
        self.assertEqual(m.source, 2)
        self.assertEqual(m.destination, 1)
        self.assertEqual(m.number, 0)
        self.assertEqual(m.fraction, 0.1)
        self.assertEqual(m.move_individuals, True)
        self.assertEqual(m.resets_growth_rate, True)

        mp = pickle.dumps(m, -1)
        ump = pickle.loads(mp)
        self.assertEqual(ump.when, 0)
        self.assertEqual(ump.source, 2)
        self.assertEqual(ump.destination, 1)
        self.assertEqual(ump.number, 0)
        self.assertEqual(ump.fraction, 0.1)
        self.assertEqual(ump.move_individuals, True)
        self.assertEqual(ump.resets_growth_rate, True)
        self.assertTrue(m == ump)

    def test_copy(self):
        m = fwdpy11.copy_individuals(0, 2, 1, 0.1)
        self.assertEqual(m.when, 0)
        self.assertEqual(m.source, 2)
        self.assertEqual(m.destination, 1)
        self.assertEqual(m.number, 0)
        self.assertEqual(m.fraction, 0.1)
        self.assertEqual(m.move_individuals, False)

        mp = pickle.dumps(m, -1)
        ump = pickle.loads(mp)
        self.assertEqual(ump.when, 0)
        self.assertEqual(ump.source, 2)
        self.assertEqual(ump.destination, 1)
        self.assertEqual(ump.number, 0)
        self.assertEqual(ump.fraction, 0.1)
        self.assertEqual(ump.move_individuals, False)
        self.assertTrue(m == ump)


class TestSetDemeSize(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.ddsc = fwdpy11.SetDemeSize(0, 1, 3)

    def test_property_access(self):
        self.assertEqual(self.ddsc.when, 0)
        self.assertEqual(self.ddsc.deme, 1)
        self.assertEqual(self.ddsc.new_size, 3)
        self.assertEqual(self.ddsc.resets_growth_rate, True)

    def test_pickle(self):
        p = pickle.dumps(self.ddsc, -1)
        up = pickle.loads(p)
        self.assertEqual(self.ddsc.when, up.when)
        self.assertEqual(self.ddsc.deme, up.deme)
        self.assertEqual(self.ddsc.new_size, up.new_size)

    def test_invalid_deme(self):
        with self.assertRaises(ValueError):
            self.dpsc = fwdpy11.SetDemeSize(0, -1, 3)


class TestSetExponentialGrowth(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.seg = fwdpy11.SetExponentialGrowth(0, 1, 0.1)

    def test_property_access(self):
        self.assertEqual(self.seg.when, 0)
        self.assertEqual(self.seg.deme, 1)
        self.assertEqual(self.seg.G, 0.1)

    def test_pickle(self):
        p = pickle.dumps(self.seg, -1)
        up = pickle.loads(p)
        self.assertEqual(self.seg.when, up.when)
        self.assertEqual(self.seg.deme, up.deme)
        self.assertEqual(self.seg.G, up.G)

    def test_invalid_deme(self):
        with self.assertRaises(ValueError):
            self.seg = fwdpy11.SetExponentialGrowth(0, -1, 0.1)

    def test_invalid_growth_rate(self):
        with self.assertRaises(ValueError):
            self.seg = fwdpy11.SetExponentialGrowth(0, 1, np.nan)


class TestMigrationMatrix(unittest.TestCase):
    def testSimpleInit(self):
        fwdpy11.MigrationMatrix(np.identity(2))

    def testShape(self):
        m = fwdpy11.MigrationMatrix(np.identity(2))
        self.assertEqual(m.shape, (2, 2))

    def testPickle(self):
        m = fwdpy11.MigrationMatrix(np.identity(2))
        p = pickle.dumps(m, -1)
        up = pickle.loads(p)
        self.assertEqual(up.shape, (2, 2))
        self.assertTrue(np.array_equal(up.M, np.identity(2)))

    def testSettingRates(self):
        m = fwdpy11.MigrationMatrix(np.identity(2))
        m._set_migration_rates(0, [0.5, 0.5])
        m._set_migration_rates(1, np.array([0.01, 0.99]))
        self.assertTrue(np.array_equal(m.M, np.array(
            [0.5, 0.5, 0.01, 0.99]).reshape(2, 2)))

        m._set_migration_rates(np.array([0, 1, 2, 3]).reshape(2, 2))

        try:
            m._set_migration_rates(0, [2.5, 0.5])
        except:  # NOQA
            self.fail("unexpected exception")

        with self.assertRaises(ValueError):
            # Fails because deme index out of range
            m._set_migration_rates(2, [0.5, 0.5])

    def test_non_square_input(self):
        with self.assertRaises(ValueError):
            fwdpy11.MigrationMatrix(np.array([2.]*2))

        with self.assertRaises(ValueError):
            """ This matrix is also invalid b/c
            rows don't sum to 1, but we expect
            a failure before that check """
            fwdpy11.MigrationMatrix(
                np.array([i for i in range(6)]).reshape(2, 3))

    def test_weights_greater_than_one(self):
        try:
            fwdpy11.MigrationMatrix(np.array([2.]*4).reshape(2, 2))
        except:  # NOQA
            self.fail("unexpected exception")


class TestSetMigrationRates(unittest.TestCase):
    def test_init_from_list(self):
        m = fwdpy11.SetMigrationRates(0, 0, [0, 1, 2])
        self.assertEqual(m.when, 0)
        self.assertEqual(m.deme, 0)
        self.assertTrue(np.array_equal(m.migrates, np.array([0, 1, 2])))

    def test_init_from_numpy(self):
        m = fwdpy11.SetMigrationRates(0, 0, np.array([0, 1, 2]))
        self.assertEqual(m.when, 0)
        self.assertEqual(m.deme, 0)
        self.assertTrue(np.array_equal(m.migrates, np.array([0, 1, 2])))

    def test_reset_entire_matrix(self):
        m = fwdpy11.SetMigrationRates(3, np.identity(3))
        self.assertTrue(np.array_equal(m.migrates, np.identity(3)))

    def test_pickle(self):
        m = fwdpy11.SetMigrationRates(0, 0, np.array([0, 1, 2]))
        p = pickle.dumps(m, -1)
        up = pickle.loads(p)
        self.assertEqual(m.when, up.when)
        self.assertEqual(m.deme, up.deme)
        self.assertEqual(m.migrates.tolist(), up.migrates.tolist())


class TestDiscreteDemographyInitialization(unittest.TestCase):
    def test_init_migmatrix_with_tuple(self):
        try:
            d = fwdpy11.DiscreteDemography(migmatrix=((np.identity(10), True)))
            self.assertEqual(d.migmatrix.scaled, True)
        except:  # NOQA
            self.fail("unexpected exception")
        try:
            d = fwdpy11.DiscreteDemography(
                migmatrix=((np.identity(10), False)))
            self.assertEqual(d.migmatrix.scaled, False)
        except:  # NOQA
            self.fail("unexpected exception")

    def test_move_or_copy(self):
        m = [fwdpy11.move_individuals(0, 0, 1, 0.5)]
        fwdpy11.DiscreteDemography(m)

    def test_setting_growth(self):
        g = [fwdpy11.SetExponentialGrowth(0, 1, 0.3)]
        fwdpy11.DiscreteDemography(set_growth_rates=g)

    def test_setting_size_changes(self):
        c = [fwdpy11.SetDemeSize(0, 1, 15151)]
        fwdpy11.DiscreteDemography(set_deme_sizes=c)

    def test_init_from_numpy(self):
        """
        NOTE: this test is important b/c it tests
        that the __init__ function overloads can be seen.
        If they are re-ordered, then this test may fail.
        """
        N = 1000
        popsizes = np.array([N]*10*N + [int(0.1*N)] *
                            int(0.1*N) + [2*N]*100, dtype=np.uint32)
        demography = fwdpy11.DiscreteDemography(popsizes)
        self.assertEqual(len(np.unique(popsizes)),
                         len(demography.set_deme_sizes))

    def test_init_with_two_growth_changes_same_generation(self):
        g = [fwdpy11.SetExponentialGrowth(0, 1, 0.3)]*2
        with self.assertRaises(ValueError):
            fwdpy11.DiscreteDemography(set_growth_rates=g)

    def test_init_with_two_selfing_changes_same_generation(self):
        g = [fwdpy11.SetSelfingRate(0, 1, 0.3)]*2
        with self.assertRaises(ValueError):
            fwdpy11.DiscreteDemography(set_selfing_rates=g)

    def test_init_with_two_deme_size_changes_same_generation(self):
        c = [fwdpy11.SetDemeSize(0, 1, 15151)]*2
        with self.assertRaises(ValueError):
            fwdpy11.DiscreteDemography(set_deme_sizes=c)

    def test_init_with_two_mass_moves_same_generation(self):
        m = [fwdpy11.move_individuals(0, 0, 1, 0.5)]*2
        with self.assertRaises(ValueError):
            fwdpy11.DiscreteDemography(m)

    def test_init_with_two_mass_copies_same_generation(self):
        m = [fwdpy11.copy_individuals(0, 0, 1, 0.5)]*2
        with self.assertRaises(ValueError):
            fwdpy11.DiscreteDemography(m)

    def test_init_with_one_mass_move_and_one_mass_copy_same_generation(self):
        # Internally, the input data will get sorted
        # so that copies happen before moves.
        m = [fwdpy11.move_individuals(0, 0, 1, 0.5),
             fwdpy11.copy_individuals(0, 0, 1, 0.5)]
        try:
            d = fwdpy11.DiscreteDemography(m)
            self.assertEqual(
                d.mass_migrations[0].move_individuals, False)
            self.assertEqual(d.mass_migrations[1].move_individuals, True)
        except:  # NOQA
            self.fail("unexpected exception")

    def test_move_too_many_individuals_from_same_deme(self):
        # Attempt to move 125% of deme 0
        m = [fwdpy11.move_individuals(0, 0, 1, 0.5),
             fwdpy11.move_individuals(0, 0, 2, 0.75)]
        with self.assertRaises(ValueError):
            fwdpy11.DiscreteDemography(m)

    def test_move_too_many_individuals_from_same_deme_with_copy_in_middle(self):
        # Attempt to move 125% of deme 0
        # This is a test that input data get sorted so
        # that copies are before moves, which will allow
        # detecting the invalid cumulative move attempt
        m = [fwdpy11.move_individuals(0, 0, 1, 0.5),
             fwdpy11.copy_individuals(0, 0, 1, 0.5),
             fwdpy11.move_individuals(0, 0, 2, 0.75)]
        with self.assertRaises(ValueError):
            fwdpy11.DiscreteDemography(m)

    def test_with_migration_matrix(self):
        d = fwdpy11.DiscreteDemography(migmatrix=np.identity(2))
        p = pickle.dumps(d, -1)
        up = pickle.loads(p)
        self.assertTrue(np.array_equal(up.migmatrix.M, np.identity(2)))


class TestDiscreteDemography(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.rng = fwdpy11.GSLrng(42)
        self.pop = fwdpy11.DiploidPopulation(100)

    def test_simple_moves_from_single_deme(self):
        d = fwdpy11.DiscreteDemography(
            [fwdpy11.move_individuals(0, 0, 1, 0.5)])
        ddr.DiscreteDemography_roundtrip(self.rng,
                                         self.pop, d, 1)
        md = np.array(self.pop.diploid_metadata)
        deme_counts = np.unique(md['deme'], return_counts=True)
        self.assertEqual(len(deme_counts[0]), 2)
        for i in range(len(deme_counts[0])):
            self.assertEqual(deme_counts[1][i], 50)

    def test_simple_copies_from_single_deme(self):
        d = fwdpy11.DiscreteDemography(
            [fwdpy11.copy_individuals(0, 0, 1, 0.5)])
        ddr.DiscreteDemography_roundtrip(self.rng,
                                         self.pop, d, 1)
        md = np.array(self.pop.diploid_metadata)
        deme_counts = np.unique(md['deme'], return_counts=True)
        expected = {0: 100, 1: 50}
        self.assertEqual(len(deme_counts[0]), len(expected))
        for i in range(len(deme_counts[0])):
            self.assertEqual(deme_counts[1][i], expected[i])

    def test_simple_back_and_forth_move(self):
        d = fwdpy11.DiscreteDemography(
            [fwdpy11.move_individuals(1, 0, 1, 0.5),
             fwdpy11.move_individuals(2, 1, 0, 1.)])

        ddr.DiscreteDemography_roundtrip(self.rng,
                                         self.pop, d, 3)
        md = np.array(self.pop.diploid_metadata)
        deme_counts = np.unique(md['deme'], return_counts=True)
        self.assertEqual(len(deme_counts[0]), 1)
        for i in range(len(deme_counts[0])):
            self.assertEqual(deme_counts[1][i], self.pop.N)

    def test_simple_back_and_forth_copy(self):
        d = fwdpy11.DiscreteDemography(
            [fwdpy11.copy_individuals(1, 0, 1, 0.5),
             fwdpy11.copy_individuals(2, 1, 0, 1.)])

        ddr.DiscreteDemography_roundtrip(self.rng,
                                         self.pop, d, 3)
        md = np.array(self.pop.diploid_metadata)
        deme_counts = np.unique(md['deme'], return_counts=True)
        expected = {0: 150, 1: 50}
        self.assertEqual(len(deme_counts[0]), len(expected))
        for i in range(len(deme_counts[0])):
            self.assertEqual(deme_counts[1][i], expected[i])

    def test_simple_moves_from_multiple_demes(self):
        # Set 1/2 the population to start in deme 1:
        md = np.array(self.pop.diploid_metadata, copy=False)
        md['deme'][self.pop.N//2:] = 1
        # In generation 0, we move 1/2 of deme 1 to
        # deme 2, which creates a new deme:
        d = fwdpy11.DiscreteDemography(
            [fwdpy11.move_individuals(0, 1, 2, 0.5)])
        # Evolve for one generation:
        ddr.DiscreteDemography_roundtrip(self.rng,
                                         self.pop, d, 1)
        # We now expect 50, 25, and 25 individuals in
        # demes 0, 1, and 2
        md = np.array(self.pop.diploid_metadata)
        deme_counts = np.unique(md['deme'], return_counts=True)
        self.assertEqual(len(deme_counts[0]), 3)
        expected = {0: 50, 1: 25, 2: 25}
        for i in range(len(deme_counts[0])):
            self.assertEqual(deme_counts[1][i], expected[i])

    def test_simple_copies_from_multiple_demes(self):
        # Set 1/2 the population to start in deme 1:
        md = np.array(self.pop.diploid_metadata, copy=False)
        md['deme'][self.pop.N//2:] = 1
        # In generation 0, we move 1/2 of deme 1 to
        # deme 2, which creates a new deme:
        d = fwdpy11.DiscreteDemography(
            [fwdpy11.copy_individuals(0, 1, 2, 0.5)])
        # Evolve for one generation:
        ddr.DiscreteDemography_roundtrip(self.rng,
                                         self.pop, d, 1)
        # We now expect 50, 50, and 25 individuals in
        # demes 0, 1, and 2
        md = np.array(self.pop.diploid_metadata)
        deme_counts = np.unique(md['deme'], return_counts=True)
        expected = {0: 50, 1: 50, 2: 25}
        self.assertEqual(len(deme_counts[0]), len(expected))
        for i in range(len(deme_counts[0])):
            self.assertEqual(deme_counts[1][i], expected[i])

    def test_single_deme_growth(self):
        N1 = 3412
        t = 111
        G = np.exp((np.log(N1)-np.log(self.pop.N))/t)
        g = [fwdpy11.SetExponentialGrowth(16, 0, G)]
        d = fwdpy11.DiscreteDemography(set_growth_rates=g)
        ddr.DiscreteDemography_roundtrip(self.rng,
                                         self.pop, d, 15 + t + 1)
        self.assertEqual(self.pop.N, N1)
        self.assertEqual(len(self.pop.diploid_metadata), N1)

    def test_two_deme_growth(self):
        N0 = [90, 10]
        md = np.array(self.pop.diploid_metadata, copy=False)
        md['deme'][N0[0]:] = 1
        t = [14, 23]  # generations of growth in each deme
        N1 = [5361, 616]
        G0 = np.exp((np.log(N1[0])-np.log(N0[0]))/t[0])
        G1 = np.exp((np.log(N1[1])-np.log(N0[1]))/t[1])

        g = []
        g.append(fwdpy11.SetExponentialGrowth(7, 0, G0))
        g.append(fwdpy11.SetExponentialGrowth(7+t[0], 0, fwdpy11.NOGROWTH))
        g.append(fwdpy11.SetExponentialGrowth(33, 1, G1))
        g.append(fwdpy11.SetExponentialGrowth(33+t[1], 1, fwdpy11.NOGROWTH))
        d = fwdpy11.DiscreteDemography(set_growth_rates=g)
        ddr.DiscreteDemography_roundtrip(self.rng, self.pop,
                                         d, 100)

        md = np.array(self.pop.diploid_metadata, copy=False)
        self.assertEqual(self.pop.N, sum(N1))
        deme_sizes = np.unique(md['deme'], return_counts=True)
        for i, j in zip(deme_sizes[1], N1):
            self.assertEqual(i, j)

    def test_two_deme_growth_with_hard_reset(self):
        N0 = [90, 10]
        md = np.array(self.pop.diploid_metadata, copy=False)
        md['deme'][N0[0]:] = 1
        t = [14, 23]  # generations of growth in each deme
        N1 = [5361, 616]
        G0 = np.exp((np.log(N1[0])-np.log(N0[0]))/t[0])
        G1 = np.exp((np.log(N1[1])-np.log(N0[1]))/t[1])

        g = []
        g.append(fwdpy11.SetExponentialGrowth(7, 0, G0))
        g.append(fwdpy11.SetExponentialGrowth(33, 1, G1))
        g.append(fwdpy11.SetExponentialGrowth(33+t[1], 1, fwdpy11.NOGROWTH))
        # Cut off the growth in deme 0 after a few generations,
        # and manually set the new deme size to 100 w/no growth
        p = [fwdpy11.SetDemeSize(11, 0, 100)]
        d = fwdpy11.DiscreteDemography(set_deme_sizes=p,
                                       set_growth_rates=g)
        ddr.DiscreteDemography_roundtrip(self.rng, self.pop,
                                         d, 100)

        md = np.array(self.pop.diploid_metadata, copy=False)
        deme_sizes = np.unique(md['deme'], return_counts=True)
        N1 = [100, N1[1]]
        self.assertEqual(self.pop.N, sum(N1))
        for i, j in zip(deme_sizes[1], N1):
            self.assertEqual(i, j)

    def test_two_deme_growth_without_hard_reset(self):
        N0 = [90, 10]
        md = np.array(self.pop.diploid_metadata, copy=False)
        md['deme'][N0[0]:] = 1
        t = [14, 23]  # generations of growth in each deme
        N1 = [5361, 616]
        G0 = np.exp((np.log(N1[0])-np.log(N0[0]))/t[0])
        G1 = np.exp((np.log(N1[1])-np.log(N0[1]))/t[1])

        g = []
        g.append(fwdpy11.SetExponentialGrowth(7, 0, G0))
        g.append(fwdpy11.SetExponentialGrowth(7+t[0], 0, fwdpy11.NOGROWTH))
        g.append(fwdpy11.SetExponentialGrowth(33, 1, G1))
        g.append(fwdpy11.SetExponentialGrowth(33+t[1], 1, fwdpy11.NOGROWTH))
        # after X generations of growth, N[0] changes to 100
        # and the growth rate is not reset.
        p = [fwdpy11.SetDemeSize(11, 0, 100, False)]
        d = fwdpy11.DiscreteDemography(set_growth_rates=g,
                                       set_deme_sizes=p)
        ddr.DiscreteDemography_roundtrip(self.rng, self.pop,
                                         d, 100)

        md = np.array(self.pop.diploid_metadata, copy=False)
        deme_sizes = np.unique(md['deme'], return_counts=True)
        N1[0] = np.round(100.*np.power(G0, 7 + t[0] - 11))
        self.assertEqual(self.pop.N, sum(N1))
        for i, j in zip(deme_sizes[1], N1):
            self.assertEqual(i, j)

    def test_two_moves_in_same_generation(self):
        """
        In generation 0, deme 0 splits equally
        into demes 1 and 2.  This should leave
        deme 0 empty and the sizes of demes
        1 and 2 both equal to 0.5 the initial
        size.
        """
        m = [fwdpy11.move_individuals(0, 0, 2, 0.5),
             fwdpy11.move_individuals(0, 0, 1, 0.5)]
        d = fwdpy11.DiscreteDemography(m)
        N0 = self.pop.N
        ddr.DiscreteDemography_roundtrip(self.rng, self.pop, d, 1)
        md = np.array(self.pop.diploid_metadata)
        expected = {0: 0, 1: N0//2, 2: N0//2}
        dc = np.unique(md['deme'], return_counts=True)
        for i, j in zip(dc[0], dc[1]):
            self.assertEqual(expected[i], j)

    def test_copies_happen_before_moves(self):
        """
        This is a more complex test.
        In the same generation:
        1. All individuals are copied from deme 0 to deme 1.
        2. 50% of deme 0 moves to deme 2.
        3. 50% of deme 0 moves to deme 3.

        This, at the end, the size of deme 1 should be
        the initial size and the size of demes 2 and 3
        should be 0.5*initial size
        """
        m = [fwdpy11.move_individuals(0, 0, 3, 0.5),
             fwdpy11.copy_individuals(0, 0, 1, 1),
             fwdpy11.move_individuals(0, 0, 2, 0.5)]
        d = fwdpy11.DiscreteDemography(m)
        N0 = self.pop.N
        ddr.DiscreteDemography_roundtrip(self.rng, self.pop, d, 1)
        md = np.array(self.pop.diploid_metadata)
        expected = {0: 0, 1: N0, 2: N0//2, 3: N0//2}
        dc = np.unique(md['deme'], return_counts=True)
        for i, j in zip(dc[0], dc[1]):
            self.assertEqual(expected[i], j)

    def test_mass_move_with_growth(self):
        """
        In generation 5, the mass movement from 0 to 1
        will reset the growth rate in deme 0 to
        fwdpy11.NOGROWTH

        This test is also handy b/c growth results in
        an odd total N by the time the mass migration happens
        """
        m = [fwdpy11.move_individuals(5, 0, 1, 0.5)]
        g = [fwdpy11.SetExponentialGrowth(0, 0, 1.1)]
        d = fwdpy11.DiscreteDemography(mass_migrations=m, set_growth_rates=g)
        N0 = self.pop.N
        ddr.DiscreteDemography_roundtrip(self.rng, self.pop, d, 10)
        md = np.array(self.pop.diploid_metadata)
        deme_counts = np.unique(md['deme'], return_counts=True)
        N5 = np.round(N0*np.power(g[0].G, 5))
        N_after_mass_mig = [N5//2, N5-N5//2]
        for i, j in zip(deme_counts[1], N_after_mass_mig):
            self.assertEqual(i, j)

    def test_mass_move_with_growth_no_reset(self):
        """
        In generation 5, the mass movement from 0 to 1
        """
        m = [fwdpy11.move_individuals(5, 0, 1, 0.5, False)]
        g = [fwdpy11.SetExponentialGrowth(0, 0, 1.1)]
        d = fwdpy11.DiscreteDemography(mass_migrations=m, set_growth_rates=g)
        N0 = self.pop.N
        ddr.DiscreteDemography_roundtrip(self.rng, self.pop, d, 10)
        md = np.array(self.pop.diploid_metadata)
        deme_counts = np.unique(md['deme'], return_counts=True)
        N5 = np.round(N0*np.power(g[0].G, 5))
        N_after_mass_mig_0 = np.round((N5//2)*np.power(g[0].G, 5))
        N = [N_after_mass_mig_0, N5 - N5//2]
        for i, j in zip(N, deme_counts[1]):
            self.assertEqual(i, j)

    def test_migration_matrix_too_small(self):
        """
        The mig matrix is 2x2 but a mass migration event
        tries to create a 3rd deme, which triggers an exception
        """
        mm = np.array([0.5]*4).reshape(2, 2)
        m = [fwdpy11.move_individuals(0, 0, 2, 0.5)]
        md = np.array(self.pop.diploid_metadata, copy=False)
        md['deme'][len(md)//2:] = 1
        d = fwdpy11.DiscreteDemography(mass_migrations=m, migmatrix=mm)
        with self.assertRaises(ValueError):
            ddr.DiscreteDemography_roundtrip(self.rng, self.pop, d, 5)

    def test_simple_two_deme_migration(self):
        mm = np.array([0.5]*4).reshape(2, 2)
        md = np.array(self.pop.diploid_metadata, copy=False)
        md['deme'][len(md)//2:] = 1
        d = fwdpy11.DiscreteDemography(migmatrix=mm)
        N = self.pop.N
        ddr.DiscreteDemography_roundtrip(self.rng, self.pop, d, 5)
        self.assertEqual(N, self.pop.N)
        md = np.array(self.pop.diploid_metadata, copy=False)
        deme_sizes = np.unique(md['deme'], return_counts=True)
        for i in deme_sizes[1]:
            self.assertEqual(i, self.pop.N//2)

    def test_change_migration_rates_simple_two_deme_migration(self):
        """
        For a 2-deme model, the mig matrix is
        [[0, 1]
         [1, 0]]
        so that all offspring have both parents from the other deme,
        which gives us an easy check on how many migration events
        will be recorded by the test simulation.

        After 3 generations, we reset the migration rates to be
        [[0.5, 0.5],
         [[0, 0]]
        so that all parents are from deme zero.
        """
        mm = np.array([0, 1, 1, 0]).reshape(2, 2)
        mmigs = [fwdpy11.move_individuals(0, 0, 1, 0.5)]
        smr = [fwdpy11.SetMigrationRates(
            3, np.array([0.5, 0.5, 0, 0]).reshape(2, 2))]
        d = fwdpy11.DiscreteDemography(mass_migrations=mmigs, migmatrix=mm,
                                       set_migration_rates=smr)
        N = self.pop.N
        migevents = ddr.DiscreteDemography_roundtrip(self.rng, self.pop, d, 5)
        self.assertEqual(N, self.pop.N)
        self.assertEqual(len(migevents), 2*N*3 + 2*N)
        md = np.array(self.pop.diploid_metadata, copy=False)
        deme_sizes = np.unique(md['deme'], return_counts=True)
        for i in deme_sizes[1]:
            self.assertEqual(i, self.pop.N//2)

    def test_change_migration_rates_simple_two_deme_migration_bad_matrix(self):
        """
        For a 2-deme model, the mig matrix is
        [0, 1
         1, 0]
        so that all offspring have both parents from the other deme,
        which gives us an easy check on how many migration events
        will be recorded by the test simulation.

        After 3 generations, we reset the migration rates to be
        [[1,0],
         [1,0]],
        which leads to there being no parents for deme 1, raising a
        MigrationError exception.
        """
        mm = np.array([0, 1, 1, 0]).reshape(2, 2)
        mmigs = [fwdpy11.move_individuals(0, 0, 1, 0.5)]
        smr = [fwdpy11.SetMigrationRates(
            3, np.array([1, 0, 1, 0]).reshape(2, 2))]
        d = fwdpy11.DiscreteDemography(mass_migrations=mmigs, migmatrix=mm,
                                       set_migration_rates=smr)
        with self.assertRaises(fwdpy11.MigrationError):
            ddr.DiscreteDemography_roundtrip(self.rng, self.pop, d, 5)

    def test_migrration_rates_larger_than_one(self):
        """
        Same as a previous tests, but rates are "weights"
        rather than "probabilities"

        """
        mm = np.array([0, 2, 2, 0]).reshape(2, 2)
        mmigs = [fwdpy11.move_individuals(0, 0, 1, 0.5)]
        smr = [fwdpy11.SetMigrationRates(
            3, np.array([1.5, 1.5, 0, 0]).reshape(2, 2))]
        d = fwdpy11.DiscreteDemography(mass_migrations=mmigs, migmatrix=mm,
                                       set_migration_rates=smr)
        N = self.pop.N
        migevents = ddr.DiscreteDemography_roundtrip(self.rng, self.pop, d, 5)
        self.assertEqual(N, self.pop.N)
        self.assertEqual(len(migevents), 2*N*3 + 2*N)
        md = np.array(self.pop.diploid_metadata, copy=False)
        deme_sizes = np.unique(md['deme'], return_counts=True)
        for i in deme_sizes[1]:
            self.assertEqual(i, self.pop.N//2)

    def test_selfing_vs_migration(self):
        """
        Parents of deme 0 are all migrants from deme 1.
        Parents of deme 1 are all migrants from deme 0.
        Deme 0 never selfs.  Deme 1 always selfs.
        """
        mm = np.array([0, 1, 1, 0]).reshape(2, 2)
        mmigs = [fwdpy11.move_individuals(0, 0, 1, 0.5)]
        s = [fwdpy11.SetSelfingRate(0, 1, 1.0)]
        mmigs = [fwdpy11.move_individuals(0, 0, 1, 0.5)]
        d = fwdpy11.DiscreteDemography(
            mass_migrations=mmigs, migmatrix=mm, set_selfing_rates=s)
        migevents = ddr.DiscreteDemography_roundtrip(self.rng, self.pop, d, 5)
        for m in migevents:
            if m[1] == 1:  # parent is from deme 1
                self.assertTrue(m[3] == ddr.MatingEventType.selfing)
                self.assertNotEqual(m[1], m[2])  # Must be a migrant parent
            elif m[1] == 0:
                self.assertTrue(m[3] == ddr.MatingEventType.outcrossing)
                self.assertNotEqual(m[1], m[2])  # Must be a migrant parent
            else:
                self.fail("invalid parental deme type")


if __name__ == "__main__":
    unittest.main()
