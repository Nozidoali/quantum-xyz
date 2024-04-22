/*
 * Author: Hanyu Wang
 * Created time: 2024-03-30 18:18:02
 * Last Modified by: Hanyu Wang
 * Last Modified time: 2024-04-02 14:32:55
 */

#include "qcircuit.hpp"
#include <queue>
#include <vector>
#include <optional>
#include <memory>
#include <iostream>
#include <unordered_map>
#include <unordered_set>

namespace xyz
{
namespace detail
{
struct bfs_state
{
    uint32_t mem_idx;
    uint32_t cnot_cost;
    bool operator < (const bfs_state& other) const
    {
        // TODO: A* search
        return cnot_cost > other.cnot_cost;
    }
    bfs_state(uint32_t mem_idx, uint32_t cnot_cost) : mem_idx(mem_idx), cnot_cost(cnot_cost) {};
};

struct memorized_state
{
    uint32_t prev;
    QState state;
    std::shared_ptr<QGate> pGate = nullptr;
    memorized_state(const QState& state, uint32_t prev) : state(state), prev(prev) {};
    memorized_state(const QState& state, uint32_t prev, std::shared_ptr<QGate> pGate) : state(state), prev(prev), pGate(pGate) {};
};

std::vector<std::shared_ptr<QGate>> enumerate_gates(const QState& state)
{
    std::vector<std::shared_ptr<QGate>> gates;
    if (state.index_to_weight.size() == 1)
    {
        auto index = state.index_to_weight.begin()->first;
        for (uint32_t target = 0; target < state.n_bits; target++)
        {
            if ((index >> target) & 1)
            {
                gates.push_back(std::make_shared<X>(target));
                return gates;
            }
        }
    }
    for (uint32_t target = 0; target < state.n_bits; target++)
    {
        const auto ry_table = state.to_ry_table(target);
        std::optional<double> theta;
        for (const auto& [index, _theta] : ry_table)
        {
            if (theta.has_value() && theta.value() != _theta)
            {
                theta.reset();
                break;
            }
            theta = _theta;
        }
        if (theta.has_value() && !Rotation::is_trivial(theta.value(), true))
        {
            gates.push_back(std::make_shared<RY>(target, theta.value()));
            return gates;
        }
    }
    for (uint32_t target = 0; target < state.n_bits; target++)
    {
        const auto ry_table = state.to_ry_table(target);
        for (uint32_t ctrl = 0; ctrl < state.n_bits; ctrl++)
            for (bool phase : {false, true})
            {
                if (ctrl == target) continue;
                std::optional<double> theta = std::nullopt;
                for (const auto& [index, _theta] : ry_table)
                {
                    if ((bool)((index >> ctrl) & 1) == phase)
                    {
                        if (theta.has_value() && theta.value() != _theta)
                        {
                            theta.reset();
                            break;
                        }
                        theta = _theta;
                    }
                }
                if (theta.has_value() && !Rotation::is_trivial(theta.value(), true))
                {
                    gates.push_back(std::make_shared<CRY>(ctrl, phase, theta.value(), target));
                    gates.push_back(std::make_shared<CRY>(ctrl, phase,  - M_PI + theta.value(), target));
                }
            }
    }
    for (uint32_t target = 0; target < state.n_bits; target++)
        for (uint32_t ctrl = 0; ctrl < state.n_bits; ctrl++)
        {
            if (ctrl == target) continue;
            gates.push_back(std::make_shared<CX>(ctrl, true, target));
        }
    return gates;
}
// Helper functions
template <bool verbose>
void prepare_state_impl(const QState& state, QCircuit& circuit)
{
    std::priority_queue<bfs_state> q;
    std::vector<memorized_state> states;
    std::unordered_map<uint64_t, uint32_t> state_to_cost;
    std::unordered_set<uint64_t> visited;
    states.push_back(memorized_state(state, -1));
    q.push(bfs_state(0, 0));
    state_to_cost[state.repr()] = 0;
    std::optional<uint32_t> solution = std::nullopt;
    while (!q.empty())
    {
        auto e = q.top(); q.pop();
        auto current_state = states[e.mem_idx];
        if (visited.find(current_state.state.repr()) != visited.end())
            continue;
        visited.insert(current_state.state.repr());
        if (current_state.state.is_ground())
        {
            solution = e.mem_idx;
            break;
        }
        if constexpr (verbose)
            std::cout << "current_state: " << current_state.state << " repr = " << current_state.state.repr() << std::endl;
        for (const auto& gate : enumerate_gates(current_state.state))
        {
            if constexpr (verbose)
                std::cout << "gate: " << *gate << std::endl;
            auto new_state = (*gate)(current_state.state, true);
            auto new_cost = e.cnot_cost + gate->get_cost();
            auto new_repr = new_state.repr();
            if (visited.find(new_repr) != visited.end())
                continue;
            if (state_to_cost.find(new_repr) == state_to_cost.end() || state_to_cost[new_repr] > e.cnot_cost + 1)
            {
                if constexpr (verbose)
                    std::cout << "\tadd: " << *gate << " -> " << new_state << std::endl;
                state_to_cost[new_repr] = new_cost;
                q.push(bfs_state(states.size(), new_cost));
                states.push_back(memorized_state(new_state, e.mem_idx, gate));
            }
        }
    }
    if (!solution.has_value())
    {
        std::cerr << "No solution found!" << std::endl;
        return;
    }
    // back trace
    for (uint32_t idx = solution.value(); idx != 0; idx = states[idx].prev)
    {
        if constexpr (verbose)
            std::cout << "gate: " << *states[idx].pGate << " -> " << states[idx].state << std::endl;
        circuit.add_gate(states[idx].pGate);
    }
}
} // namespace detail

QCircuit prepare_state(const QState& state)
{
    QCircuit circuit(state.n_bits);
    detail::prepare_state_impl<false>(state, circuit);
    return circuit;
}
} // namespace xyz