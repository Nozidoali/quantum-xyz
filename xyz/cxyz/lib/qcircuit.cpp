/*
 * Author: Hanyu Wang
 * Created time: 2024-04-02 10:48:38
 * Last Modified by: Hanyu Wang
 * Last Modified time: 2024-04-02 14:17:16
 */

#include "qcircuit.hpp"

namespace xyz
{
void QCircuit::add_gate(std::shared_ptr<QGate> gate)
{
    pGates.push_back(gate);
}
std::string QCircuit::to_string() const
{
    std::string qasm = "";
    qasm += "qreg " + std::to_string(num_qubits) + "\n";
    for (const auto& pGate : pGates)
    {
        qasm += pGate->to_string() + "\n";
    }
    return qasm;
}
} // namespace xyz
