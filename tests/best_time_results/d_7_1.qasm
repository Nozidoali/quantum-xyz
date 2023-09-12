OPENQASM 2.0;
include "qelib1.inc";
gate cry_o0(param0) q0,q1 { x q0; cry(pi/2) q0,q1; x q0; }
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
qreg q6764[7];
creg c7[7];
ry(2.0137073708685356) q6764[3];
cry(0.9272952180016123) q6764[3],q6764[4];
cry_o0(pi/2) q6764[3],q6764[5];
cx q6764[3],q6764[6];
cx_oFalse q6764[5],q6764[6];
cx q6764[4],q6764[3];
cry(2*pi/3) q6764[3],q6764[2];
cx q6764[2],q6764[3];
cry(1.9106332362490186) q6764[2],q6764[1];
cx q6764[1],q6764[2];
cry(pi/2) q6764[1],q6764[0];
cx q6764[0],q6764[1];
measure q6764[0] -> c7[0];
measure q6764[1] -> c7[1];
measure q6764[2] -> c7[2];
measure q6764[3] -> c7[3];
measure q6764[4] -> c7[4];
measure q6764[5] -> c7[5];
measure q6764[6] -> c7[6];
