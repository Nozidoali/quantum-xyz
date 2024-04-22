/*
 * Author: Hanyu Wang
 * Created time: 2024-04-02 14:02:03
 * Last Modified by: Hanyu Wang
 * Last Modified time: 2024-04-02 14:05:55
 */

#include "qgate.hpp"

namespace xyz
{
std::string Controlled::to_string() const
{
    std::string phase_str = phase? "+" : "-";
    return "C[" + phase_str + std::to_string(ctrl) + "]";
}
} // namespace xyz