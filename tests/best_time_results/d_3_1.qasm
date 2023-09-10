OPENQASM 2.0;
include "qelib1.inc";
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
gate cry_o0(param0) q0,q1 { x q0; cry(pi/2) q0,q1; x q0; }
qreg q6203[3];
creg c35[3];
x q6203[1];
ry(1.9106332362490184) q6203[1];
cx_oFalse q6203[1],q6203[2];
cry_o0(pi/2) q6203[1],q6203[0];
cx q6203[0],q6203[2];
measure q6203[0] -> c35[0];
measure q6203[1] -> c35[1];
measure q6203[2] -> c35[2];
