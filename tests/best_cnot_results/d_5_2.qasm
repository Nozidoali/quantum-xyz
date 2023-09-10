OPENQASM 2.0;
include "qelib1.inc";
gate cry_o0(param0) q0,q1 { x q0; cry(2.4619188346815495) q0,q1; x q0; }
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
gate cry_o0_140121055254592(param0) q0,q1 { x q0; cry(2.4188584057763776) q0,q1; x q0; }
gate ccry(param0) q0,q1,q2 { ry(1.183199640139716) q2; ccx q0,q1,q2; ry(-1.183199640139716) q2; ccx q0,q1,q2; }
gate ccry_o0(param0) q0,q1,q2 { x q0; x q1; ccry(2.366399280279432) q0,q1,q2; x q0; x q1; }
gate cry_o0_140121055250368(param0) q0,q1 { x q0; cry(2.300523983021863) q0,q1; x q0; }
gate ccry_140121046642032(param0) q0,q1,q2 { ry(1.1071487177940904) q2; ccx q0,q1,q2; ry(-1.1071487177940904) q2; ccx q0,q1,q2; }
gate ccry_o0_140121046020304(param0) q0,q1,q2 { x q0; x q1; ccry_140121046642032(2.214297435588181) q0,q1,q2; x q0; x q1; }
gate ccry_140121046643280(param0) q0,q1,q2 { ry(0.9553166181245093) q2; ccx q0,q1,q2; ry(-0.9553166181245093) q2; ccx q0,q1,q2; }
gate ccry_o1(param0) q0,q1,q2 { x q1; ccry_140121046643280(1.9106332362490186) q0,q1,q2; x q1; }
gate ccry_140121054820240(param0) q0,q1,q2 { ry(pi/4) q2; ccx q0,q1,q2; ry(-pi/4) q2; ccx q0,q1,q2; }
qreg q6[5];
creg c1[5];
x q6[1];
x q6[2];
x q6[3];
x q6[4];
ry(2.498091544796509) q6[3];
cry_o0(2.4619188346815495) q6[3],q6[1];
cx_oFalse q6[1],q6[3];
cry_o0_140121055254592_o0(2.4188584057763776) q6[1],q6[3];
ccry_o0(2.366399280279432) q6[1],q6[3],q6[2];
cx_oFalse q6[2],q6[1];
cry_o0_140121055250368_o0(2.300523983021863) q6[2],q6[1];
cx_oFalse q6[1],q6[3];
ccry_o0_140121046020304_o0(2.214297435588181) q6[2],q6[1],q6[0];
cx q6[0],q6[4];
cry(2*pi/3) q6[0],q6[3];
cx_oFalse q6[3],q6[4];
ccry_o1(1.9106332362490186) q6[0],q6[3],q6[2];
cx q6[2],q6[4];
ccry_140121054820240(pi/2) q6[0],q6[2],q6[1];
cx q6[1],q6[2];
measure q6[0] -> c1[0];
measure q6[1] -> c1[1];
measure q6[2] -> c1[2];
measure q6[3] -> c1[3];
measure q6[4] -> c1[4];
