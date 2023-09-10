OPENQASM 2.0;
include "qelib1.inc";
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
gate cry_o0(param0) q0,q1 { x q0; cry(2.4188584057763776) q0,q1; x q0; }
qreg q0[9];
creg c0[9];
x q0[7];
ry(2.4619188346815495) q0[7];
cx_oFalse q0[7],q0[8];
cry_o0(2.4188584057763776) q0[7],q0[6];
cx q0[6],q0[8];
cry(2.366399280279432) q0[6],q0[5];
cx q0[5],q0[6];
cry(2.300523983021863) q0[5],q0[4];
cx q0[4],q0[5];
cry(2.214297435588181) q0[4],q0[3];
cx q0[3],q0[4];
cry(2*pi/3) q0[3],q0[2];
cx q0[2],q0[3];
cry(1.9106332362490186) q0[2],q0[1];
cx q0[1],q0[2];
cry(pi/2) q0[1],q0[0];
cx q0[0],q0[1];
measure q0[0] -> c0[0];
measure q0[1] -> c0[1];
measure q0[2] -> c0[2];
measure q0[3] -> c0[3];
measure q0[4] -> c0[4];
measure q0[5] -> c0[5];
measure q0[6] -> c0[6];
measure q0[7] -> c0[7];
measure q0[8] -> c0[8];
