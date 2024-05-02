****** MEDEVA SIMULACIONES ******

Set
     t      'intervalos de tiempo'                                  /1*96/
     N      'number of charging points'                             /1*4/
;

Scalars
DeltaT                                                              /0.25/

*PVS
PPVn        Potencia nominal del modulo en kW                       /10/

*EVS
*SocEVmax    SoC max [0 - 1] -EV                                     /1.0/
socEVmin    SOC min [0 - 1] -EV                                     /0.1/
*Cevbatt      energy capacity (kWh)                                  /35/

*Storage
SocmaxS     Soc max [0 - 1] - Storage                               /1.0/
socminS     SOC min [0 - 1] - Storage                               /0.1/
SocS_ini    SOC inicial [0 - 1] - Storage                           /0.1/
CSbatt      energy capacity (kWh) - Storage                         /23.33/
effc        eficiencia de carga [0 - 1] - Storage                   /0.95/
effd        eficiencia de descarga [0 - 1] - Storage                /0.95/
PSmaxc      max power carga (kW) - Storage                          /10/
PSmaxd      max power descarga (kW) - Storage                       /10/
;

parameter Nt;

Nt = card(t);

*****Parameters for PV model******
parameters Temp(t), Irr(t);

*****Parameters for chargers model******

*Parameter from forecast results
Parameter SOC_ini(t,n)      SoC esperado - EV;
Parameter U_ev(t,n)         uso cargadores;
Parameter Dem(t)            demanda edificio;

*Configuration Parameters
Parameter P_inter_max(t)    max power grid;
Parameter P_ch_max(n)       max power carga (kW) - EV;
Parameter P_dch_max(n)      max power descarga (kW) - EV;
Parameter Eff_ch(n)         eficiencia de carga [0 - 1] -EV;
Parameter Eff_dch(n)        eficiencia de descarga [0 - 1] -EV;
Parameter soc_first(n)      SoC EV t = 1;
Parameter socEVmax(n)       SoC EV max [0 - 1] -EV;
Parameter Cevbatt(n)        Energy capacity (kWh) -EV;


*Prices
Parameter C_buy(t)          Energy buy price (€\kWh);
Parameter C_sell(t)         Energy sell price (€\kWh);

*leer de excel

$onecho > in.txt
par=Temp rng=Temperatura!A2 Rdim=1
par=Irr rng=Irrad!A2 Rdim=1
par=SOC_ini rng=SOC_esperados!A2 Rdim=2
par=U_ev rng=uso_cargadores!A2 Rdim=2
par=Dem rng=demanda_edificio!A2 Rdim=1
par=P_inter_max rng=Potencia_contratada!A2 Rdim=1
par=P_ch_max rng=P_ch_max!A2 Rdim=1
par=P_dch_max rng=P_dch_max!A2 Rdim=1
par=Eff_ch rng=eff_ch!A2 Rdim=1
par=Eff_dch rng=eff_dsc!A2 Rdim=1
par=soc_first rng= Soc_first!A2 Rdim=1
par=C_buy rng=Curva_precios_compra!A2 Rdim=1
par=C_sell rng=C_sell!A2 Rdim=1
par=socEVmax rng=socEVmax!A2 Rdim=1
par=Cevbatt rng=Cevbatt!A2 Rdim=1
$offecho

*Algunos fatan seguro, revisar

$CALL GDXXRW "datosSimulaciones_7 cargadores.xlsx" trace=3 @in.txt
$gdxin "datosSimulaciones_7 cargadores.gdx"

*todas los parametros declarados arriba deben de estar en esta linea
$load Temp, Irr, SOC_ini, U_ev, Dem, P_inter_max, P_ch_max, P_dch_max, Eff_ch, Eff_dch, soc_first, C_buy, C_sell, socEVmax, Cevbatt,
$gdxin


*gebneracion solar
Parameter Tc(t) temperatura de la cell;
Tc(t) = 17.23292 + 0.451708*Temp(t) +22.706*Irr(t);

Parameter PPVav(t)  potencia fotovoltaica disponible;
          PPVav(t) = max(0,((-0.062059*Irr(t)+0.04277774)*Tc(t)+9.692792*Irr(t)-1.885868))*(PPvn/6.6);

*es para identificar cuando se inicia un proceso de carga nuevo
Parameter new_case(T,N);
loop(n,
         loop(t,If(
                         soc_ini(t,n) >= socEVmin and soc_ini(t,n) <> socEVmax(n) , new_case(t,n) = 1;
                 else
                         new_case(t,n) = 0;
                 );
         );
);

*es para identificar el SoC de salida de cada vehiculo.

Parameter new_socEVmin(t,n);
loop(n,
         loop(t $(ord(t)<Nt),If(
                         SocEVmin*U_ev(t,n)>0 and SocEVmin*U_ev(t+1,n)=0 , new_socEVmin(t,n) = SOC_ini(t,n) ;
                 else
                         new_socEVmin(t,n) = socEVmin;
                 );
         );
);
*Implicamos que para cada instante de timepo sea igual al socEVmin menos para el instante en que el coche sale de la estación de carga que debe ser igual al SoC esperado.

Variables
pPV(t)      solar power
pPV_sc(t)   solar power used to charge battery.

*chargers
pEVc(t,n)   charging power EV
pEVd(t,n)   discharging power EV
xEV(t,n)    charge proccess
SOCev(t,N)  state of charge ev

* fo
z           objective function

* grid
pIb(t)      power from grid
pIs(t)      power to grid
x(t)        direccion de la interconexion

* storage
pSc(t)      charging power EV
pSd(t)      discharging power EV
xS(t)       charge proccess
SOCs(t)     state of charge ev


Positive Variables pPV, pPV_sc, pEVc ,pEVd, SOCev, pIb, pIs, pSc, pSd, SOCs;
Binary Variable x,  xEV, xS;


Equations
cost
balance(t)
PVpower(t)
PVpower2(t)
inter1(t)
inter2(t)
balanceSOCev(t,n)
SOCiev(n)
soc_LB(t,n)
soc_UB(t,n)
powercev(t,n)
powerdev(t,n)
balanceSOC(t)
SOCi
SOCf(t)
powercs(t)
powerds(t)
MinSocs(t)
MaxSocs(t)
;

*objective function
cost    ..  z =e= sum((t,n), (1-SOCev(t,n))) + sum(t,0.2*pIb(t));
*power balance
balance(t)  ..  pPV(t) + pPV_sc(t) +pIb(t) + sum(n, pEVd(t,n)) + psd(t) =e=  Dem(t)+ sum(n,pEVc(t,n)) + pIs(t) + psc(t);
*PV power
PVpower(t)   .. pPV(t) + pPV_sc(t) =e= PPVav(t);
PVpower2(t)  .. pPV_sc(t) =e= psc(t);
* inter
inter1(t)    .. pIs(t) =l= (1-x(t))*P_inter_max(t);
inter2(t)    .. pIb(t) =l= x(t)*P_inter_max(t);

*EVS
balanceSOCev(t,n)$(ord(t)>1) ..  SOCev(t,n)*Cevbatt(n) =e= U_ev(t,n)*(
                                                    (SOCev(t-1,n)*(1-new_case(t,n))+SOC_ini(t,n)*new_case(t,n)
                                                    )*Cevbatt(n) + pEVc(t,n)*deltaT*Eff_ch(n) - pEVd(t,n)*deltaT/Eff_dch(n));
SOCiev(n)     .. SOCev("1",n)*Cevbatt(n) =e= U_ev("1",n)*(soc_first(n)*Cevbatt(n) + pEVc("1",n)*deltaT*Eff_ch(n)
                                          - pEVd("1",n)*deltaT/Eff_dch(n));
soc_LB(t,n)         .. SOCev(t,n) =g= new_socEVmin(t,n)*U_ev(t,n);
soc_UB(t,n)         .. SOCev(t,n) =l= SocEVmax(n)*U_ev(t,n);
powercev(t,n) .. pEVc(t,n) =l= xev(t,n)*U_ev(t,n)*P_ch_max(n);
powerdev(t,n) .. pEVd(t,n) =l= (1-xev(t,n))*U_ev(t,n)*P_dch_max(n);

*Storage
balanceSOC(t)$(ord(t)>1)         ..  SOCs(t)*CSbatt =e= SOCs(t-1)*CSbatt + psc(t)*deltaT*effc - psd(t)*deltaT/effd;
SOCi                             .. SOCs("1")*CSbatt =e= SOCs_ini*CSbatt + psc("1")*deltaT*effc - psd("1")*deltaT/effd;
SOCf(t)$(ord(t)=Nt)              .. SOCs(t) =e= SOCs_ini;
powercs(t)                       .. psc(t) =l= xs(t)*PSmaxc;
powerds(t)                       .. psd(t) =l= (1-xs(t))*PSmaxd;
MinSocs(t)                       .. SOCs(t) =g= SocminS;
MaxSocs(t)                       .. SOCs(t) =l= SocmaxS;

MODEL medeva_escenario /all/;

option mip =cplex;
*tiempo en segundo maximo
option resLim = 20200;
option IterLim=210000000
*gap  permitido
option OptCR=0.0001;
option solvelink=0;


SOLVE medeva_escenario using mip minimizing z

execute_unload "Results_medeva_base.gdx"  pPV, pPV_sc, pEVc, pEVd, xEV, SOCev, pIb, pIs, x, pSc, pSd, xS, SOCs, z

execute 'gdxxrw.exe "Results_medeva_base.gdx" o="Results_medeva_base_2.xlsx" Squeeze=N var =pPV.l  rng=pPV!'
execute 'gdxxrw.exe "Results_medeva_base.gdx" o="Results_medeva_base_2.xlsx" Squeeze=N var =pPV_sc.l  rng=pPV_sc!'
execute 'gdxxrw.exe "Results_medeva_base.gdx" o="Results_medeva_base_2.xlsx" Squeeze=N var =pEVc.l  rng=pEVc!'
execute 'gdxxrw.exe "Results_medeva_base.gdx" o="Results_medeva_base_2.xlsx" Squeeze=N var =pEVd.l  rng=pEVd!'
execute 'gdxxrw.exe "Results_medeva_base.gdx" o="Results_medeva_base_2.xlsx" Squeeze=N var =xEV.l  rng=xEV!'
execute 'gdxxrw.exe "Results_medeva_base.gdx" o="Results_medeva_base_2.xlsx" Squeeze=N var =SOCev.l  rng=SOCev!'
execute 'gdxxrw.exe "Results_medeva_base.gdx" o="Results_medeva_base_2.xlsx" Squeeze=N var =pIb.l  rng=pIb!'
execute 'gdxxrw.exe "Results_medeva_base.gdx" o="Results_medeva_base_2.xlsx" Squeeze=N var =pIs.l  rng=pIs!'
execute 'gdxxrw.exe "Results_medeva_base.gdx" o="Results_medeva_base_2.xlsx" Squeeze=N var =x.l  rng=x!'
execute 'gdxxrw.exe "Results_medeva_base.gdx" o="Results_medeva_base_2.xlsx" Squeeze=N var =pSc.l  rng=pSc!'
execute 'gdxxrw.exe "Results_medeva_base.gdx" o="Results_medeva_base_2.xlsx" Squeeze=N var =pSd.l  rng=pSd!'
execute 'gdxxrw.exe "Results_medeva_base.gdx" o="Results_medeva_base_2.xlsx" Squeeze=N var =xS.l  rng=xS!'
execute 'gdxxrw.exe "Results_medeva_base.gdx" o="Results_medeva_base_2.xlsx" Squeeze=N var =SOCs.l  rng=SOCs!'
execute 'gdxxrw.exe "Results_medeva_base.gdx" o="Results_medeva_base_2.xlsx" Squeeze=N var =z.l rng=funcion_objetivo!'



