OPENQASM 2.0;
include "qelib1.inc";
gate cry_o0(param0) q0,q1 { x q0; cry(pi/2) q0,q1; x q0; }
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
qreg q46279[12];
creg c41[12];
ry(2.300523983021863) q46279[8];
cry(0.6435011087932846) q46279[8],q46279[9];
cry_o0(pi/2) q46279[8],q46279[10];
cx q46279[8],q46279[11];
cx_oFalse q46279[10],q46279[11];
cx q46279[9],q46279[8];
cry(2.4619188346815495) q46279[8],q46279[7];
cx q46279[7],q46279[8];
cry(2.4188584057763776) q46279[7],q46279[6];
cx q46279[6],q46279[7];
cry(2.366399280279432) q46279[6],q46279[5];
cx q46279[5],q46279[6];
cry(2.300523983021863) q46279[5],q46279[4];
cx q46279[4],q46279[5];
cry(2.214297435588181) q46279[4],q46279[3];
cx q46279[3],q46279[4];
cry(2*pi/3) q46279[3],q46279[2];
cx q46279[2],q46279[3];
cry(1.9106332362490184) q46279[2],q46279[1];
cx q46279[1],q46279[2];
cry(pi/2) q46279[1],q46279[0];
cx q46279[0],q46279[1];
measure q46279[0] -> c41[0];
measure q46279[1] -> c41[1];
measure q46279[2] -> c41[2];
measure q46279[3] -> c41[3];
measure q46279[4] -> c41[4];
measure q46279[5] -> c41[5];
measure q46279[6] -> c41[6];
measure q46279[7] -> c41[7];
measure q46279[8] -> c41[8];
measure q46279[9] -> c41[9];
measure q46279[10] -> c41[10];
measure q46279[11] -> c41[11];
