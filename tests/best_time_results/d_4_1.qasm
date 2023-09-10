OPENQASM 2.0;
include "qelib1.inc";
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
gate cry_o0(param0) q0,q1 { x q0; cry(1.9106332362490186) q0,q1; x q0; }
qreg q1042[4];
creg c5[4];
x q1042[2];
ry(2*pi/3) q1042[2];
cx_oFalse q1042[2],q1042[3];
cry_o0(1.9106332362490186) q1042[2],q1042[1];
cx q1042[1],q1042[3];
cry(pi/2) q1042[1],q1042[0];
cx q1042[0],q1042[1];
measure q1042[0] -> c5[0];
measure q1042[1] -> c5[1];
measure q1042[2] -> c5[2];
measure q1042[3] -> c5[3];
