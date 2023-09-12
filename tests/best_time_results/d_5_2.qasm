OPENQASM 2.0;
include "qelib1.inc";
gate cry_o0(param0) q0,q1 { x q0; cry(1.9106332362490186) q0,q1; x q0; }
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
gate ccry(param0) q0,q1,q2 { ry(1.1071487177940904) q2; ccx q0,q1,q2; ry(-1.1071487177940904) q2; ccx q0,q1,q2; }
gate ccry_o0(param0) q0,q1,q2 { x q0; x q1; ccry(2.214297435588181) q0,q1,q2; x q0; x q1; }
gate ccry_139651742164176(param0) q0,q1,q2 { ry(0.9553166181245093) q2; ccx q0,q1,q2; ry(-0.9553166181245093) q2; ccx q0,q1,q2; }
gate ccry_o1(param0) q0,q1,q2 { x q1; ccry_139651742164176(1.9106332362490186) q0,q1,q2; x q1; }
gate ccry_139651656044688(param0) q0,q1,q2 { ry(pi/4) q2; ccx q0,q1,q2; ry(-pi/4) q2; ccx q0,q1,q2; }
qreg q33[5];
creg c1[5];
ry(1.9823131728623844) q33[3];
cry_o0(1.9106332362490186) q33[3],q33[2];
cry(1.1278852827212578) q33[3],q33[2];
cry(pi/2) q33[2],q33[1];
cx_oFalse q33[3],q33[1];
x q33[4];
ccry_o0(2.214297435588181) q33[2],q33[1],q33[0];
cx q33[0],q33[4];
cx_oFalse q33[0],q33[4];
cry(2*pi/3) q33[0],q33[3];
cx_oFalse q33[3],q33[4];
ccry_o1(1.9106332362490186) q33[0],q33[3],q33[2];
cx q33[2],q33[4];
ccry_139651656044688(pi/2) q33[0],q33[2],q33[1];
cx q33[1],q33[2];
measure q33[0] -> c1[0];
measure q33[1] -> c1[1];
measure q33[2] -> c1[2];
measure q33[3] -> c1[3];
measure q33[4] -> c1[4];
