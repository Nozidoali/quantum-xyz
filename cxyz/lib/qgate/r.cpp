/*
 * Author: Hanyu Wang
 * Created time: 2024-04-02 09:47:09
 * Last Modified by: Hanyu Wang
 * Last Modified time: 2024-04-02 14:04:50
 */

#include "qgate.hpp"

namespace xyz
{
bool Rotation::is_trivial(double theta, bool use_x)
{
    bool is_zero = std::abs(theta) < eps || std::abs(theta - 2 * M_PI) < eps;
    bool is_pi = std::abs(theta - M_PI) < eps || std::abs(theta + M_PI) < eps;
    if (use_x)
        return is_zero || is_pi;
    return is_zero;
}
std::string Rotation::to_string() const
{
    return "R(" + std::to_string(theta) + ")";
}
} // namespace xyz