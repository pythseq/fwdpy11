//
// Copyright (C) 2017 Kevin Thornton <krthornt@uci.edu>
//
// This file is part of fwdpy11.
//
// fwdpy11 is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// fwdpy11 is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with fwdpy11.  If not, see <http://www.gnu.org/licenses/>.
//
#include <cmath>
#include <memory>
#include <functional>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <fwdpp/fitness_models.hpp>
#include <fwdpy11/genetic_values/GeneticValueToFitness.hpp>
#include <fwdpy11/genetic_values/SlocusPopGeneticValue.hpp>
#include <fwdpy11/genetic_values/SlocusPopGeneticValueWithMapping.hpp>
#include <fwdpy11/genetic_values/MlocusPopGeneticValue.hpp>
#include <fwdpy11/genetic_values/MlocusPopGeneticValueWithMapping.hpp>
#include <fwdpy11/genetic_values/SlocusAdditive.hpp>
#include <fwdpy11/genetic_values/SlocusMult.hpp>
#include <fwdpy11/genetic_values/SlocusGBR.hpp>
#include <fwdpy11/genetic_values/details/mlocus_aggregators.hpp>
#include <fwdpy11/genetic_values/MlocusAdditive.hpp>
#include <fwdpy11/genetic_values/MlocusMult.hpp>
#include <fwdpy11/genetic_values/MlocusGBR.hpp>
#include <fwdpy11/genetic_values/noise.hpp>
#include <fwdpy11/genetic_values/default_update.hpp>

namespace py = pybind11;

PYBIND11_MODULE(genetic_values, m)
{
    auto imported_noise = static_cast<pybind11::object>(
        pybind11::module::import("fwdpy11.genetic_value_noise"));

    py::enum_<fwdpp::additive_diploid::policy>(m, "AdditivePolicy")
        .value("aw", fwdpp::additive_diploid::policy::aw)
        .value("atrait", fwdpp::additive_diploid::policy::atrait)
        .export_values();

    py::enum_<fwdpp::multiplicative_diploid::policy>(m, "MultiplicativePolicy")
        .value("mw", fwdpp::multiplicative_diploid::policy::mw)
        .value("mtrait", fwdpp::multiplicative_diploid::policy::mtrait)
        .export_values();

    py::class_<fwdpy11::SlocusPopGeneticValue>(
        m, "SlocusPopGeneticValue",
        "ABC for genetic value calculations for diploid members of "
        ":class:`fwdpy11.SlocusPop`")
        .def("__call__",
             [](const fwdpy11::SlocusPopGeneticValue& gv,
                const std::size_t diploid_index,
                const fwdpy11::SlocusPop& pop) {
                 return gv(diploid_index, pop);
             },
             R"delim(
             Calculate the genetic value for an individual.
             
             :param diploid_index: The index of the individual to calculate.
             :type diploid_index: int >= 0
             :param pop: The population object containing the individual.
             :type pop: :class:`fwdpy11.SlocusPop`
             )delim",
             py::arg("diploid_index"), py::arg("pop"))
        .def("fitness",
             [](const fwdpy11::SlocusPopGeneticValue& gv,
                const std::size_t diploid_index,
                const fwdpy11::SlocusPop& pop) {
                 return gv.genetic_value_to_fitness(
                     pop.diploid_metadata[diploid_index]);
             },
             R"delim(
        Return the fitness of an individual.
        
        :param diploid_index: The index of the individual
        :type diploid_index: int >= 0
        :param pop: The population containing the individual
        :type pop: :class:`fwdpy11.SlocusPop`
        )delim",
             py::arg("diploid_index"), py::arg("pop"));

    py::class_<fwdpy11::SlocusPopGeneticValueWithMapping,
               fwdpy11::SlocusPopGeneticValue>(
        m, "SlocusPopGeneticValueWithMapping",
        "Genetic value calculations with flexible mapping of genetic value to "
        "fitness.")
        .def_property_readonly(
            "gvalue_to_fitness",
            [](const fwdpy11::SlocusPopGeneticValueWithMapping& o) {
                return o.gv2w->clone();
            },
            "Access the genetic value to fitness map.")
        .def_property_readonly(
            "noise",
            [](const fwdpy11::SlocusPopGeneticValueWithMapping& o) {
                return o.noise_fxn->clone();
            },
            "Access the random noise funcion");

    py::class_<fwdpy11::SlocusAdditive,
               fwdpy11::SlocusPopGeneticValueWithMapping>(
        m, "SlocusAdditive", "Additive genetic values.")
        .def(py::init([](const double scaling) {
                 return fwdpy11::SlocusAdditive(fwdpp::additive_diploid(
                     scaling, fwdpp::additive_diploid::policy::aw));
             }),
             py::arg("scaling"),
             R"delim(
             Additive effects on fitness.

             :param scaling: How to treat mutant homozygotes.
             :type scaling: float

             For a model of fitness, the genetic value is 1, 1+e*h,
             1+scaling*e for genotypes AA, Aa, and aa, respectively.
             )delim")
        .def(py::init([](const double scaling,
                         const fwdpy11::GeneticValueIsTrait& g) {
                 return fwdpy11::SlocusAdditive(
                     fwdpp::additive_diploid(
                         scaling, fwdpp::additive_diploid::policy::atrait),
                     g);
             }),
             py::arg("scaling"), py::arg("gv2w"),
             R"delim(
             Construct an object of additive effects on a trait with a specific
             functional mapping from genetic value to fitness.

             :param scaling: How to treat mutant homozygotes.
             :type scaling: float
             :param gv2w: Map from genetic value to fitness.
             :type gv2w: :class:`fwdpy11.genetic_values.GeneticValueIsTrait`
             )delim")
        .def(py::init([](const double scaling,
                         const fwdpy11::GeneticValueIsTrait& g,
                         const fwdpy11::GeneticValueNoise& n) {
                 return fwdpy11::SlocusAdditive(
                     fwdpp::additive_diploid(
                         scaling, fwdpp::additive_diploid::policy::atrait),
                     g, n);
             }),
             py::arg("scaling"), py::arg("gv2w"), py::arg("noise"),
             R"delim(
             Additive effects on a trait with a specific mapping from 
             genetic value to fitness and random effects ("noise").

             :param scaling: How to treat mutant homozygotes.
             :type scaling: float
             :param gv2w: Map from genetic value to fitness.
             :type gv2w: :class:`fwdpy11.genetic_values.GeneticValueIsTrait`
             :param noise: Function to generate random effects on trait value.
             :type noise: :class:`fwdpy11.genetic_value_noise.GeneticValueNoise`
             )delim")
        .def_property_readonly(
            "scaling",
            [](const fwdpy11::SlocusAdditive& wa) { return wa.gv.scaling; },
            "Access to the scaling parameter.")
        .def_property_readonly(
            "is_fitness",
            [](const fwdpy11::SlocusAdditive& wa) {
                return wa.gv.p == fwdpp::additive_diploid::policy::aw;
            },
            "Returns True if instance calculates fitness as the genetic value "
            "and False if the genetic value is a trait value.");

    py::class_<fwdpy11::SlocusMult, fwdpy11::SlocusPopGeneticValueWithMapping>(
        m, "SlocusMult", "Multiplicative genetic values.")
        .def(py::init([](const double scaling) {
                 return fwdpy11::SlocusMult(fwdpp::multiplicative_diploid(
                     scaling, fwdpp::multiplicative_diploid::policy::mw));
             }),
             py::arg("scaling"),
             R"delim(
             Multiplicative effects on fitness.

             :param scaling: How to treat mutant homozygotes.
             :type scaling: float

             For a model of fitness, the genetic value is 1, 1+e*h,
             1+scaling*e for genotypes AA, Aa, and aa, respectively.
             )delim")
        .def(py::init([](const double scaling,
                         const fwdpy11::GeneticValueIsTrait& g) {
                 return fwdpy11::SlocusMult(
                     fwdpp::multiplicative_diploid(
                         scaling,
                         fwdpp::multiplicative_diploid::policy::mtrait),
                     g);
             }),
             py::arg("scaling"), py::arg("gv2w"),
             R"delim(
             Construct an object of multiplicative effects on a trait with a specific
             functional mapping from genetic value to fitness.

             :param scaling: How to treat mutant homozygotes.
             :type scaling: float
             :param gv2w: Map from genetic value to fitness.
             :type gv2w: :class:`fwdpy11.genetic_values.GeneticValueIsTrait`
             )delim")
        .def(py::init([](const double scaling,
                         const fwdpy11::GeneticValueIsTrait& g,
                         const fwdpy11::GeneticValueNoise& n) {
                 return fwdpy11::SlocusMult(
                     fwdpp::multiplicative_diploid(
                         scaling,
                         fwdpp::multiplicative_diploid::policy::mtrait),
                     g, n);
             }),
             py::arg("scaling"), py::arg("gv2w"), py::arg("noise"),
             R"delim(
             Multiplicative effects on a trait with a specific mapping from 
             genetic value to fitness and random effects ("noise").

             :param scaling: How to treat mutant homozygotes.
             :type scaling: float
             :param gv2w: Map from genetic value to fitness.
             :type gv2w: :class:`fwdpy11.genetic_values.GeneticValueIsTrait`
             :param noise: Function to generate random effects on trait value.
             :type noise: :class:`fwdpy11.genetic_value_noise.GeneticValueNoise`
             )delim")
        .def_property_readonly(
            "scaling",
            [](const fwdpy11::SlocusMult& wa) { return wa.gv.scaling; },
            "Access to the scaling parameter.")
        .def_property_readonly(
            "is_fitness",
            [](const fwdpy11::SlocusMult& wa) {
                return wa.gv.p == fwdpp::multiplicative_diploid::policy::mw;
            },
            "Returns True if instance calculates fitness as the genetic value "
            "and False if the genetic value is a trait value.");

    py::class_<fwdpy11::SlocusGBR, fwdpy11::SlocusPopGeneticValueWithMapping>(
        m, "SlocusGBR",
        R"delim(
        The "gene-based recessive" trait model described in Thornton et al.
        2013 http://dx.doi.org/10.1371/journal.pgen.1003258 and Sanjak et al. 2017
        http://dx.doi.org/10.1371/journal.pgen.1006573.

        The trait value is the geometric mean of the sum of effect sizes on each haplotype.
        It is undefined for the case where these sums are negative.
        )delim")
        .def(py::init([](const fwdpy11::GeneticValueIsTrait& gv2w) {
                 return fwdpy11::SlocusGBR(fwdpy11::GBR{}, gv2w);
             }),
             py::arg("gv2w"),
             R"delim(
             Construct object with specific genetic value to fitness map.
             
             :param gv2w: Genetic value to fitness map
             :type gv2w: :class:`fwdpy11.genetic_values.GeneticValueIsTrait`
             )delim")
        .def(py::init([](const fwdpy11::GeneticValueIsTrait& gv2w,
                         const fwdpy11::GeneticValueNoise& noise) {
                 return fwdpy11::SlocusGBR(fwdpy11::GBR{}, gv2w, noise);
             }),
             py::arg("gv2w"), py::arg("noise"),
             R"delim(
             Construct object with specific genetic value to fitness map 
             and random effects on trait value.
             
             :param gv2w: Genetic value to fitness map
             :type gv2w: :class:`fwdpy11.genetic_values.GeneticValueIsTrait`
             :param noise: Model of random effects on trait value.
             :type noise: :class:`fwdpy11.genetic_value_noise.GeneticValueNoise`
             )delim");

    // Classes for Mlocus genetic values
    py::class_<fwdpy11::MlocusPopGeneticValue>(
        m, "MlocusPopGeneticValue",
        "ABC for genetic value calculations for diploid members of "
        ":class:`fwdpy11.MlocusPop`")
        .def("__call__",
             [](const fwdpy11::MlocusPopGeneticValue& gv,
                const std::size_t diploid_index,
                const fwdpy11::MlocusPop& pop) {
                 return gv(diploid_index, pop);
             },
             R"delim(
             Calculate the genetic value for an individual.
             
             :param diploid_index: The index of the individual to calculate.
             :type diploid_index: int >= 0
             :param pop: The population object containing the individual.
             :type pop: :class:`fwdpy11.MlocusPop`
             )delim",
             py::arg("diploid_index"), py::arg("pop"))
        .def("fitness",
             [](const fwdpy11::MlocusPopGeneticValue& gv,
                const std::size_t diploid_index,
                const fwdpy11::MlocusPop& pop) {
                 return gv.genetic_value_to_fitness(
                     pop.diploid_metadata[diploid_index]);
             },
             R"delim(
             Calculate the genetic value for an individual.
             
             :param diploid_index: The index of the individual to calculate.
             :type diploid_index: int >= 0
             :param pop: The population object containing the individual.
             :type pop: :class:`fwdpy11.MlocusPop`
             )delim",
             py::arg("diploid_index"), py::arg("pop"));

    py::class_<fwdpy11::MlocusPopGeneticValueWithMapping,
               fwdpy11::MlocusPopGeneticValue>(
        m, "MlocusPopGeneticValueWithMapping",
        "Genetic value calculations with flexible mapping of genetic value to "
        "fitness.")
        .def_property_readonly(
            "gvalue_to_fitness",
            [](const fwdpy11::MlocusPopGeneticValueWithMapping& o) {
                return o.gv2w->clone();
            },
            "Access the genetic value to fitness map.")
        .def_property_readonly(
            "noise",
            [](const fwdpy11::MlocusPopGeneticValueWithMapping& o) {
                return o.noise_fxn->clone();
            },
            "Access the random noise function.");

    py::class_<fwdpy11::MlocusAdditive,
               fwdpy11::MlocusPopGeneticValueWithMapping>(m, "MlocusAdditive")
        .def(py::init([](const double scaling) {
                 return fwdpy11::MlocusAdditive(
                     fwdpp::additive_diploid(
                         scaling, fwdpp::additive_diploid::policy::aw),
                     fwdpy11::aggregate_additive_fitness());
             }),
             py::arg("scaling"))
        .def(py::init([](const double scaling,
                         const fwdpy11::GeneticValueIsTrait& gv2w) {
                 return fwdpy11::MlocusAdditive(
                     fwdpp::additive_diploid(
                         scaling, fwdpp::additive_diploid::policy::atrait),
                     fwdpy11::aggregate_additive_trait(), gv2w);
             }),
             py::arg("scaling"), py::arg("gv2w"))
        .def(py::init([](const double scaling,
                         const fwdpy11::GeneticValueIsTrait& gv2w,
                         const fwdpy11::GeneticValueNoise& noise) {
                 return fwdpy11::MlocusAdditive(
                     fwdpp::additive_diploid(
                         scaling, fwdpp::additive_diploid::policy::atrait),
                     fwdpy11::aggregate_additive_trait(), gv2w, noise);
             }),
             py::arg("scaling"), py::arg("gv2w"), py::arg("noise"));

    py::class_<fwdpy11::MlocusMult, fwdpy11::MlocusPopGeneticValueWithMapping>(
        m, "MlocusMult")
        .def(py::init([](const double scaling) {
                 return fwdpy11::MlocusMult(
                     fwdpp::multiplicative_diploid(
                         scaling, fwdpp::multiplicative_diploid::policy::mw),
                     fwdpy11::aggregate_mult_fitness());
             }),
             py::arg("scaling"))
        .def(py::init([](const double scaling,
                         const fwdpy11::GeneticValueIsTrait& gv2w) {
                 return fwdpy11::MlocusMult(
                     fwdpp::multiplicative_diploid(
                         scaling,
                         fwdpp::multiplicative_diploid::policy::mtrait),
                     fwdpy11::aggregate_mult_trait(), gv2w);
             }),
             py::arg("scaling"), py::arg("gv2w"))
        .def(py::init([](const double scaling,
                         const fwdpy11::GeneticValueIsTrait& gv2w,
                         const fwdpy11::GeneticValueNoise& noise) {
                 return fwdpy11::MlocusMult(
                     fwdpp::multiplicative_diploid(
                         scaling,
                         fwdpp::multiplicative_diploid::policy::mtrait),
                     fwdpy11::aggregate_mult_trait(), gv2w, noise);
             }),
             py::arg("scaling"), py::arg("gv2w"), py::arg("scaling"));

    py::class_<fwdpy11::MlocusGBR, fwdpy11::MlocusPopGeneticValueWithMapping>(
        m, "MlocusGBR"
           R"delim(
        The "gene-based recessive" trait model described in Thornton et al.
        2013 http://dx.doi.org/10.1371/journal.pgen.1003258 and Sanjak et al. 2017
        http://dx.doi.org/10.1371/journal.pgen.1006573.

        The trait value is the geometric mean of the sum of effect sizes on each haplotype.
        It is undefined for the case where these sums are negative.

        The final genetic value is additive across loci.  The GBR model is applied within
        loci.
        )delim")
        .def(py::init([](const fwdpy11::GeneticValueIsTrait& gv2w) {
                 return fwdpy11::MlocusGBR(fwdpy11::GBR{},
                                           fwdpy11::aggregate_additive_trait(),
                                           gv2w);
             }),
             py::arg("gv2w"))
        .def(py::init([](const fwdpy11::GeneticValueIsTrait& gv2w,
                         const fwdpy11::GeneticValueNoise& noise) {
                 return fwdpy11::MlocusGBR(fwdpy11::GBR{},
                                           fwdpy11::aggregate_additive_trait(),
                                           gv2w, noise);
             }),
             py::arg("gv2w"), py::arg("noise"));

    py::class_<fwdpy11::GeneticValueToFitnessMap>(
        m, "GeneticValueToFitnessMap",
        "ABC for functions translating genetic values into fitness.");

    py::class_<fwdpy11::GeneticValueIsTrait,
               fwdpy11::GeneticValueToFitnessMap>(m, "GeneticValueIsTrait",
                                                  "ABC");

    py::class_<fwdpy11::GeneticValueIsFitness,
               fwdpy11::GeneticValueToFitnessMap>(m, "GeneticValueIsFitness")
        .def(py::init<>());

    py::class_<fwdpy11::GSS, fwdpy11::GeneticValueIsTrait>(
        m, "GSS", "Gaussian stabilizing selection.")
        .def(py::init<double, double>(), py::arg("opt"), py::arg("VS"))
        .def_readonly("VS", &fwdpy11::GSS::VS)
        .def_readonly("opt", &fwdpy11::GSS::opt);

    py::class_<fwdpy11::GSSmo, fwdpy11::GeneticValueIsTrait>(
        m, "GSSmo", "Gaussian stabilizing selection with a moving optimum.")
        .def(
            py::init<std::vector<std::tuple<std::uint32_t, double, double>>>(),
            py::arg("optima"));
}
