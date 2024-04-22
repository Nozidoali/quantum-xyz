/*
 * Author: Hanyu Wang
 * Created time: 2024-03-30 17:14:20
 * Last Modified by: Hanyu Wang
 * Last Modified time: 2024-04-02 13:54:45
 */

#pragma once
#include "qstate.hpp"
#include "qgate.hpp"
#include <vector>
#include <memory>

namespace xyz
{
class QCircuit {
private:
    /* data */
    std::vector<std::shared_ptr<QGate> > pGates;
    uint32_t num_qubits = 0;
public:
    // Default constructor
    QCircuit() = default;
    QCircuit(uint32_t num_qubits) : num_qubits(num_qubits) {};
    void add_gate(std::shared_ptr<QGate> gate);
    std::string to_string() const;
};

QCircuit prepare_state(const QState& state);
} // namespace xyz


