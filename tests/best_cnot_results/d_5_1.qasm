OPENQASM 2.0;
include "qelib1.inc";
gate cry_o0(param0) q0,q1 { x q0; cry(pi/2) q0,q1; x q0; }
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
qreg q52766[5];
creg c46[5];
ry(1.7721542475852274) q52766[1];
cry(1.2309594173407747) q52766[1],q52766[2];
cry_o0(pi/2) q52766[1],q52766[3];
cx q52766[1],q52766[4];
cx_oFalse q52766[3],q52766[4];
cx q52766[2],q52766[1];
cry(pi/2) q52766[1],q52766[0];
cx q52766[0],q52766[1];
measure q52766[0] -> c46[0];
measure q52766[1] -> c46[1];
measure q52766[2] -> c46[2];
measure q52766[3] -> c46[3];
measure q52766[4] -> c46[4];
