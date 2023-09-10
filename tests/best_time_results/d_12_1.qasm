OPENQASM 2.0;
include "qelib1.inc";
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
gate cry_o0(param0) q0,q1 { x q0; cry(2.5290379152504543) q0,q1; x q0; }
qreg q6432[12];
creg c41[12];
x q6432[10];
ry(2.555907110132642) q6432[10];
cx_oFalse q6432[10],q6432[11];
cry_o0(2.5290379152504543) q6432[10],q6432[9];
cx q6432[9],q6432[11];
cry(2.498091544796509) q6432[9],q6432[8];
cx q6432[8],q6432[9];
cry(2.4619188346815495) q6432[8],q6432[7];
cx q6432[7],q6432[8];
cry(2.4188584057763776) q6432[7],q6432[6];
cx q6432[6],q6432[7];
cry(2.366399280279432) q6432[6],q6432[5];
cx q6432[5],q6432[6];
cry(2.300523983021863) q6432[5],q6432[4];
cx q6432[4],q6432[5];
cry(2.214297435588181) q6432[4],q6432[3];
cx q6432[3],q6432[4];
cry(2*pi/3) q6432[3],q6432[2];
cx q6432[2],q6432[3];
cry(1.9106332362490184) q6432[2],q6432[1];
cx q6432[1],q6432[2];
cry(pi/2) q6432[1],q6432[0];
cx q6432[0],q6432[1];
measure q6432[0] -> c41[0];
measure q6432[1] -> c41[1];
measure q6432[2] -> c41[2];
measure q6432[3] -> c41[3];
measure q6432[4] -> c41[4];
measure q6432[5] -> c41[5];
measure q6432[6] -> c41[6];
measure q6432[7] -> c41[7];
measure q6432[8] -> c41[8];
measure q6432[9] -> c41[9];
measure q6432[10] -> c41[10];
measure q6432[11] -> c41[11];
