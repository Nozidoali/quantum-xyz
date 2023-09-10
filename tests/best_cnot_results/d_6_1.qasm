OPENQASM 2.0;
include "qelib1.inc";
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
gate cry_o0(param0) q0,q1 { x q0; cry(2.214297435588181) q0,q1; x q0; }
qreg q6413[6];
creg c38[6];
x q6413[4];
ry(2.300523983021863) q6413[4];
cx_oFalse q6413[4],q6413[5];
cry_o0(2.214297435588181) q6413[4],q6413[3];
cx q6413[3],q6413[5];
cry(2*pi/3) q6413[3],q6413[2];
cx q6413[2],q6413[3];
cry(1.9106332362490184) q6413[2],q6413[1];
cx q6413[1],q6413[2];
cry(pi/2) q6413[1],q6413[0];
cx q6413[0],q6413[1];
measure q6413[0] -> c38[0];
measure q6413[1] -> c38[1];
measure q6413[2] -> c38[2];
measure q6413[3] -> c38[3];
measure q6413[4] -> c38[4];
measure q6413[5] -> c38[5];
