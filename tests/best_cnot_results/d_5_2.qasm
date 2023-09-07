OPENQASM 2.0;
include "qelib1.inc";
qreg q1[5];
creg c1[5];
ry(1.3694384060045657) q1[2];
ry(pi/4) q1[0];
cx q1[2],q1[0];
ry(-pi/4) q1[0];
cx q1[2],q1[0];
ry(pi/8) q1[1];
cx q1[2],q1[1];
ry(-pi/8) q1[1];
cx q1[0],q1[1];
ry(pi/8) q1[1];
cx q1[2],q1[1];
ry(-pi/8) q1[1];
cx q1[0],q1[1];
ry(pi/8) q1[3];
cx q1[2],q1[3];
ry(-pi/8) q1[3];
cx q1[0],q1[3];
ry(-pi/8) q1[3];
cx q1[2],q1[3];
ry(pi/8) q1[3];
cx q1[0],q1[3];
ry(pi/4) q1[4];
cx q1[2],q1[4];
ry(-pi/4) q1[4];
cx q1[0],q1[4];
ry(pi/4) q1[4];
cx q1[2],q1[4];
ry(-pi/4) q1[4];
cx q1[0],q1[4];
ry(pi/4) q1[4];
cx q1[2],q1[4];
ry(-pi/4) q1[4];
cx q1[3],q1[4];
ry(-pi/4) q1[4];
cx q1[2],q1[4];
ry(pi/4) q1[4];
cx q1[3],q1[4];
ry(pi/4) q1[0];
cx q1[2],q1[0];
ry(-pi/4) q1[0];
cx q1[1],q1[0];
ry(pi/4) q1[0];
cx q1[2],q1[0];
ry(-pi/4) q1[0];
cx q1[1],q1[0];
ry(0.6154797086703874) q1[4];
cx q1[2],q1[4];
ry(0.6154797086703874) q1[4];
cx q1[2],q1[4];
ry(pi/8) q1[1];
cx q1[2],q1[1];
ry(pi/8) q1[1];
cx q1[4],q1[1];
ry(pi/8) q1[1];
cx q1[2],q1[1];
ry(pi/8) q1[1];
cx q1[4],q1[1];
ry(pi/4) q1[0];
cx q1[2],q1[0];
ry(pi/4) q1[0];
cx q1[4],q1[0];
ry(pi/4) q1[0];
cx q1[2],q1[0];
ry(pi/4) q1[0];
cx q1[4],q1[0];
ry(pi/4) q1[3];
cx q1[2],q1[3];
ry(pi/4) q1[3];
cx q1[2],q1[3];
ry(pi/4) q1[4];
cx q1[2],q1[4];
ry(pi/4) q1[4];
cx q1[3],q1[4];
ry(pi/4) q1[4];
cx q1[2],q1[4];
ry(pi/4) q1[4];
cx q1[3],q1[4];
ry(pi/4) q1[1];
cx q1[2],q1[1];
ry(pi/4) q1[1];
cx q1[3],q1[1];
ry(pi/4) q1[1];
cx q1[2],q1[1];
ry(pi/4) q1[1];
cx q1[3],q1[1];
ry(pi/4) q1[0];
cx q1[2],q1[0];
ry(pi/4) q1[0];
cx q1[1],q1[0];
ry(-pi/4) q1[0];
cx q1[2],q1[0];
ry(-pi/4) q1[0];
cx q1[1],q1[0];
measure q1[0] -> c1[0];
measure q1[1] -> c1[1];
measure q1[2] -> c1[2];
measure q1[3] -> c1[3];
measure q1[4] -> c1[4];
