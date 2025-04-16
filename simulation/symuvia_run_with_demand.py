from ctypes import cdll, byref
import ctypes
import os
import random as rd
import datetime
import sys
import shutil
from ctypes import byref
import ctypes as ct 
import datetime

import os
import pandas as pd
import datetime

class Symuvia_run_with_demand:
    def __init__(self, symuvia):
        self.__symuvia = symuvia
        self.__logger=self.__symuvia.logger()
        self.__symuflow_ddl=self.__symuvia.symuflow_ddl()
        self.__demand=self.__symuvia.demand()
        self.__timeSimSec=self.__symuvia.timeSimSec()
        self.__symuvia_input=self.__symuvia.symuvia_input()
        self.__logger.log(cl=None, method=None, message="Init Symuvia simulation. Run with demand")

    def test(self):
        time, tmptime, bEnd, period, VNC, VC = 0 , 0, ct.c_int(0), 0, 0, 0

        # ------------------------
        # Time step flow calculation
        # ------------------------

        while (bEnd.value == 0):
            # Vehicles creation (warning: vehicules with time creation between 0 and 1 are not generated)
            if (time > 0):
                squery = str(time) + ' < creation <= ' + str(time + 1)
                dts = self.__demand.query(squery)

                for index, row in dts.iterrows():
                    tc = ct.c_double(row.creation - time)

                    if (row.origin != row.destination):
                        ok = self.__symuflow_ddl.SymCreateVehicleWithRouteEx(row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8'), 1, tc,row.path.encode('UTF8'))
                        if (ok < 0):
                            print('Vehicle not created: ', ok, ' ', row)
                            VNC = VNC + 1
                        else:
                            VC = VC + 1
                    else:
                        print('Vehicle not created: ', row)
                        VNC = VNC + 1

            # Time step calculation
            ok = self.__symuflow_ddl.SymRunNextStepLiteEx(1, byref(bEnd))
            time = time + 1
            tmptime = tmptime + 1
            if (bEnd.value != 0):
                self.__symuflow_ddl.SymUnloadCurrentNetworkEx()
                print(f'Microscopic simulation completed')
                print(VC, ' ', VNC)

        del self.__symuflow_ddl

    def run(self,run):
        if run:
            pos,time, tmptime, bEnd, period, VNC, VC = 1, 0 , 0, ct.c_int(0), 0, 0, 0
            self.__logger.log(cl=None, method=None, message="start simulation")
            while (bEnd.value == 0):
                if (time > 0):
                    if time%60==0: self.__logger.log(cl=None,method=None,message="time: {}. Vehicles created: {:>5}, not created {:>3}".format( str(datetime.timedelta(seconds=time+self.__timeSimSec[0])),VC,VNC))
                    squery = str(time) + ' < creation <= ' + str(time + 1)
                    dts = self.__demand.query(squery)
                    for index, row in dts.iterrows():
                        tc = ct.c_double(row.creation - time)
                        if (row.origin != row.destination):
                            ok = self.__symuflow_ddl.SymCreateVehicleWithRouteEx(row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8'), 1, tc,row.path.encode('UTF8'))
                            if (ok < 0):
                                self.__logger.warning(cl=None, method=None,message='Vehicle not created. Pos {}, creation: {}, origin: {}, destination: {}, type of vehicle: {}'.format(pos, row.creation, row.origin.encode('UTF8'),row.destination.encode('UTF8'),row.typeofvehicle.encode('UTF8')),doQuit=False)
                                VNC = VNC + 1
                            else:VC = VC + 1
                        else:
                            self.__logger.warning(cl=None, method=None,message='Vehicle not created. origin and destination are the same. Pos {}, creation: {}, origin: {}, destination: {}, type of vehicle: {}'.format(pos, row.creation, row.origin.encode('UTF8'),row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8')),doQuit=False)
                            VNC = VNC + 1
                ok = self.__symuflow_ddl.SymRunNextStepLiteEx(1, byref(bEnd))
                time += 1
                tmptime +=  1
                pos+=1
                if (bEnd.value != 0):
                    self.__symuflow_ddl.SymUnloadCurrentNetworkEx()
                    self.__logger.log(cl=None, method=None, message="Simulation end. Number of rows: {},vehicles created: {}, not created: {}".format(pos, VC,VNC))
            del self.__symuflow_ddl

    def run_01 (self,run):
        if run:
            self.__logger.log(cl=None, method=None, message="run simulation")
            startTime = [6, 30, 0]

            startTimeSec = startTime[0] * 60 * 60 + startTime[1] * 60 + startTime[2]
            time, tmptime, bEnd, period, VNC, VC = startTimeSec, 0, ct.c_int(0), 0, 0, 0

            self.__logger.log(cl=None, method=None, message="start simulation")
            print(self.__demand)
            while (bEnd.value == 0):
                # Vehicles creation (warning: vehicules with time creation between 0 and 1 are not generated)
                if (time > 0):
                    # print ("init {}".format(time))
                    squery = str(time) + ' < creation <= ' + str(time + 1)
                    dts = self.__demand.query(squery)
                    if time % 60 == 0: self.__logger.log(cl=None, method=None,
                                                  message="time: " + str(datetime.timedelta(seconds=time)))
                    for index, row in dts.iterrows():
                        tc = ct.c_double(row.creation - time)
                        # print (row)
                        if (row.origin != row.destination):
                            # print ("1 {}".format(time))

                            ok = self.__symuflow_lib.SymCreateVehicleEx(row.typeofvehicle.encode('UTF-8'),
                                                                 row.origin.encode('UTF-8'),
                                                                 row.destination.encode('UTF-8'), 1, tc)
                            # ok = symuvia_dll.SymCreateVehicleWithRouteEx(row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8'), 1, tc, row.path.encode('UTF8'))
                            if (ok < 0):
                                self.__logger.warning(cl=None, method=None,
                                               message='Vehicle not created. Id {}, creation: {}, origin: {}, destination: {}, type of vehicle: {}'.format(
                                                   row.id, row.creation, row.origin.encode('UTF8'),
                                                   row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8')),
                                               doQuit=False)
                                VNC = VNC + 1
                            else:
                                # logger.log(cl=None,method=None,message='Vehicle created. Id {}, creation: {}, origin: {}, destination: {}, type of vehicle: {}'.format(row.id,row.creation,row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8')))
                                VC = VC + 1
                        else:
                            self.__logger.warning(cl=None, method=None,
                                           message='Vehicle not created. origin and destination are the same. Id {}, creation: {}, origin: {}, destination: {}, type of vehicle: {}'.format(
                                               row.id, row.creation, row.origin.encode('UTF8'),
                                               row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8')),
                                           doQuit=False)
                            VNC = VNC + 1

                # print ("2 {}".format(time))

                # Time step calculation
                ok = self.__symuflow_lib.SymRunNextStepLiteEx(1, byref(bEnd))
                time = time + 1
                tmptime = tmptime + 1
                # print ("end {}".format(time))

                if (bEnd.value != 0):
                    self.__symuflow_lib.SymUnloadCurrentNetworkEx()
                    print(f'Microscopic simulation completed')
                    print(VC, ' ', VNC)

            del self.__symuflow_lib
