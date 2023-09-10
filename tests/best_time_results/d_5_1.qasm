OPENQASM 2.0;
include "qelib1.inc";
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
gate cry_o0(param0) q0,q1 { x q0; cry(2*pi/3) q0,q1; x q0; }
qreg q7391[5];
creg c46[5];
x q7391[3];
ry(2.214297435588181) q7391[3];
cx_oFalse q7391[3],q7391[4];
cry_o0(2*pi/3) q7391[3],q7391[2];
cx q7391[2],q7391[4];
cry(1.9106332362490186) q7391[2],q7391[1];
cx q7391[1],q7391[2];
cry(pi/2) q7391[1],q7391[0];
cx q7391[0],q7391[1];
measure q7391[0] -> c46[0];
measure q7391[1] -> c46[1];
measure q7391[2] -> c46[2];
measure q7391[3] -> c46[3];
measure q7391[4] -> c46[4];
