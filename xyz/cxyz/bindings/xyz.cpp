#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <unordered_map>
#include <iostream>
#include "qcircuit.hpp"

namespace py = pybind11;

namespace xyz {

    QCircuit initialize(py::object qstate) {
        auto data_attr = qstate.attr("index_to_weight");
        // Cast the Python dict to a C++ unordered_map with int keys and double values
        std::map<uint32_t, double> index_to_weight = data_attr.cast<std::map<uint32_t, double>>();
        uint32_t num_qubits = qstate.attr("num_qubits").cast<uint32_t>();

        // Now use the map to initialize and return a QCircuit instance
        QState state(index_to_weight, num_qubits);
        return prepare_state(state);
    }
}

PYBIND11_MODULE(xyz, m) {
    py::class_<xyz::QCircuit>(m, "QCircuit")
        .def(py::init<>())
        .def(py::init<uint32_t>(), py::arg("num_qubits") = 0);

    m.def("initialize", &xyz::initialize, "Initialize a QCircuit with a given qstate.");
}
