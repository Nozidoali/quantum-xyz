OPENQASM 2.0;
include "qelib1.inc";
gate cry_o0(param0) q0,q1 { x q0; cry(pi/2) q0,q1; x q0; }
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
qreg q6649[4];
creg c5[4];
ry(pi/2) q6649[0];
cry(pi/2) q6649[0],q6649[1];
cry_o0(pi/2) q6649[0],q6649[2];
cx q6649[0],q6649[3];
cx_oFalse q6649[2],q6649[3];
cx q6649[1],q6649[0];
measure q6649[0] -> c5[0];
measure q6649[1] -> c5[1];
measure q6649[2] -> c5[2];
measure q6649[3] -> c5[3];
