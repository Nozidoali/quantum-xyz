OPENQASM 3.0;
include "stdgates.inc";
qubit[6] q3;
ry(0.4510268117962624) q3[5];
ry(0.5967431472175735) q3[4];
cx q3[5], q3[4];
ry(0.5967431472175735) q3[4];
cx q3[5], q3[4];
ry(0.9553166181245092) q3[2];
cx q3[4], q3[2];
ry(-0.9553166181245092) q3[2];
cx q3[4], q3[2];
ry(pi/4) q3[5];
cx q3[2], q3[5];
ry(-pi/4) q3[5];
cx q3[2], q3[5];
ry(pi/4) q3[3];
cx q3[4], q3[3];
ry(-pi/4) q3[3];
cx q3[4], q3[3];
cx q3[3], q3[5];
ry(0.6448807126460417) q3[2];
cx q3[4], q3[2];
ry(0.6448807126460415) q3[2];
cx q3[5], q3[2];
ry(0.6448807126460415) q3[2];
cx q3[4], q3[2];
ry(0.6448807126460415) q3[2];
cx q3[5], q3[2];
cx q3[2], q3[3];
ry(0.6389767775331606) q3[3];
cx q3[2], q3[3];
ry(-0.6389767775331606) q3[3];
cx q3[4], q3[3];
ry(-0.6389767775331606) q3[3];
cx q3[2], q3[3];
ry(0.6389767775331606) q3[3];
cx q3[4], q3[3];
negctrl @ x q3[3], q3[5];
ry(0.3161297394063069) q3[1];
cx q3[2], q3[1];
ry(-0.3161297394063069) q3[1];
cx q3[4], q3[1];
ry(-0.3161297394063068) q3[1];
cx q3[2], q3[1];
ry(0.3161297394063068) q3[1];
cx q3[3], q3[1];
ry(0.3161297394063068) q3[1];
cx q3[2], q3[1];
ry(-0.3161297394063068) q3[1];
cx q3[4], q3[1];
ry(-0.3161297394063068) q3[1];
cx q3[2], q3[1];
ry(0.3161297394063068) q3[1];
cx q3[3], q3[1];
cx q3[1], q3[4];
cx q3[1], q3[3];
cx q3[1], q3[2];
ry(1.2490457723982544) q3[5];
cx q3[1], q3[5];
ry(-1.2490457723982544) q3[5];
cx q3[1], q3[5];
ry(0.6154797086703874) q3[3];
cx q3[1], q3[3];
ry(-0.6154797086703874) q3[3];
cx q3[5], q3[3];
ry(-0.6154797086703874) q3[3];
cx q3[1], q3[3];
ry(0.6154797086703874) q3[3];
cx q3[5], q3[3];
negctrl @ x q3[3], q3[5];
ry(0.4558691454842438) q3[5];
cx q3[1], q3[5];
ry(-0.4558691454842438) q3[5];
cx q3[3], q3[5];
ry(-0.4558691454842438) q3[5];
cx q3[1], q3[5];
ry(0.4558691454842438) q3[5];
cx q3[3], q3[5];
ry(0.2767871794485226) q3[4];
cx q3[1], q3[4];
ry(-0.2767871794485226) q3[4];
cx q3[3], q3[4];
ry(-0.2767871794485226) q3[4];
cx q3[1], q3[4];
ry(0.2767871794485226) q3[4];
cx q3[5], q3[4];
ry(0.2767871794485226) q3[4];
cx q3[1], q3[4];
ry(-0.2767871794485226) q3[4];
cx q3[3], q3[4];
ry(-0.2767871794485226) q3[4];
cx q3[1], q3[4];
ry(0.2767871794485226) q3[4];
cx q3[5], q3[4];
negctrl @ x q3[4], q3[3];
ry(pi/6) q3[3];
cx q3[1], q3[3];
ry(-pi/6) q3[3];
cx q3[4], q3[3];
ry(-pi/6) q3[3];
cx q3[1], q3[3];
ry(pi/6) q3[3];
cx q3[4], q3[3];
negctrl @ x q3[3], q3[5];
ry(0.23882915453112738) q3[2];
cx q3[1], q3[2];
ry(-0.23882915453112738) q3[2];
cx q3[4], q3[2];
ry(-0.23882915453112732) q3[2];
cx q3[1], q3[2];
ry(0.23882915453112732) q3[2];
cx q3[3], q3[2];
ry(0.23882915453112732) q3[2];
cx q3[1], q3[2];
ry(-0.23882915453112732) q3[2];
cx q3[4], q3[2];
ry(-0.23882915453112732) q3[2];
cx q3[1], q3[2];
ry(0.23882915453112732) q3[2];
cx q3[3], q3[2];
ry(pi/8) q3[5];
cx q3[1], q3[5];
ry(-pi/8) q3[5];
cx q3[2], q3[5];
ry(pi/8) q3[5];
cx q3[1], q3[5];
ry(-pi/8) q3[5];
cx q3[2], q3[5];
ry(0.11941457726556369) q3[2];
cx q3[4], q3[2];
ry(-0.11941457726556369) q3[2];
cx q3[1], q3[2];
ry(0.11941457726556369) q3[2];
cx q3[4], q3[2];
ry(-0.11941457726556369) q3[2];
cx q3[3], q3[2];
ry(-0.11941457726556366) q3[2];
cx q3[4], q3[2];
ry(0.11941457726556366) q3[2];
cx q3[1], q3[2];
ry(-0.11941457726556366) q3[2];
cx q3[4], q3[2];
ry(0.11941457726556366) q3[2];
cx q3[5], q3[2];
ry(0.11941457726556366) q3[2];
cx q3[4], q3[2];
ry(-0.11941457726556366) q3[2];
cx q3[1], q3[2];
ry(0.11941457726556366) q3[2];
cx q3[4], q3[2];
ry(-0.11941457726556366) q3[2];
cx q3[3], q3[2];
ry(-0.11941457726556366) q3[2];
cx q3[4], q3[2];
ry(0.11941457726556366) q3[2];
cx q3[1], q3[2];
ry(-0.11941457726556366) q3[2];
cx q3[4], q3[2];
ry(0.11941457726556366) q3[2];
cx q3[5], q3[2];
ry(pi/16) q3[3];
cx q3[1], q3[3];
ry(-pi/16) q3[3];
cx q3[2], q3[3];
ry(pi/16) q3[3];
cx q3[1], q3[3];
ry(-pi/16) q3[3];
cx q3[4], q3[3];
ry(pi/16) q3[3];
cx q3[1], q3[3];
ry(-pi/16) q3[3];
cx q3[2], q3[3];
ry(pi/16) q3[3];
cx q3[1], q3[3];
ry(-pi/16) q3[3];
cx q3[4], q3[3];
cx q3[3], q3[4];
ry(11*pi/16) q3[0];
cx q3[1], q3[0];
ry(pi/16) q3[0];
cx q3[2], q3[0];
ry(pi/16) q3[0];
cx q3[1], q3[0];
ry(pi/16) q3[0];
cx q3[3], q3[0];
ry(pi/16) q3[0];
cx q3[1], q3[0];
ry(-pi/16) q3[0];
cx q3[2], q3[0];
ry(pi/16) q3[0];
cx q3[1], q3[0];
ry(pi/16) q3[0];
cx q3[4], q3[0];
ry(pi/16) q3[0];
cx q3[1], q3[0];
ry(-pi/16) q3[0];
cx q3[2], q3[0];
ry(-pi/16) q3[0];
cx q3[1], q3[0];
ry(-pi/16) q3[0];
cx q3[3], q3[0];
ry(pi/16) q3[0];
cx q3[1], q3[0];
ry(-pi/16) q3[0];
cx q3[2], q3[0];
ry(pi/16) q3[0];
cx q3[1], q3[0];
ry(pi/16) q3[0];
cx q3[5], q3[0];
ry(pi/16) q3[0];
cx q3[1], q3[0];
ry(-pi/16) q3[0];
cx q3[2], q3[0];
ry(-pi/16) q3[0];
cx q3[1], q3[0];
ry(-pi/16) q3[0];
cx q3[3], q3[0];
ry(-pi/16) q3[0];
cx q3[1], q3[0];
ry(5*pi/16) q3[0];
cx q3[2], q3[0];
ry(-pi/16) q3[0];
cx q3[1], q3[0];
ry(-pi/16) q3[0];
cx q3[4], q3[0];
ry(pi/16) q3[0];
cx q3[1], q3[0];
ry(-pi/16) q3[0];
cx q3[2], q3[0];
ry(-pi/16) q3[0];
cx q3[1], q3[0];
ry(-pi/16) q3[0];
cx q3[3], q3[0];
ry(pi/16) q3[0];
cx q3[1], q3[0];
ry(-pi/16) q3[0];
cx q3[2], q3[0];
ry(pi/16) q3[0];
cx q3[1], q3[0];
ry(pi/16) q3[0];
cx q3[5], q3[0];
