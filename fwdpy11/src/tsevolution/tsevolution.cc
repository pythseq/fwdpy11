#include <pybind11/pybind11.h>

namespace py = pybind11;

void init_slocus_evolution(py::module &);

PYBIND11_MODULE(_tsevolution, m)
{
    m.doc() = "Evolution under a Wright-Fisher model using tree sequences.";

    init_slocus_evolution(m);
}

