/*
 * Author: Hanyu Wang
 * Created time: 2024-04-02 11:16:31
 * Last Modified by: Hanyu Wang
 * Last Modified time: 2024-04-02 11:40:04
 */

#include <gtest/gtest.h>
#include "qgate.hpp"

using namespace xyz;

TEST(QGateTest, ApplyCRy1)
{
    std::map<uint32_t, double> index_to_weight = {{0b001, 1}, {0b011, 1}, {0b000, 1}};
    QState state(index_to_weight, 3);
    CRY gate(1, 0, M_PI / 2, 0);
    QState new_state = gate(state);
    EXPECT_LT(std::abs(new_state.index_to_weight[0b011] - 1), QState::eps);
    EXPECT_LT(std::abs(new_state.index_to_weight[0b001] - sqrt(2)), QState::eps);
    EXPECT_EQ(new_state.index_to_weight.find(0b000), new_state.index_to_weight.end());
}

TEST(QGateTest, ApplyCRy2)
{
    std::map<uint32_t, double> index_to_weight = {{0b001, 1}, {0b011, 1}, {0b000, 2}};
    QState state(index_to_weight, 3);
    CRY gate1(1, 0, - 2 * atan2(1, 2), 0);
    QState new_state = gate1(state);
    EXPECT_LT(std::abs(new_state.index_to_weight[0b011] - 1), QState::eps);
    EXPECT_LT(std::abs(new_state.index_to_weight[0b000] - sqrt(5)), QState::eps);
    EXPECT_EQ(new_state.index_to_weight.find(0b001), new_state.index_to_weight.end());
    CRY gate2(1, 0, - 2 * atan2(1, 2) + M_PI, 0);
    new_state = gate2(state);
    EXPECT_LT(std::abs(new_state.index_to_weight[0b011] - 1), QState::eps);
    EXPECT_LT(std::abs(new_state.index_to_weight[0b001] - sqrt(5)), QState::eps);
    EXPECT_EQ(new_state.index_to_weight.find(0b000), new_state.index_to_weight.end());
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}