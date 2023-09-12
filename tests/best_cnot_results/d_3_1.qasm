OPENQASM 2.0;
include "qelib1.inc";
gate cry_o0(param0) q0,q1 { x q0; cry(pi/2) q0,q1; x q0; }
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
qreg q43627[3];
creg c35[3];
ry(1.2309594173407747) q43627[2];
cry_o0(pi/2) q43627[2],q43627[0];
cx_oFalse q43627[0],q43627[1];
cx q43627[2],q43627[1];
measure q43627[0] -> c35[0];
measure q43627[1] -> c35[1];
measure q43627[2] -> c35[2];
