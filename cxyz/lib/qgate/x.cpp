/*
 * Author: Hanyu Wang
 * Created time: 2024-03-31 14:45:41
 * Last Modified by: Hanyu Wang
 * Last Modified time: 2024-04-02 09:39:46
 */

#include "qstate.hpp"
#include "qgate.hpp"

#include <cmath>

namespace xyz
{
QState X::operator()(const QState& state, const bool reverse) const
{
    (void)reverse;
    QState new_state;
    for (const auto& [index, weight] : state.index_to_weight)
    {
        uint32_t new_index = index ^ (1 << target_qubit);
        new_state.index_to_weight[new_index] = weight;
    }
    new_state.n_bits = state.n_bits;
    return new_state;
}
std::string X::to_string() const
{
    return "X(" + std::to_string(target_qubit) + ")";
}
uint32_t X::get_cost() const
{
    return 0;
}
} // namespace xyz