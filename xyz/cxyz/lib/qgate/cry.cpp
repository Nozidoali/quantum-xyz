/*
 * Author: Hanyu Wang
 * Created time: 2024-03-31 14:45:41
 * Last Modified by: Hanyu Wang
 * Last Modified time: 2024-04-02 14:08:42
 */

#include "qstate.hpp"
#include "qgate.hpp"

#include <cmath>

namespace xyz
{
QState CRY::operator()(const QState& state, const bool reverse) const
{
    auto _theta = reverse? -theta : theta;
    QState new_state;
    for (const auto& [index, weight] : state.index_to_weight)
    {
        if ((bool)((index >> ctrl) & 1) != phase)
        {
            new_state.index_to_weight[index] = weight;
            continue;
        }
        if (new_state.index_to_weight.find(index) == new_state.index_to_weight.end())
            new_state.index_to_weight[index] = 0;
        new_state.index_to_weight[index] += std::cos(_theta / 2) * weight;
        uint32_t new_index = index ^ (1 << target_qubit);
        new_state.index_to_weight[new_index] += std::sin(_theta / 2) *
        ((index & (1 << target_qubit))? -weight : weight);
    }
    for (auto it = new_state.index_to_weight.begin(); it != new_state.index_to_weight.end();)
    {
        if (std::abs(it->second) < QState::eps)
            it = new_state.index_to_weight.erase(it);
        else
            ++it;
    }
    new_state.n_bits = state.n_bits;
    return new_state;
}
uint32_t CRY::get_cost() const
{
    return 2;
}
std::string CRY::to_string() const
{
    std::string ctrl_str = Controlled::to_string();
    std::string ry_str = RY::to_string();
    return ctrl_str + ry_str;
}
} // namespace xyz