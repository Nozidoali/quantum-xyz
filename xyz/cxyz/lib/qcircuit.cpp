/*
 * Author: Hanyu Wang
 * Created time: 2024-04-02 10:48:38
 * Last Modified by: Hanyu Wang
 * Last Modified time: 2024-04-02 10:48:45
 */

#include "qcircuit.hpp"

namespace xyz
{
void QCircuit::add_gate(std::shared_ptr<QGate> gate)
{
    pGates.push_back(gate);
}
} // namespace xyz
