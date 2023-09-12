OPENQASM 2.0;
include "qelib1.inc";
gate cry_o0(param0) q0,q1 { x q0; cry(1.9106332362490186) q0,q1; x q0; }
gate cx_oFalse q0,q1 { x q0; cx q0,q1; x q0; }
gate ccry(param0) q0,q1,q2 { ry(1.4501177736638868) q2; ccx q0,q1,q2; ry(-1.4501177736638868) q2; ccx q0,q1,q2; }
gate ccry_o1(param0) q0,q1,q2 { x q1; ccry(2.9002355473277737) q0,q1,q2; x q1; }
gate ccry_139651302503088(param0) q0,q1,q2 { ry(1.4483209188811768) q2; ccx q0,q1,q2; ry(-1.4483209188811768) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302629312(param0) q0,q1,q2 { x q1; ccry_139651302503088(2.8966418377623535) q0,q1,q2; x q1; }
gate ccry_139651302506256(param0) q0,q1,q2 { ry(1.4473918600601101) q2; ccx q0,q1,q2; ry(-1.4473918600601101) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302636608(param0) q0,q1,q2 { x q1; ccry_139651302506256(2.8947837201202202) q0,q1,q2; x q1; }
gate ccry_139651302501312(param0) q0,q1,q2 { ry(1.446441332248135) q2; ccx q0,q1,q2; ry(-1.446441332248135) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302628016(param0) q0,q1,q2 { x q1; ccry_139651302501312(2.89288266449627) q0,q1,q2; x q1; }
gate ccry_139651358415392(param0) q0,q1,q2 { ry(1.445468495626831) q2; ccx q0,q1,q2; ry(-1.445468495626831) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302626336(param0) q0,q1,q2 { x q1; ccry_139651358415392(2.890936991253662) q0,q1,q2; x q1; }
gate ccry_139651358415584(param0) q0,q1,q2 { ry(1.4434522996602146) q2; ccx q0,q1,q2; ry(-1.4434522996602146) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302629936(param0) q0,q1,q2 { x q1; ccry_139651358415584(2.886904599320429) q0,q1,q2; x q1; }
gate ccry_139651358412128(param0) q0,q1,q2 { ry(1.4424070131594149) q2; ccx q0,q1,q2; ry(-1.4424070131594149) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302632240(param0) q0,q1,q2 { x q1; ccry_139651358412128(2.8848140263188298) q0,q1,q2; x q1; }
gate ccry_139651358420720(param0) q0,q1,q2 { ry(1.441335555791786) q2; ccx q0,q1,q2; ry(-1.441335555791786) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302623744(param0) q0,q1,q2 { x q1; ccry_139651358420720(2.882671111583572) q0,q1,q2; x q1; }
gate ccry_139651358421968(param0) q0,q1,q2 { ry(1.4402368169098752) q2; ccx q0,q1,q2; ry(-1.4402368169098752) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302622256(param0) q0,q1,q2 { x q1; ccry_139651358421968(2.8804736338197503) q0,q1,q2; x q1; }
gate ccry_139651358417792(param0) q0,q1,q2 { ry(1.4391096187364805) q2; ccx q0,q1,q2; ry(-1.4391096187364805) q2; ccx q0,q1,q2; }
gate ccry_o1_139651357701072(param0) q0,q1,q2 { x q1; ccry_139651358417792(2.878219237472961) q0,q1,q2; x q1; }
gate ccry_139651358422544(param0) q0,q1,q2 { ry(1.4367647653836775) q2; ccx q0,q1,q2; ry(-1.4367647653836775) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302631184(param0) q0,q1,q2 { x q1; ccry_139651358422544(2.873529530767355) q0,q1,q2; x q1; }
gate ccry_139651358412032(param0) q0,q1,q2 { ry(1.4355443685502411) q2; ccx q0,q1,q2; ry(-1.4355443685502411) q2; ccx q0,q1,q2; }
gate ccry_o1_139651357694304(param0) q0,q1,q2 { x q1; ccry_139651358412032(2.8710887371004823) q0,q1,q2; x q1; }
gate ccry_139651283499232(param0) q0,q1,q2 { ry(1.4342900156325915) q2; ccx q0,q1,q2; ry(-1.4342900156325915) q2; ccx q0,q1,q2; }
gate ccry_o1_139651357697136(param0) q0,q1,q2 { x q1; ccry_139651283499232(2.868580031265183) q0,q1,q2; x q1; }
gate ccry_139651283491744(param0) q0,q1,q2 { ry(1.4330001021490115) q2; ccx q0,q1,q2; ry(-1.4330001021490115) q2; ccx q0,q1,q2; }
gate ccry_o1_139651357697280(param0) q0,q1,q2 { x q1; ccry_139651283491744(2.866000204298023) q0,q1,q2; x q1; }
gate ccry_139651283496016(param0) q0,q1,q2 { ry(1.431672915427498) q2; ccx q0,q1,q2; ry(-1.431672915427498) q2; ccx q0,q1,q2; }
gate ccry_o1_139651357694928(param0) q0,q1,q2 { x q1; ccry_139651283496016(2.863345830854996) q0,q1,q2; x q1; }
gate ccry_139651283498368(param0) q0,q1,q2 { ry(1.4303066250413763) q2; ccx q0,q1,q2; ry(-1.4303066250413763) q2; ccx q0,q1,q2; }
gate ccry_o1_139651357697328(param0) q0,q1,q2 { x q1; ccry_139651283498368(2.8606132500827526) q0,q1,q2; x q1; }
gate ccry_139651283485792(param0) q0,q1,q2 { ry(1.4274487578895312) q2; ccx q0,q1,q2; ry(-1.4274487578895312) q2; ccx q0,q1,q2; }
gate ccry_o1_139651357695504(param0) q0,q1,q2 { x q1; ccry_139651283485792(2.8548975157790624) q0,q1,q2; x q1; }
gate ccry_139651283497504(param0) q0,q1,q2 { ry(1.4259528297963369) q2; ccx q0,q1,q2; ry(-1.4259528297963369) q2; ccx q0,q1,q2; }
gate ccry_o1_139651357690992(param0) q0,q1,q2 { x q1; ccry_139651283497504(2.8519056595926737) q0,q1,q2; x q1; }
gate ccry_139651283486752(param0) q0,q1,q2 { ry(1.4244090675006476) q2; ccx q0,q1,q2; ry(-1.4244090675006476) q2; ccx q0,q1,q2; }
gate ccry_o1_139651357694880(param0) q0,q1,q2 { x q1; ccry_139651283486752(2.848818135001295) q0,q1,q2; x q1; }
gate ccry_139651283493088(param0) q0,q1,q2 { ry(1.4228148660461128) q2; ccx q0,q1,q2; ry(-1.4228148660461128) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302643728(param0) q0,q1,q2 { x q1; ccry_139651283493088(2.8456297320922257) q0,q1,q2; x q1; }
gate ccry_139651283498080(param0) q0,q1,q2 { ry(1.4211674174353792) q2; ccx q0,q1,q2; ry(-1.4211674174353792) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302648240(param0) q0,q1,q2 { x q1; ccry_139651283498080(2.8423348348707584) q0,q1,q2; x q1; }
gate ccry_139651283490160(param0) q0,q1,q2 { ry(1.419463689817681) q2; ccx q0,q1,q2; ry(-1.419463689817681) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302639840(param0) q0,q1,q2 { x q1; ccry_139651283490160(2.838927379635362) q0,q1,q2; x q1; }
gate ccry_139651315620672(param0) q0,q1,q2 { ry(1.417700404008042) q2; ccx q0,q1,q2; ry(-1.417700404008042) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302651696(param0) q0,q1,q2 { x q1; ccry_139651315620672(2.835400808016084) q0,q1,q2; x q1; }
gate ccry_139651283490640(param0) q0,q1,q2 { ry(1.4139806414504958) q2; ccx q0,q1,q2; ry(-1.4139806414504958) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302647856(param0) q0,q1,q2 { x q1; ccry_139651283490640(2.8279612829009917) q0,q1,q2; x q1; }
gate ccry_139651315625616(param0) q0,q1,q2 { ry(1.412016112149136) q2; ccx q0,q1,q2; ry(-1.412016112149136) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302640176(param0) q0,q1,q2 { x q1; ccry_139651315625616(2.824032224298272) q0,q1,q2; x q1; }
gate ccry_139651315616400(param0) q0,q1,q2 { ry(1.409975846120432) q2; ccx q0,q1,q2; ry(-1.409975846120432) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302651072(param0) q0,q1,q2 { x q1; ccry_139651315616400(2.819951692240864) q0,q1,q2; x q1; }
gate ccry_139651315623552(param0) q0,q1,q2 { ry(1.4078548481843773) q2; ccx q0,q1,q2; ry(-1.4078548481843773) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302645360(param0) q0,q1,q2 { x q1; ccry_139651315623552(2.8157096963687547) q0,q1,q2; x q1; }
gate ccry_139651315621152(param0) q0,q1,q2 { ry(1.4056476493802699) q2; ccx q0,q1,q2; ry(-1.4056476493802699) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302652752(param0) q0,q1,q2 { x q1; ccry_139651315621152(2.8112952987605397) q0,q1,q2; x q1; }
gate ccry_139651315615728(param0) q0,q1,q2 { ry(1.4033482475752073) q2; ccx q0,q1,q2; ry(-1.4033482475752073) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302638736(param0) q0,q1,q2 { x q1; ccry_139651315615728(2.8066964951504145) q0,q1,q2; x q1; }
gate ccry_139651358421440(param0) q0,q1,q2 { ry(1.400950038711223) q2; ccx q0,q1,q2; ry(-1.400950038711223) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302646560(param0) q0,q1,q2 { x q1; ccry_139651358421440(2.801900077422446) q0,q1,q2; x q1; }
gate ccry_139651283488432(param0) q0,q1,q2 { ry(1.3984457368955736) q2; ccx q0,q1,q2; ry(-1.3984457368955736) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302639984(param0) q0,q1,q2 { x q1; ccry_139651283488432(2.796891473791147) q0,q1,q2; x q1; }
gate ccry_139651315620528(param0) q0,q1,q2 { ry(1.3930857259497849) q2; ccx q0,q1,q2; ry(-1.3930857259497849) q2; ccx q0,q1,q2; }
gate ccry_o1_139651358144112(param0) q0,q1,q2 { x q1; ccry_139651315620528(2.7861714518995697) q0,q1,q2; x q1; }
gate ccry_139651315621056(param0) q0,q1,q2 { ry(1.3902111126041985) q2; ccx q0,q1,q2; ry(-1.3902111126041985) q2; ccx q0,q1,q2; }
gate ccry_o1_139651358139936(param0) q0,q1,q2 { x q1; ccry_139651315621056(2.780422225208397) q0,q1,q2; x q1; }
gate ccry_139651283485504(param0) q0,q1,q2 { ry(1.387192316515978) q2; ccx q0,q1,q2; ry(-1.387192316515978) q2; ccx q0,q1,q2; }
gate ccry_o1_139651358143008(param0) q0,q1,q2 { x q1; ccry_139651283485504(2.774384633031956) q0,q1,q2; x q1; }
gate ccry_139651302292304(param0) q0,q1,q2 { ry(1.3840168657133032) q2; ccx q0,q1,q2; ry(-1.3840168657133032) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302646176(param0) q0,q1,q2 { x q1; ccry_139651302292304(2.7680337314266064) q0,q1,q2; x q1; }
gate ccry_139651302497856(param0) q0,q1,q2 { ry(1.38067072344843) q2; ccx q0,q1,q2; ry(-1.38067072344843) q2; ccx q0,q1,q2; }
gate ccry_o1_139651358146464(param0) q0,q1,q2 { x q1; ccry_139651302497856(2.76134144689686) q0,q1,q2; x q1; }
gate ccry_139651358418176(param0) q0,q1,q2 { ry(1.37713802635057) q2; ccx q0,q1,q2; ry(-1.37713802635057) q2; ccx q0,q1,q2; }
gate ccry_o1_139651358132832(param0) q0,q1,q2 { x q1; ccry_139651358418176(2.75427605270114) q0,q1,q2; x q1; }
gate ccry_139651358133168(param0) q0,q1,q2 { ry(1.373400766945016) q2; ccx q0,q1,q2; ry(-1.373400766945016) q2; ccx q0,q1,q2; }
gate ccry_o1_139651358131632(param0) q0,q1,q2 { x q1; ccry_139651358133168(2.746801533890032) q0,q1,q2; x q1; }
gate ccry_139651357696992(param0) q0,q1,q2 { ry(1.369438406004566) q2; ccx q0,q1,q2; ry(-1.369438406004566) q2; ccx q0,q1,q2; }
gate ccry_o1_139651358144640(param0) q0,q1,q2 { x q1; ccry_139651357696992(2.738876812009132) q0,q1,q2; x q1; }
gate ccry_139651315872336(param0) q0,q1,q2 { ry(1.3652273956337229) q2; ccx q0,q1,q2; ry(-1.3652273956337229) q2; ccx q0,q1,q2; }
gate ccry_o1_139651358141424(param0) q0,q1,q2 { x q1; ccry_139651315872336(2.7304547912674457) q0,q1,q2; x q1; }
gate ccry_139651359061376(param0) q0,q1,q2 { ry(1.3559464937191845) q2; ccx q0,q1,q2; ry(-1.3559464937191845) q2; ccx q0,q1,q2; }
gate ccry_o1_139651358142864(param0) q0,q1,q2 { x q1; ccry_139651359061376(2.711892987438369) q0,q1,q2; x q1; }
gate ccry_139651359054560(param0) q0,q1,q2 { ry(1.3508083493994372) q2; ccx q0,q1,q2; ry(-1.3508083493994372) q2; ccx q0,q1,q2; }
gate ccry_o1_139651358139792(param0) q0,q1,q2 { x q1; ccry_139651359054560(2.7016166987988743) q0,q1,q2; x q1; }
gate ccry_139651315874736(param0) q0,q1,q2 { ry(1.3452829208967654) q2; ccx q0,q1,q2; ry(-1.3452829208967654) q2; ccx q0,q1,q2; }
gate ccry_o1_139651358144832(param0) q0,q1,q2 { x q1; ccry_139651315874736(2.6905658417935308) q0,q1,q2; x q1; }
gate ccry_139651358718464(param0) q0,q1,q2 { ry(1.3393189628247184) q2; ccx q0,q1,q2; ry(-1.3393189628247184) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302280496(param0) q0,q1,q2 { x q1; ccry_139651358718464(2.678637925649437) q0,q1,q2; x q1; }
gate ccry_139651358713424(param0) q0,q1,q2 { ry(1.3328552019646884) q2; ccx q0,q1,q2; ry(-1.3328552019646884) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302283808(param0) q0,q1,q2 { x q1; ccry_139651358713424(2.665710403929377) q0,q1,q2; x q1; }
gate ccry_139651283862144(param0) q0,q1,q2 { ry(1.3258176636680326) q2; ccx q0,q1,q2; ry(-1.3258176636680326) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302279920(param0) q0,q1,q2 { x q1; ccry_139651283862144(2.651635327336065) q0,q1,q2; x q1; }
gate ccry_139651283872560(param0) q0,q1,q2 { ry(1.318116071652818) q2; ccx q0,q1,q2; ry(-1.318116071652818) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302286976(param0) q0,q1,q2 { x q1; ccry_139651283872560(2.636232143305636) q0,q1,q2; x q1; }
gate ccry_139651283869968(param0) q0,q1,q2 { ry(1.3096389158918724) q2; ccx q0,q1,q2; ry(-1.3096389158918724) q2; ccx q0,q1,q2; }
gate ccry_o1_139651358138880(param0) q0,q1,q2 { x q1; ccry_139651283869968(2.619277831783745) q0,q1,q2; x q1; }
gate ccry_139651334795568(param0) q0,q1,q2 { ry(1.3002465638163239) q2; ccx q0,q1,q2; ry(-1.3002465638163239) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302288272(param0) q0,q1,q2 { x q1; ccry_139651334795568(2.6004931276326477) q0,q1,q2; x q1; }
gate ccry_139651334785056(param0) q0,q1,q2 { ry(1.289761425292083) q2; ccx q0,q1,q2; ry(-1.289761425292083) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302288176(param0) q0,q1,q2 { x q1; ccry_139651334785056(2.579522850584166) q0,q1,q2; x q1; }
gate ccry_139651307644112(param0) q0,q1,q2 { ry(1.2645189576252271) q2; ccx q0,q1,q2; ry(-1.2645189576252271) q2; ccx q0,q1,q2; }
gate ccry_o1_139651302292448(param0) q0,q1,q2 { x q1; ccry_139651307644112(2.5290379152504543) q0,q1,q2; x q1; }
gate ccry_139651302277712(param0) q0,q1,q2 { ry(1.2490457723982544) q2; ccx q0,q1,q2; ry(-1.2490457723982544) q2; ccx q0,q1,q2; }
gate ccry_139651302287456(param0) q0,q1,q2 { ry(1.2309594173407747) q2; ccx q0,q1,q2; ry(-1.2309594173407747) q2; ccx q0,q1,q2; }
gate ccry_139651302292928(param0) q0,q1,q2 { ry(1.2094292028881888) q2; ccx q0,q1,q2; ry(-1.2094292028881888) q2; ccx q0,q1,q2; }
gate ccry_139651302280352(param0) q0,q1,q2 { ry(1.183199640139716) q2; ccx q0,q1,q2; ry(-1.183199640139716) q2; ccx q0,q1,q2; }
gate ccry_139651302504048(param0) q0,q1,q2 { ry(1.1502619915109316) q2; ccx q0,q1,q2; ry(-1.1502619915109316) q2; ccx q0,q1,q2; }
gate ccry_139651302502368(param0) q0,q1,q2 { ry(1.1071487177940904) q2; ccx q0,q1,q2; ry(-1.1071487177940904) q2; ccx q0,q1,q2; }
gate ccry_139651302495984(param0) q0,q1,q2 { ry(pi/3) q2; ccx q0,q1,q2; ry(-pi/3) q2; ccx q0,q1,q2; }
gate ccry_139651302491184(param0) q0,q1,q2 { ry(0.9553166181245093) q2; ccx q0,q1,q2; ry(-0.9553166181245093) q2; ccx q0,q1,q2; }
gate ccry_139651302495408(param0) q0,q1,q2 { ry(pi/4) q2; ccx q0,q1,q2; ry(-pi/4) q2; ccx q0,q1,q2; }
qreg q15930[13];
creg c15[13];
ry(2.7468015338900313) q15930[8];
cry(2.568079549166696) q15930[8],q15930[9];
cry_o0(1.9106332362490186) q15930[9],q15930[10];
cx q15930[8],q15930[9];
cry(pi/2) q15930[10],q15930[11];
cx_oFalse q15930[8],q15930[11];
cry(pi/2) q15930[9],q15930[8];
ccry_o1(2.9002355473277737) q15930[8],q15930[9],q15930[7];
cx q15930[7],q15930[11];
cx q15930[7],q15930[10];
cx q15930[7],q15930[9];
cry(2.898458609847934) q15930[7],q15930[11];
ccry_o1_139651302629312_o1(2.8966418377623535) q15930[7],q15930[11],q15930[10];
ccry_o1_139651302636608_o1(2.8947837201202202) q15930[7],q15930[10],q15930[9];
ccry_o1_139651302628016_o1(2.89288266449627) q15930[7],q15930[9],q15930[8];
ccry_o1_139651302626336_o1(2.890936991253662) q15930[7],q15930[8],q15930[6];
cx q15930[6],q15930[11];
cx q15930[6],q15930[10];
cx q15930[6],q15930[9];
cx q15930[6],q15930[8];
cry(2.8889449273052294) q15930[6],q15930[11];
ccry_o1_139651302629936_o1(2.886904599320429) q15930[6],q15930[11],q15930[10];
ccry_o1_139651302632240_o1(2.8848140263188298) q15930[6],q15930[10],q15930[9];
ccry_o1_139651302623744_o1(2.882671111583572) q15930[6],q15930[9],q15930[8];
ccry_o1_139651302622256_o1(2.8804736338197503) q15930[6],q15930[8],q15930[7];
ccry_o1_139651357701072_o1(2.878219237472961) q15930[6],q15930[7],q15930[5];
cx q15930[5],q15930[11];
cx q15930[5],q15930[10];
cx q15930[5],q15930[9];
cx q15930[5],q15930[8];
cx q15930[5],q15930[7];
cry(2.8759054221120626) q15930[5],q15930[11];
ccry_o1_139651302631184_o1(2.873529530767355) q15930[5],q15930[11],q15930[10];
ccry_o1_139651357694304_o1(2.8710887371004823) q15930[5],q15930[10],q15930[9];
ccry_o1_139651357697136_o1(2.868580031265183) q15930[5],q15930[9],q15930[8];
ccry_o1_139651357697280_o1(2.866000204298023) q15930[5],q15930[8],q15930[7];
ccry_o1_139651357694928_o1(2.863345830854996) q15930[5],q15930[7],q15930[6];
ccry_o1_139651357697328_o1(2.8606132500827526) q15930[5],q15930[6],q15930[4];
cx q15930[4],q15930[11];
cx q15930[4],q15930[10];
cx q15930[4],q15930[9];
cx q15930[4],q15930[8];
cx q15930[4],q15930[7];
cx q15930[4],q15930[6];
cry(2.8577985443814655) q15930[4],q15930[11];
ccry_o1_139651357695504_o1(2.8548975157790624) q15930[4],q15930[11],q15930[10];
ccry_o1_139651357690992_o1(2.8519056595926737) q15930[4],q15930[10],q15930[9];
ccry_o1_139651357694880_o1(2.848818135001295) q15930[4],q15930[9],q15930[8];
ccry_o1_139651302643728_o1(2.8456297320922257) q15930[4],q15930[8],q15930[7];
ccry_o1_139651302648240_o1(2.8423348348707584) q15930[4],q15930[7],q15930[6];
ccry_o1_139651302639840_o1(2.838927379635362) q15930[4],q15930[6],q15930[5];
ccry_o1_139651302651696_o1(2.835400808016084) q15930[4],q15930[5],q15930[3];
cx q15930[3],q15930[11];
cx q15930[3],q15930[10];
cx q15930[3],q15930[9];
cx q15930[3],q15930[8];
cx q15930[3],q15930[7];
cx q15930[3],q15930[6];
cx q15930[3],q15930[5];
cry(2.8317480138481663) q15930[3],q15930[11];
ccry_o1_139651302647856_o1(2.8279612829009917) q15930[3],q15930[11],q15930[10];
ccry_o1_139651302640176_o1(2.824032224298272) q15930[3],q15930[10],q15930[9];
ccry_o1_139651302651072_o1(2.819951692240864) q15930[3],q15930[9],q15930[8];
ccry_o1_139651302645360_o1(2.8157096963687547) q15930[3],q15930[8],q15930[7];
ccry_o1_139651302652752_o1(2.8112952987605397) q15930[3],q15930[7],q15930[6];
ccry_o1_139651302638736_o1(2.8066964951504145) q15930[3],q15930[6],q15930[5];
ccry_o1_139651302646560_o1(2.801900077422446) q15930[3],q15930[5],q15930[4];
ccry_o1_139651302639984_o1(2.796891473791147) q15930[3],q15930[4],q15930[2];
cx q15930[2],q15930[11];
cx q15930[2],q15930[10];
cx q15930[2],q15930[9];
cx q15930[2],q15930[8];
cx q15930[2],q15930[7];
cx q15930[2],q15930[6];
cx q15930[2],q15930[5];
cx q15930[2],q15930[4];
cry(2.7916545622584157) q15930[2],q15930[11];
ccry_o1_139651358144112_o1(2.7861714518995697) q15930[2],q15930[11],q15930[10];
ccry_o1_139651358139936_o1(2.780422225208397) q15930[2],q15930[10],q15930[9];
ccry_o1_139651358143008_o1(2.774384633031956) q15930[2],q15930[9],q15930[8];
ccry_o1_139651302646176_o1(2.7680337314266064) q15930[2],q15930[8],q15930[7];
ccry_o1_139651358146464_o1(2.76134144689686) q15930[2],q15930[7],q15930[6];
ccry_o1_139651358132832_o1(2.75427605270114) q15930[2],q15930[6],q15930[5];
ccry_o1_139651358131632_o1(2.746801533890032) q15930[2],q15930[5],q15930[4];
ccry_o1_139651358144640_o1(2.738876812009132) q15930[2],q15930[4],q15930[3];
ccry_o1_139651358141424_o1(2.7304547912674457) q15930[2],q15930[3],q15930[1];
cx q15930[1],q15930[11];
cx q15930[1],q15930[10];
cx q15930[1],q15930[9];
cx q15930[1],q15930[8];
cx q15930[1],q15930[7];
cx q15930[1],q15930[6];
cx q15930[1],q15930[5];
cx q15930[1],q15930[4];
cx q15930[1],q15930[3];
cry(2.7214811754473156) q15930[1],q15930[11];
ccry_o1_139651358142864_o1(2.711892987438369) q15930[1],q15930[11],q15930[10];
ccry_o1_139651358139792_o1(2.7016166987988743) q15930[1],q15930[10],q15930[9];
ccry_o1_139651358144832_o1(2.6905658417935308) q15930[1],q15930[9],q15930[8];
ccry_o1_139651302280496_o1(2.678637925649437) q15930[1],q15930[8],q15930[7];
ccry_o1_139651302283808_o1(2.665710403929377) q15930[1],q15930[7],q15930[6];
ccry_o1_139651302279920_o1(2.651635327336065) q15930[1],q15930[6],q15930[5];
ccry_o1_139651302286976_o1(2.636232143305636) q15930[1],q15930[5],q15930[4];
ccry_o1_139651358138880_o1(2.619277831783745) q15930[1],q15930[4],q15930[3];
ccry_o1_139651302288272_o1(2.6004931276326477) q15930[1],q15930[3],q15930[2];
x q15930[12];
ccry_o1_139651302288176_o1(2.579522850584166) q15930[1],q15930[2],q15930[0];
cx q15930[0],q15930[12];
cx q15930[0],q15930[11];
cx q15930[0],q15930[1];
cx_oFalse q15930[0],q15930[12];
cry(2.5559071101326425) q15930[0],q15930[11];
cx_oFalse q15930[11],q15930[12];
ccry_o1_139651302292448_o1(2.5290379152504543) q15930[0],q15930[11],q15930[10];
cx q15930[10],q15930[12];
ccry_139651302277712(2.498091544796509) q15930[0],q15930[10],q15930[9];
cx q15930[9],q15930[10];
ccry_139651302287456(2.4619188346815495) q15930[0],q15930[9],q15930[8];
cx q15930[8],q15930[9];
ccry_139651302292928(2.4188584057763776) q15930[0],q15930[8],q15930[7];
cx q15930[7],q15930[8];
ccry_139651302280352(2.366399280279432) q15930[0],q15930[7],q15930[6];
cx q15930[6],q15930[7];
ccry_139651302504048(2.300523983021863) q15930[0],q15930[6],q15930[5];
cx q15930[5],q15930[6];
ccry_139651302502368(2.214297435588181) q15930[0],q15930[5],q15930[4];
cx q15930[4],q15930[5];
ccry_139651302495984(2*pi/3) q15930[0],q15930[4],q15930[3];
cx q15930[3],q15930[4];
ccry_139651302491184(1.9106332362490186) q15930[0],q15930[3],q15930[2];
cx q15930[2],q15930[3];
ccry_139651302495408(pi/2) q15930[0],q15930[2],q15930[1];
cx q15930[1],q15930[2];
measure q15930[0] -> c15[0];
measure q15930[1] -> c15[1];
measure q15930[2] -> c15[2];
measure q15930[3] -> c15[3];
measure q15930[4] -> c15[4];
measure q15930[5] -> c15[5];
measure q15930[6] -> c15[6];
measure q15930[7] -> c15[7];
measure q15930[8] -> c15[8];
measure q15930[9] -> c15[9];
measure q15930[10] -> c15[10];
measure q15930[11] -> c15[11];
measure q15930[12] -> c15[12];
