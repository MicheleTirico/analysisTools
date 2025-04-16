from ctypes import byref
import ctypes as ct
import datetime

from analysisTools.tools import getTimeInSecFromHms


class Symuvia_run_with_rerouting:
    def __init__(self, symuvia):
        self.__symuvia = symuvia
        self.__logger=self.__symuvia.logger()
        self.__symuflow_ddl=self.__symuvia.symuflow_ddl()
        self.__demand=self.__symuvia.demand()
        self.__timeSimSec=self.__symuvia.timeSimSec()
        self.__symuvia_input=self.__symuvia.symuvia_input()
        self.__logger.log(cl=None, method=None, message="Init Symuvia simulation. Run with rerouting")

    # checkRouteInTimeSlot
    def run (self,run,withPath,listLinksToCheck,dynamicTimeSlot):
        if run:
            self.__logger.log(cl=None,method=None,message="run simulation with check routes")
            pos=0
            time,bEnd,VNC,VC=0, ct.c_int(0),0,0
            # print(self.__timeSimSec)
            while(bEnd.value==0):
                if(time>0):
                    # print(time)
                    if time%60==0:self.__logger.log(cl=None,method=None,message="time: {}. Vehicles created: {:>5}, not created {:>3}".format( str(datetime.timedelta(seconds=time+self.__timeSimSec[0])),VC,VNC))
                    query = str(time) + ' < creation <= ' + str(time+1)
                    dts = self.__demand.query(query)
                    for index, row in dts.iterrows():
                        tc = ct.c_double(row.creation-time)
                        if row.origin!=row.destination and (type(row.destination) is str):
                            path_default=row.path.encode("UTF8")
                            path=path_default
                            if time >= getTimeInSecFromHms(dynamicTimeSlot[0])-self.__timeSimSec[0] and time <=getTimeInSecFromHms(dynamicTimeSlot[1])-self.__timeSimSec[0]:
                                if self.__isSchoolsInPath(schools=listLinksToCheck,path=path_default.decode("UTF8").split(" ")):

                                # if any(_ in path_default.decode("UTF8").split(" ") for _ in listLinksToCheck):   # control
                                    self.__logger.log(cl=None,method=None,message="time: {}. Run Control for vehicle from {} to {}".format( str(datetime.timedelta(seconds=time+self.__timeSimSec[0])),row.origin,row.destination))
                                    shortPaths=self.__getPaths(originId=row.origin.encode('UTF8'),destinationId=row.destination.encode('UTF8'),typeVeh=row.typeofvehicle.encode('UTF8'),dbTime=tc,nbShortestPaths=10,memory=1000)

                                    if len(shortPaths)>0:
                                        path = " ".join(self.__get_path_outSchools(shortPaths=shortPaths,schools=listLinksToCheck)[0]).encode("UTF8")
                            else  :  pass # self.__logger.log(cl=None,method=None,message="time: {}. For vehicle from {} to {} no control needed".format( str(datetime.timedelta(seconds=time+self.__timeSimSec[0])),row.origin,row.destination))

                            # create vehicle
                            if withPath:    ok = self.__symuflow_ddl.SymCreateVehicleWithRouteEx(row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8'), 1, tc,path)
                            else :          ok = self.__symuflow_ddl.SymCreateVehicleEx(row.typeofvehicle.encode('UTF8'),row.origin.encode('UTF8'), row.destination.encode('UTF8'),1, tc)
                            if(ok<0):
                                self.__logger.warning(cl=None,method=None,message='Vehicle n. {:>3} not created. creation: {}, origin: {}, destination: {}, type of vehicle: {}'.format(pos,row.creation,row.origin, row.destination, row.typeofvehicle),doQuit=False)
                                VNC=VNC+1
                            else:
                                # self.__logger.log(cl=None,method=None,message='Vehicle n. {:>3} created. creation: {}, origin: {}, destination: {}, type of vehicle: {}'.format(pos,row.creation,row.origin, row.destination, row.typeofvehicle))
                                VC=VC+1
                        else:
                            self.__logger.warning(cl=None,method=None,message='Vehicle n. {:>3} not created (o=d). creation: {}, origin: {}, destination: {}, type of vehicle: {}'.format(pos,row.creation,row.origin, row.destination, row.typeofvehicle),doQuit=False)
                            VNC=VNC+1

                # Time step calculation
                ok = self.__symuflow_ddl.SymRunNextStepLiteEx(1, byref(bEnd))
                time=time+1
                pos+=1
                if (bEnd.value != 0):
                    self.__symuflow_ddl.SymUnloadCurrentNetworkEx()
                    self.__logger.log(cl=None, method=None, message="Simulation end. Number of rows: {},vehicles created: {}, not created: {}".format(pos, VC, VNC))
            del self.__symuflow_ddl

    def __isSchoolsInPath(self,schools,path):
        # print (schools)
        # print(type(schools))
        test = False
        i=0
        while test ==False and i < len(schools):
            v = schools[i]
            if v in path :
                test =True
            i+=1
        return test
    def __get_path_outSchools(self,shortPaths,schools):
        pos=[]
        i=0
        while i <len(shortPaths):
            for s in schools:
                if s in shortPaths[i] :
                    pos.append(i)
            i+=1
        return [item for idx, item in enumerate(shortPaths) if idx not in pos]

    def __getPaths(self,originId,destinationId,typeVeh,nbShortestPaths,memory,dbTime):
        pathLinks = (ct.POINTER(ct.c_char_p) * nbShortestPaths)()
        for i in range(nbShortestPaths): pathLinks[i] = (ct.c_char_p * memory)()  # Allocate memory for 10,000 links per path

        # Create an array of pointers to c_double
        pathCosts = (ct.POINTER(ct.c_double) * nbShortestPaths)()
        for i in range(nbShortestPaths): pathCosts[i] = (ct.c_double * 1)()  # Allocate memory for 1 cost per path

        # Convert to ctypes pointers
        pathLinks_ptr = ct.cast(ct.pointer(pathLinks), ct.POINTER(ct.POINTER(ct.POINTER(ct.c_char_p))))
        pathCosts_ptr = ct.cast(ct.pointer(pathCosts), ct.POINTER(ct.POINTER(ct.c_double)))

        # Call the function
        result = self.__symuflow_ddl.SymComputeRoutesEx(originId,destinationId,typeVeh,dbTime,nbShortestPaths,pathLinks_ptr,pathCosts_ptr)
        l=[]

        if result == 0:
            for a in range (nbShortestPaths):
                l2=[]
                test= True
                c=0
                while test :
                    try:v = pathLinks_ptr[0][a][c]
                    except ValueError:
                        self.__logger.warning(cl=None,method=None,message='No path from {} to {} founded ({}).'.format(originId,destinationId,"value Error"),doQuit=False)
                        return l
                    if v==None: test=False
                    else :
                        l2.append(v.decode("UTF8"))
                        c+=1
                l.append(l2)
        else:
            self.__logger.warning(cl=None,method=None,message='No path from {} to {} founded ({}).'.format(originId,destinationId,"no result"),doQuit=False)
        return l
