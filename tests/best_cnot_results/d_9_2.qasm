OPENQASM 2.0;
include "qelib1.inc";
gate cry_o0(param0) q0,q1 { x q0; cry(2.801900077422446) q0,q1; x q0; }
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
gate cry_o0_140121008019376(param0) q0,q1 { x q0; cry(2.796891473791147) q0,q1; x q0; }
gate ccry(param0) q0,q1,q2 { ry(1.3958272811292078) q2; ccx q0,q1,q2; ry(-1.3958272811292078) q2; ccx q0,q1,q2; }
gate ccry_o0(param0) q0,q1,q2 { x q0; x q1; ccry(2.7916545622584157) q0,q1,q2; x q0; x q1; }
gate cry_o0_140121008017216(param0) q0,q1 { x q0; cry(2.7861714518995697) q0,q1; x q0; }
gate ccry_140121044035872(param0) q0,q1,q2 { ry(1.3902111126041985) q2; ccx q0,q1,q2; ry(-1.3902111126041985) q2; ccx q0,q1,q2; }
gate ccry_o0_140121008023936(param0) q0,q1,q2 { x q0; x q1; ccry_140121044035872(2.780422225208397) q0,q1,q2; x q0; x q1; }
gate ccry_140121043729520(param0) q0,q1,q2 { ry(1.384016865713303) q2; ccx q0,q1,q2; ry(-1.384016865713303) q2; ccx q0,q1,q2; }
gate ccry_o1(param0) q0,q1,q2 { x q1; ccry_140121043729520(2.768033731426606) q0,q1,q2; x q1; }
gate ccry_140121044026752(param0) q0,q1,q2 { ry(1.38067072344843) q2; ccx q0,q1,q2; ry(-1.38067072344843) q2; ccx q0,q1,q2; }
gate ccry_o1_140121008025952(param0) q0,q1,q2 { x q1; ccry_140121044026752(2.76134144689686) q0,q1,q2; x q1; }
gate ccry_140121044034192(param0) q0,q1,q2 { ry(1.37713802635057) q2; ccx q0,q1,q2; ry(-1.37713802635057) q2; ccx q0,q1,q2; }
gate ccry_o1_140121008129168(param0) q0,q1,q2 { x q1; ccry_140121044034192(2.75427605270114) q0,q1,q2; x q1; }
gate ccry_140121044039712(param0) q0,q1,q2 { ry(1.369438406004566) q2; ccx q0,q1,q2; ry(-1.369438406004566) q2; ccx q0,q1,q2; }
gate ccry_o1_140121008133248(param0) q0,q1,q2 { x q1; ccry_140121044039712(2.738876812009132) q0,q1,q2; x q1; }
gate ccry_140121044034624(param0) q0,q1,q2 { ry(1.3652273956337229) q2; ccx q0,q1,q2; ry(-1.3652273956337229) q2; ccx q0,q1,q2; }
gate ccry_o1_140121008142224(param0) q0,q1,q2 { x q1; ccry_140121044034624(2.7304547912674457) q0,q1,q2; x q1; }
gate ccry_140121044030400(param0) q0,q1,q2 { ry(1.3607405877236578) q2; ccx q0,q1,q2; ry(-1.3607405877236578) q2; ccx q0,q1,q2; }
gate ccry_o1_140121008138384(param0) q0,q1,q2 { x q1; ccry_140121044030400(2.7214811754473156) q0,q1,q2; x q1; }
gate ccry_140121044030304(param0) q0,q1,q2 { ry(1.3559464937191843) q2; ccx q0,q1,q2; ry(-1.3559464937191843) q2; ccx q0,q1,q2; }
gate ccry_o1_140121043849936(param0) q0,q1,q2 { x q1; ccry_140121044030304(2.7118929874383686) q0,q1,q2; x q1; }
gate ccry_140121044035104(param0) q0,q1,q2 { ry(1.3452829208967654) q2; ccx q0,q1,q2; ry(-1.3452829208967654) q2; ccx q0,q1,q2; }
gate ccry_o1_140121043857040(param0) q0,q1,q2 { x q1; ccry_140121044035104(2.6905658417935308) q0,q1,q2; x q1; }
gate ccry_140121043845328(param0) q0,q1,q2 { ry(1.3393189628247184) q2; ccx q0,q1,q2; ry(-1.3393189628247184) q2; ccx q0,q1,q2; }
gate ccry_o1_140121043857424(param0) q0,q1,q2 { x q1; ccry_140121043845328(2.678637925649437) q0,q1,q2; x q1; }
gate ccry_140121008136800(param0) q0,q1,q2 { ry(1.3328552019646884) q2; ccx q0,q1,q2; ry(-1.3328552019646884) q2; ccx q0,q1,q2; }
gate ccry_o1_140121043846960(param0) q0,q1,q2 { x q1; ccry_140121008136800(2.665710403929377) q0,q1,q2; x q1; }
gate ccry_140121044026608(param0) q0,q1,q2 { ry(1.3258176636680326) q2; ccx q0,q1,q2; ry(-1.3258176636680326) q2; ccx q0,q1,q2; }
gate ccry_o1_140121043853104(param0) q0,q1,q2 { x q1; ccry_140121044026608(2.651635327336065) q0,q1,q2; x q1; }
gate ccry_140121044040480(param0) q0,q1,q2 { ry(1.318116071652818) q2; ccx q0,q1,q2; ry(-1.318116071652818) q2; ccx q0,q1,q2; }
gate ccry_o1_140121043856896(param0) q0,q1,q2 { x q1; ccry_140121044040480(2.636232143305636) q0,q1,q2; x q1; }
gate ccry_140121037889952(param0) q0,q1,q2 { ry(1.3002465638163239) q2; ccx q0,q1,q2; ry(-1.3002465638163239) q2; ccx q0,q1,q2; }
gate ccry_o1_140121043854880(param0) q0,q1,q2 { x q1; ccry_140121037889952(2.6004931276326477) q0,q1,q2; x q1; }
gate ccry_140121037881984(param0) q0,q1,q2 { ry(1.289761425292083) q2; ccx q0,q1,q2; ry(-1.289761425292083) q2; ccx q0,q1,q2; }
gate ccry_o1_140121043858720(param0) q0,q1,q2 { x q1; ccry_140121037881984(2.579522850584166) q0,q1,q2; x q1; }
gate ccry_140121037890384(param0) q0,q1,q2 { ry(1.2779535550663212) q2; ccx q0,q1,q2; ry(-1.2779535550663212) q2; ccx q0,q1,q2; }
gate ccry_o1_140121043851664(param0) q0,q1,q2 { x q1; ccry_140121037890384(2.5559071101326425) q0,q1,q2; x q1; }
gate ccry_140121037896624(param0) q0,q1,q2 { ry(1.2645189576252271) q2; ccx q0,q1,q2; ry(-1.2645189576252271) q2; ccx q0,q1,q2; }
gate ccry_o1_140121043858768(param0) q0,q1,q2 { x q1; ccry_140121037896624(2.5290379152504543) q0,q1,q2; x q1; }
gate ccry_140121037882080(param0) q0,q1,q2 { ry(1.2490457723982544) q2; ccx q0,q1,q2; ry(-1.2490457723982544) q2; ccx q0,q1,q2; }
gate ccry_o1_140121043856464(param0) q0,q1,q2 { x q1; ccry_140121037882080(2.498091544796509) q0,q1,q2; x q1; }
gate ccry_140121037893216(param0) q0,q1,q2 { ry(1.2309594173407747) q2; ccx q0,q1,q2; ry(-1.2309594173407747) q2; ccx q0,q1,q2; }
gate ccry_o1_140121043718912(param0) q0,q1,q2 { x q1; ccry_140121037893216(2.4619188346815495) q0,q1,q2; x q1; }
gate ccry_140121008130560(param0) q0,q1,q2 { ry(1.183199640139716) q2; ccx q0,q1,q2; ry(-1.183199640139716) q2; ccx q0,q1,q2; }
gate ccry_o1_140121043728848(param0) q0,q1,q2 { x q1; ccry_140121008130560(2.366399280279432) q0,q1,q2; x q1; }
gate ccry_140121043725104(param0) q0,q1,q2 { ry(1.1502619915109316) q2; ccx q0,q1,q2; ry(-1.1502619915109316) q2; ccx q0,q1,q2; }
gate ccry_140121043718240(param0) q0,q1,q2 { ry(1.1071487177940904) q2; ccx q0,q1,q2; ry(-1.1071487177940904) q2; ccx q0,q1,q2; }
gate ccry_140121043721168(param0) q0,q1,q2 { ry(pi/3) q2; ccx q0,q1,q2; ry(-pi/3) q2; ccx q0,q1,q2; }
gate ccry_140121043725296(param0) q0,q1,q2 { ry(0.9553166181245093) q2; ccx q0,q1,q2; ry(-0.9553166181245093) q2; ccx q0,q1,q2; }
gate ccry_140121043726064(param0) q0,q1,q2 { ry(pi/4) q2; ccx q0,q1,q2; ry(-pi/4) q2; ccx q0,q1,q2; }
qreg q6419[9];
creg c39[9];
x q6419[5];
x q6419[6];
x q6419[7];
x q6419[8];
ry(2.8066964951504145) q6419[7];
cry_o0(2.801900077422446) q6419[7],q6419[5];
cx_oFalse q6419[5],q6419[7];
cry_o0_140121008019376_o0(2.796891473791147) q6419[5],q6419[7];
ccry_o0(2.7916545622584157) q6419[5],q6419[7],q6419[6];
cx_oFalse q6419[6],q6419[5];
cry_o0_140121008017216_o0(2.7861714518995697) q6419[6],q6419[5];
cx_oFalse q6419[5],q6419[7];
ccry_o0_140121008023936_o0(2.780422225208397) q6419[6],q6419[5],q6419[4];
cx q6419[4],q6419[6];
cx q6419[4],q6419[5];
cry(2.774384633031956) q6419[4],q6419[7];
ccry_o1(2.768033731426606) q6419[4],q6419[7],q6419[6];
ccry_o1_140121008025952_o1(2.76134144689686) q6419[4],q6419[6],q6419[5];
ccry_o1_140121008129168_o1(2.75427605270114) q6419[4],q6419[5],q6419[3];
cx q6419[3],q6419[7];
cx q6419[3],q6419[6];
cx q6419[3],q6419[5];
cry(2.746801533890032) q6419[3],q6419[7];
ccry_o1_140121008133248_o1(2.738876812009132) q6419[3],q6419[7],q6419[6];
ccry_o1_140121008142224_o1(2.7304547912674457) q6419[3],q6419[6],q6419[5];
ccry_o1_140121008138384_o1(2.7214811754473156) q6419[3],q6419[5],q6419[4];
ccry_o1_140121043849936_o1(2.7118929874383686) q6419[3],q6419[4],q6419[2];
cx q6419[2],q6419[7];
cx q6419[2],q6419[6];
cx q6419[2],q6419[5];
cx q6419[2],q6419[4];
cry(2.7016166987988743) q6419[2],q6419[7];
ccry_o1_140121043857040_o1(2.6905658417935308) q6419[2],q6419[7],q6419[6];
ccry_o1_140121043857424_o1(2.678637925649437) q6419[2],q6419[6],q6419[5];
ccry_o1_140121043846960_o1(2.665710403929377) q6419[2],q6419[5],q6419[4];
ccry_o1_140121043853104_o1(2.651635327336065) q6419[2],q6419[4],q6419[3];
ccry_o1_140121043856896_o1(2.636232143305636) q6419[2],q6419[3],q6419[1];
cx q6419[1],q6419[7];
cx q6419[1],q6419[6];
cx q6419[1],q6419[5];
cx q6419[1],q6419[4];
cx q6419[1],q6419[3];
cry(2.619277831783745) q6419[1],q6419[7];
ccry_o1_140121043854880_o1(2.6004931276326477) q6419[1],q6419[7],q6419[6];
ccry_o1_140121043858720_o1(2.579522850584166) q6419[1],q6419[6],q6419[5];
ccry_o1_140121043851664_o1(2.5559071101326425) q6419[1],q6419[5],q6419[4];
ccry_o1_140121043858768_o1(2.5290379152504543) q6419[1],q6419[4],q6419[3];
ccry_o1_140121043856464_o1(2.498091544796509) q6419[1],q6419[3],q6419[2];
ccry_o1_140121043718912_o1(2.4619188346815495) q6419[1],q6419[2],q6419[0];
cx q6419[0],q6419[8];
cx q6419[0],q6419[7];
cx q6419[0],q6419[1];
cry(2.4188584057763776) q6419[0],q6419[7];
cx_oFalse q6419[7],q6419[8];
ccry_o1_140121043728848_o1(2.366399280279432) q6419[0],q6419[7],q6419[6];
cx q6419[6],q6419[8];
ccry_140121043725104(2.300523983021863) q6419[0],q6419[6],q6419[5];
cx q6419[5],q6419[6];
ccry_140121043718240(2.214297435588181) q6419[0],q6419[5],q6419[4];
cx q6419[4],q6419[5];
ccry_140121043721168(2*pi/3) q6419[0],q6419[4],q6419[3];
cx q6419[3],q6419[4];
ccry_140121043725296(1.9106332362490186) q6419[0],q6419[3],q6419[2];
cx q6419[2],q6419[3];
ccry_140121043726064(pi/2) q6419[0],q6419[2],q6419[1];
cx q6419[1],q6419[2];
measure q6419[0] -> c39[0];
measure q6419[1] -> c39[1];
measure q6419[2] -> c39[2];
measure q6419[3] -> c39[3];
measure q6419[4] -> c39[4];
measure q6419[5] -> c39[5];
measure q6419[6] -> c39[6];
measure q6419[7] -> c39[7];
measure q6419[8] -> c39[8];
