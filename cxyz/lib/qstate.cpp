#include "qstate.hpp"
#include <cmath>

namespace xyz
{
bool QState::is_ground() const
{
    return index_to_weight.size() == 1 && index_to_weight.find(0) != index_to_weight.end();
}
std::ostream& operator<<(std::ostream& os, const QState& obj)
{
    for (auto it = obj.index_to_weight.begin(); it != obj.index_to_weight.end(); it++)
    {
        auto index = it->first;
        auto weight = it->second;
        os << weight << "*|";
        for (uint32_t i = 0; i < obj.n_bits; i++)
            os << ((index >> i) & 1);
        os << ">";
        if (std::next(it) != obj.index_to_weight.end())
            os << " + ";
    }
    return os;
}
std::unordered_map<uint32_t, double> QState::to_ry_table(uint32_t target) const
{
    std::unordered_map<uint32_t, double> ry_table;
    for (const auto& [index, weight] : index_to_weight)
    {
        auto index_0 = index & (~(1 << target));
        auto index_1 = index | (1 << target);

        if (ry_table.find(index_0) != ry_table.end())
            continue;
        if (index_to_weight.find(index_0) == index_to_weight.end())
            ry_table[index_0] = M_PI;
        else if (index_to_weight.find(index_1) == index_to_weight.end())
            ry_table[index_0] = 0;
        else
            ry_table[index_0] = 2 * atan2(index_to_weight.at(index_1), index_to_weight.at(index_0));
    }
    return ry_table;
}
uint64_t QState::repr() const
{
    if (hash_value.has_value())
        return hash_value.value();
    uint64_t hash = 0;
    for (auto it = index_to_weight.end(); it != index_to_weight.begin();)
    {
        it--;
        hash = (hash << n_bits) ^ it->first;
    }
    return hash;
}
} // namespace xyz