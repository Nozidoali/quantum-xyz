/*
 * Author: Hanyu Wang
 * Created time: 2024-04-02 09:30:39
 * Last Modified by: Hanyu Wang
 * Last Modified time: 2024-04-02 09:37:42
 */

#include "qgate.hpp"

namespace xyz
{
std::ostream& operator<<(std::ostream& os, const QGate& obj)
{
    os << obj.to_string();
    return os;
}
} // namespace xyz