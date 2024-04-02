/*
 * Author: Hanyu Wang
 * Created time: 2024-03-30 19:27:46
 * Last Modified by: Hanyu Wang
 * Last Modified time: 2024-04-02 09:52:06
 */

#pragma once

#include "qstate.hpp"
#include <cstdint>
#include <vector>
#include <iostream>
#include <cmath>

namespace xyz
{
class QGate
{
private:
public:
    /* data */
    uint32_t target_qubit;
    QGate() = default;
    QGate(uint32_t target_qubit) : target_qubit(target_qubit) {};
    virtual QState operator()(const QState& state, const bool reverse = false) const = 0;
    virtual uint32_t get_cost() const = 0;
    virtual std::string to_string() const = 0;
    friend std::ostream& operator<<(std::ostream& os, const QGate& obj);
};

class Rotation
{
public:
    /* data */
    static constexpr double eps = 1e-6;
    static bool is_trivial(double theta, bool use_x = false);
    double theta;
    Rotation(double theta) : theta(theta) {};
};

class RY : public QGate, public Rotation
{
private:
public:
    /* data */
    RY(uint32_t target_qubit, double theta) : Rotation(theta), QGate(target_qubit) {};
    QState operator()(const QState& state, const bool reverse = false) const;
    uint32_t get_cost() const;
    std::string to_string() const;
};

class Controlled
{
private:
public:
    /* data */
    uint32_t ctrl;
    bool phase;
    Controlled(uint32_t ctrl, bool phase) : ctrl(ctrl), phase(phase) {};
};

class MultiControlled
{
private:
    /* data */
public:
    std::vector<uint32_t> ctrls;
    std::vector<bool> phases;
    MultiControlled(std::vector<uint32_t> ctrls) : ctrls(ctrls) {};
};

class CRY : public Controlled, public RY
{
private:
public:
    /* data */
    CRY(uint32_t ctrl, bool phase, double theta, uint32_t target_qubit) : Controlled(ctrl, phase), RY(target_qubit, theta) {};
    QState operator()(const QState& state, const bool reverse = false) const;
    std::string to_string() const;
    uint32_t get_cost() const;
};

class MCRY : public MultiControlled, public RY
{
private:
    /* data */
public:
    MCRY(std::vector<uint32_t> ctrls, double theta, uint32_t target_qubit) : MultiControlled(ctrls), RY(target_qubit, theta) {};
};

class X : public QGate
{
private:
    /* data */
public:
    using QGate::QGate;
    QState operator()(const QState& state, const bool reverse = false) const;
    uint32_t get_cost() const;
    std::string to_string() const;
};

class CX : public Controlled, public X
{
private:
    /* data */
public:
    CX(uint32_t ctrl, bool phase, uint32_t target_qubit) : Controlled(ctrl, phase), X(target_qubit) {};
    QState operator()(const QState& state, const bool reverse = false) const;
    std::string to_string() const;
    uint32_t get_cost() const;
};

} // namespace xyz