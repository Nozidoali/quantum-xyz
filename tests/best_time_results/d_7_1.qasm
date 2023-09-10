OPENQASM 2.0;
include "qelib1.inc";
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
gate cry_o0(param0) q0,q1 { x q0; cry(2.300523983021863) q0,q1; x q0; }
qreg q1055[7];
creg c7[7];
x q1055[5];
ry(2.366399280279432) q1055[5];
cx_oFalse q1055[5],q1055[6];
cry_o0(2.300523983021863) q1055[5],q1055[4];
cx q1055[4],q1055[6];
cry(2.214297435588181) q1055[4],q1055[3];
cx q1055[3],q1055[4];
cry(2*pi/3) q1055[3],q1055[2];
cx q1055[2],q1055[3];
cry(1.9106332362490186) q1055[2],q1055[1];
cx q1055[1],q1055[2];
cry(pi/2) q1055[1],q1055[0];
cx q1055[0],q1055[1];
measure q1055[0] -> c7[0];
measure q1055[1] -> c7[1];
measure q1055[2] -> c7[2];
measure q1055[3] -> c7[3];
measure q1055[4] -> c7[4];
measure q1055[5] -> c7[5];
measure q1055[6] -> c7[6];
