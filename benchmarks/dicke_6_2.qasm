OPENQASM 2.0;
include "qelib1.inc";
qreg q1[6];
ry(1.9106332362490184) q1[1];
ry(1.2490457723982544) q1[4];
cx q1[1],q1[4];
ry(-1.2490457723982544) q1[4];
cx q1[1],q1[4];
ry(1.2309594173407747) q1[2];
cx q1[4],q1[2];
ry(-1.2309594173407747) q1[2];
cx q1[4],q1[2];
ry(pi/4) q1[0];
cx q1[2],q1[0];
ry(-pi/4) q1[0];
cx q1[2],q1[0];
ry(1.1071487177940906) q1[0];
cx q1[1],q1[0];
ry(1.1071487177940906) q1[0];
cx q1[1],q1[0];
x q1[5];
ry(-pi/4) q1[5];
cx q1[0],q1[5];
ry(pi/4) q1[5];
cx q1[0],q1[5];
cx q1[2],q1[0];
cx q1[1],q1[5];
cx q1[0],q1[1];
cx q1[4],q1[1];
cx q1[5],q1[3];
cx q1[0],q1[5];
cx q1[2],q1[5];
ry(-pi/4) q1[4];
cx q1[2],q1[4];
ry(pi/4) q1[4];
cx q1[2],q1[4];
cx q1[4],q1[2];
ry(-pi/4) q1[1];
cx q1[0],q1[1];
ry(pi/4) q1[1];
cx q1[0],q1[1];
cx q1[1],q1[0];