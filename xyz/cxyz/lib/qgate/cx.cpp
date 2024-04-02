/*
 * Author: Hanyu Wang
 * Created time: 2024-03-30 20:13:18
 * Last Modified by: Hanyu Wang
 * Last Modified time: 2024-04-02 12:30:10
 */

#include "qstate.hpp"
#include "qgate.hpp"

#include <cmath>

namespace xyz
{
QState CX::operator()(const QState& state, const bool reverse) const
{
    (void)reverse;
    QState new_state;
    for (const auto& [index, weight] : state.index_to_weight)
    {
        uint32_t new_index = index;
        if ((bool)((index >> ctrl) & 1) == phase)
            new_index ^= (1 << target_qubit);
        new_state.index_to_weight[new_index] = weight;
    }
    new_state.n_bits = state.n_bits;
    return new_state;
}
uint32_t CX::get_cost() const
{
    return 1;
}
std::string CX::to_string() const
{
    std::string phase_str = phase? "" : "~";
    return "C(" + phase_str + std::to_string(ctrl) + ")X(" + std::to_string(target_qubit) + ")";
}
} // namespace xyz