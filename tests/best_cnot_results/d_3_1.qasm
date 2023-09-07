OPENQASM 2.0;
include "qelib1.inc";
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
qreg q10[3];
creg c10[3];
ry(1.2309594173407747) q10[2];
ry(pi/4) q10[0];
cx q10[2],q10[0];
ry(pi/4) q10[0];
cx q10[2],q10[0];
cx_oFalse q10[0],q10[1];
cx q10[2],q10[1];
measure q10[0] -> c10[0];
measure q10[1] -> c10[1];
measure q10[2] -> c10[2];
