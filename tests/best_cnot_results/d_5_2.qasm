OPENQASM 2.0;
include "qelib1.inc";
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
gate cry_o0(param0) q0,q1 { x q0; cry(1.9106332362490186) q0,q1; x q0; }
gate cry_o0_139757518810288(param0) q0,q1 { x q0; cry(pi/2) q0,q1; x q0; }
gate cry_o0_139757518926176(param0) q0,q1 { x q0; cry(pi/2) q0,q1; x q0; }
qreg q6[5];
creg c1[5];
ry(2.498091544796509) q6[0];
cx q6[0],q6[1];
cry(1.9106332362490186) q6[1],q6[0];
cx_oFalse q6[0],q6[2];
cry_o0(1.9106332362490186) q6[2],q6[0];
cx q6[1],q6[4];
cx q6[2],q6[4];
cx q6[0],q6[1];
cry_o0_139757518810288_o0(pi/2) q6[4],q6[2];
cry_o0(1.9106332362490186) q6[4],q6[1];
cx_oFalse q6[2],q6[3];
cx q6[4],q6[3];
cx q6[1],q6[4];
cry_o0_139757518926176_o0(pi/2) q6[4],q6[0];
cx_oFalse q6[0],q6[4];
measure q6[0] -> c1[0];
measure q6[1] -> c1[1];
measure q6[2] -> c1[2];
measure q6[3] -> c1[3];
measure q6[4] -> c1[4];
