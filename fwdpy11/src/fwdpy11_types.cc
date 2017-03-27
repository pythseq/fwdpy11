#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include <fwdpy11/types.hpp>

namespace py = pybind11;

using fwdpp_popgenmut_base = fwdpy11::singlepop_t::popbase_t;
using singlepop_sugar_base = fwdpy11::singlepop_t::base;

PYBIND11_PLUGIN(fwdpy11_types) {
    py::module m("fwdpy11_types", "Wrap C++ types specific to fwdpy11.");

    py::class_<fwdpy11::GSLrng_t>(
        m, "GSLrng", "Random number generator based on a mersenne twister.")
        .def(py::init<unsigned>(),
             "Constructor takes unsigned integer as a seed");

    py::class_<fwdpy11::diploid_t>(
        m, "SingleLocusDiploid",
        "Diploid data type for a single (usually contiguous) genomic region")
        .def(py::init<>())
        .def(py::init<std::size_t, std::size_t>())
        .def_readonly("first", &fwdpy11::diploid_t::first,
                      "Key to first gamete. (read-only)")
        .def_readonly("second", &fwdpy11::diploid_t::second,
                      "Key to second gamete. (read-onle)")
        .def_readonly("w", &fwdpy11::diploid_t::w, "Fitness. (read-only)")
        .def_readonly("g", &fwdpy11::diploid_t::g, "Genetic value (read-only).")
        .def_readonly("e", &fwdpy11::diploid_t::e,
                      "Random/environmental effects (read-only).")
        .def("__getstate__",
             [](const fwdpy11::diploid_t& d) {
                 return py::make_tuple(d.first, d.second, d.w, d.g, d.e);
             })
        .def("__setstate__", [](fwdpy11::diploid_t& d, py::tuple t) {
            new (&d) fwdpy11::diploid_t(t[0].cast<std::size_t>(),
                                        t[1].cast<std::size_t>());
            d.w = t[2].cast<double>();
            d.g = t[3].cast<double>();
            d.e = t[4].cast<double>();
        });

    py::bind_vector<fwdpy11::dipvector_t>(
        m, "DiploidContainer",
        "C++ representation of a list of "
        ":class:`fwdpy11.fwdpy11_types."
        "SingleLocusDiploid`.  Typically, access will be read-only.");
    py::bind_vector<std::vector<KTfwd::uint_t>>(m, "VectorUint32");
    py::bind_vector<fwdpy11::gcont_t>(m, "GameteContainer",
                                      "C++ representations of a list of "
                                      ":class:`fwdpy11.fwdpp_types.Gamete`.  "
                                      "Typically, access will be read-only.");
    py::bind_vector<fwdpy11::mcont_t>(m, "MutationContainer",
                                      "C++ representation of a list of "
                                      ":class:`fwdpy11.fwdpp_types.Mutation`.  "
                                      "Typically, access will be read-only.");

    py::class_<fwdpp_popgenmut_base>(m, "SpopMutationBase",
                                     "Base class for a single deme/single "
                                     "locus object containing "
                                     ":class:`fwdpy11.fwdpp_types.Mutation`.")
        .def_readonly("mutations", &fwdpp_popgenmut_base::mutations,R"delim(
    List of :class:`fwdpy11.fwdpp_types.Mutation`.

    .. note:: 
        This list contains **both** extinct *and* extant mutations.  
        To distinguish them, use :attr:`fwdpy11.fwdpy11_types.SpopMutationBase.mcounts`.
)delim")
        .def_readonly("mcounts", &fwdpp_popgenmut_base::mcounts, R"delim(
    List of number of occurrences of elements in 
    :attr:`fwdpy11.fwdpy11_types.SpopMutationBase.mutations`.

    The values are unsigned 32-bit integers.  

    .. note::
        Some values may be 0.  These represent *extinct* variants.  You will typically want to avoid processing such mutations.
)delim")
        .def_readonly("fixations", &fwdpp_popgenmut_base::fixations)
        .def_readonly("fixation_times", &fwdpp_popgenmut_base::fixation_times)
        .def_readonly("gametes", &fwdpp_popgenmut_base::gametes);

    py::class_<singlepop_sugar_base, fwdpp_popgenmut_base>(m, "SinglepopBase")
        .def_readonly("diploids", &singlepop_sugar_base::diploids);

    // Expose the type based on fwdpp's "sugar" layer
    py::class_<fwdpy11::singlepop_t, singlepop_sugar_base>(
        m, "Spop", "Population object representing a single deme.")
        .def(py::init<unsigned>(),
             "Construct with an unsigned integer representing the initial "
             "population size.")
        .def("clear", &fwdpy11::singlepop_t::clear,
             "Clears all population data.")
        .def_readonly("generation", &fwdpy11::singlepop_t::generation)
        .def_readonly("N", &fwdpy11::singlepop_t::N)
        .def("__getstate__",
             [](const fwdpy11::singlepop_t& pop) {
                 return py::bytes(pop.serialize());
             })
        .def("__setstate__", [](fwdpy11::singlepop_t& p, py::bytes s) {
            new (&p) fwdpy11::singlepop_t(s);
        });

    return m.ptr();
}
