/*
 * Author: Hanyu Wang
 * Created time: 2024-03-30 18:35:38
 * Last Modified by: Hanyu Wang
 * Last Modified time: 2024-04-02 12:30:34
 */

#include <iostream>
#include <map>
#include <cstdint>
#include <qcircuit.hpp>

using namespace xyz;
int main() {
    std::map<uint32_t, double> index_to_weight = {{0b0011, 1}, {0b0101, 1}, {0b1001, 1}, {0b0110, 1}, {0b1010, 1}, {0b1100, 1}};
    QState qstate(index_to_weight, 4);
    // std::map<uint32_t, double> index_to_weight = {{0b001, 1}, {0b010, 1}, {0b100, 1}};
    // QState qstate(index_to_weight, 3);
    // std::map<uint32_t, double> index_to_weight = {{0b00, 1}, {0b01, 1}, {0b11, 1}};
    QCircuit qcircuit = prepare_state(qstate);
    return 0;
}