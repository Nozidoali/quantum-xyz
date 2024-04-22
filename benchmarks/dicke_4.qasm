OPENQASM 3.0;
include "stdgates.inc";
gate cx c, t {
  ctrl @ U(pi, 0, pi) c, t;
}
qubit[4] q1;
ry(1.2309594173407747) q1[1];
ry(pi/4) q1[3];
cx q1[1], q1[3];
ry(pi/4) q1[3];
cx q1[1], q1[3];
ry(pi/2) q1[2];
cx_oFalse_140400673275536 q1[2], q1[1];
cx_oFalse q1[1], q1[3];
ry(5*pi/8) q1[0];
cx q1[1], q1[0];
ry(pi/8) q1[0];
cx q1[2], q1[0];
ry(pi/8) q1[0];
cx q1[1], q1[0];
ry(pi/8) q1[0];
cx q1[3], q1[0];
ry(pi/8) q1[0];
cx q1[1], q1[0];
ry(-3*pi/8) q1[0];
cx q1[2], q1[0];
ry(pi/8) q1[0];
cx q1[1], q1[0];
ry(pi/8) q1[0];
cx q1[3], q1[0];
