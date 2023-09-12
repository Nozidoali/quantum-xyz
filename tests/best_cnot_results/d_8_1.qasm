OPENQASM 2.0;
include "qelib1.inc";
gate cry_o0(param0) q0,q1 { x q0; cry(pi/2) q0,q1; x q0; }
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
qreg q42468[8];
creg c31[8];
ry(2*pi/3) q42468[4];
cry(0.8410686705679306) q42468[4],q42468[5];
cry_o0(pi/2) q42468[4],q42468[6];
cx q42468[4],q42468[7];
cx_oFalse q42468[6],q42468[7];
cx q42468[5],q42468[4];
cry(2.214297435588181) q42468[4],q42468[3];
cx q42468[3],q42468[4];
cry(2*pi/3) q42468[3],q42468[2];
cx q42468[2],q42468[3];
cry(1.9106332362490184) q42468[2],q42468[1];
cx q42468[1],q42468[2];
cry(pi/2) q42468[1],q42468[0];
cx q42468[0],q42468[1];
measure q42468[0] -> c31[0];
measure q42468[1] -> c31[1];
measure q42468[2] -> c31[2];
measure q42468[3] -> c31[3];
measure q42468[4] -> c31[4];
measure q42468[5] -> c31[5];
measure q42468[6] -> c31[6];
measure q42468[7] -> c31[7];
