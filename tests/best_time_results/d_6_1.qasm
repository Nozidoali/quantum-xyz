OPENQASM 2.0;
include "qelib1.inc";
gate cry_o0(param0) q0,q1 { x q0; cry(pi/2) q0,q1; x q0; }
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
qreg q46042[6];
creg c38[6];
ry(1.9106332362490184) q46042[2];
cry(pi/3) q46042[2],q46042[3];
cry_o0(pi/2) q46042[2],q46042[4];
cx q46042[2],q46042[5];
cx_oFalse q46042[4],q46042[5];
cx q46042[3],q46042[2];
cry(1.9106332362490184) q46042[2],q46042[1];
cx q46042[1],q46042[2];
cry(pi/2) q46042[1],q46042[0];
cx q46042[0],q46042[1];
measure q46042[0] -> c38[0];
measure q46042[1] -> c38[1];
measure q46042[2] -> c38[2];
measure q46042[3] -> c38[3];
measure q46042[4] -> c38[4];
measure q46042[5] -> c38[5];
