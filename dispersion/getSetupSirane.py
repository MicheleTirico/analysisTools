import sys
import pandas as pd
import geopandas as gpd
import toolbox

from analysisTools import tools
from scripts.parameters import parameters
from datetime import datetime, timedelta

class GetSetupSirane:
    def __init__(self, logger, parameters):
        self.__logger = logger
        self.__logger.logSep(cl=self, method=sys._getframe(), message="init get setup Sirane")
        if parameters != None: self.set_parameters(parameters)
        self.__listPols= ["pm10","no","no2"]

    def set_parameters(self, parameters):    self.__parameters = parameters

    def handleEmissions_copert(self,run,df_emi,gdf_links):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(),message="handle emissions from Copert")
            df_emi=df_emi[["nox_g","pm10_g","ID","hh"]]
            df_emi = df_emi.copy()
            gdf_links["length"]=gdf_links.length

            # compute no and no2
            df_emi["no_g"] = self.__parameters.perNO * df_emi["nox_g"]
            df_emi["no2_g"]=df_emi["nox_g"]-df_emi["no_g"]

            # group per hh
            df_emi = df_emi.groupby(by=["ID","hh"]).sum().reset_index()

            # compute per length
            df_emi=df_emi.merge(gdf_links[["ID","length"]],on="ID")
            for pol in self.__listPols: df_emi[pol+"_g/m"]=df_emi[pol+"_g"]/df_emi["length"]

            # compute per second
            for pol in self.__listPols: df_emi[pol + "_g/s"] = df_emi[pol + "_g"] / 3600

        return df_emi

    # DEPRECATED : it can be used when merge with a sirane network (not symuvia)
    def setEmissionsToLinksSirane(self,run,df_emi,listPathIn):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(),message="put emissions to links sirane")
            closest_links=pd.read_csv(listPathIn[0],sep=";")
            df_emi=df_emi.merge(closest_links[["id_sym","id_sir"]], left_on="ID",right_on="id_sym")
            df_emi=df_emi[['hh', 'nox_g/s', 'pm10_g/s', 'no_g/s','no2_g/s', 'id_sir']].groupby(by=["hh","id_sir"]).sum().reset_index()
            # tools.storeDataframe(logger=self.__logger,pathStore=listPathOut[0],df=df_emi)
        return df_emi

    def get_emi_rues(self,run,df_emi,listPathOut,name_id,list_id_network) : #,date_start_end):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="make emissions files. Edit emi_rues")
            listPath = []
            listDate = []
            for ts in sorted(set(df_emi["hh"])):
                time = [int(ts), 0, 0]
                nameFile = '{}_{:0>2}{:0>2}{:0>2}.dat'.format(parameters.emi_rues, time[0], time[1], time[2])
                self.__logger.log(cl=self, method=sys._getframe(), message="get file {}".format(nameFile))
                # get emi_rues files
                df1 = df_emi[df_emi["hh"] == ts][[name_id] + ["{}_g/s".format(_) for _ in self.__listPols]]
                df1 = df1[[name_id, "no2_g/s", "no_g/s", "pm10_g/s"]]
                df1 = df1.rename(columns={name_id: "Id", "no2_g/s": "NO2", "no_g/s": "NO", "pm10_g/s": "PM"})

                if list_id_network!=None:
                    self.__logger.log(cl=self, method=sys._getframe(), message="search links without emissions and set it at 0.0")
                    missing_ids = set(list_id_network) - set(df1["Id"])
                    new_rows = pd.DataFrame({"Id": list(missing_ids), "NO2": 0.0, "NO": 0.0, "PM":0.0})
                    df1 = pd.concat([df1, new_rows], ignore_index=True)
                    df1 = df1.set_index("Id").loc[list_id_network].reset_index()

                df1.to_csv("{}{}".format(listPathOut[0], nameFile), sep="\t", index=False)

    def make_emi_rues_constant(self,run,listPathOut,nameFile,list_id_network,val_emissions={"NO2":0.0,	"NO":0.0,	"PM":0.0}):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="make emissions files. create a file where values of emissions are constants")
            df1=pd.DataFrame({"Id": list_id_network,"NO2":  val_emissions["NO2"],"NO":  val_emissions["NO"],"PM":  val_emissions["PM"]})
            df1.to_csv("{}{}".format(listPathOut[0], nameFile), sep="\t", index=False)

    def append_evol_emis_trafic_vals(self,run,df,period_hh,period_day,nameFile,pathOut=None):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(),message="append emissions to evol emi. Period hh: {}, period day: {}".format(period_hh,period_day))
            listDate = []
            # date day
            start_date = datetime.strptime(period_day[0], "%d/%m/%Y")
            end_date = datetime.strptime(period_day[1], "%d/%m/%Y")
            date_list = [(start_date + timedelta(days=i)).strftime("%d/%m/%Y") for i in range((end_date - start_date).days + 1)]
            # date hh
            start_date_hh = datetime.strptime(period_hh[0], "%H:%M")
            end_date_hh = datetime.strptime(period_hh[1], "%H:%M")
            date_list_hh = [(start_date_hh + timedelta(hours=i)).strftime("%H:%M") for i in range((end_date_hh - start_date_hh).seconds // 3600 + 1)]
            # get row
            for hh in date_list_hh:
                for day in date_list:
                    date ="{} {}".format(day,hh)
                    listDate.append(date)
            # get df and concat
            df_evol = pd.DataFrame({"Date": listDate, "Fich_Emis": '{}{}'.format("EMISSIONS/EMIS_LIN/", nameFile)})
            df_evol=pd.concat((df,df_evol))
            # Sort DataFrame by date
            df_evol['Date'] = pd.to_datetime(df_evol['Date'], format='%d/%m/%Y %H:%M')
            df_evol = df_evol.sort_values(by='Date')
            df_evol['Date'] = df_evol['Date'].dt.strftime('%d/%m/%Y %H:%M')

            if pathOut !=None:  df_evol.to_csv(pathOut, sep="\t", index=False)
            return df_evol

    def get_mod_tempo_trafic(self,run,df_evol,listPathOut,Coeff_Modul=1.0):
        if run :
            self.__logger.log(cl=self, method=sys._getframe(),message="Get file mod temp trafic. Coeff modul: {}".format(Coeff_Modul))
            df_mod = pd.DataFrame({"Date": list(df_evol.Date), "Coeff_Modul": Coeff_Modul})
            df_mod.to_csv(listPathOut[0], sep="\t", index=False)

    def get_source_lin(self,run,pathOut):
        if run :
            self.__logger.log(cl=self, method=sys._getframe(),message="Get file source lin")
            with open(pathOut, 'w') as file:
                file.write("{}\t{}\n".format("Fich_Evol_Emis", "Fich_Modul"))
                file.write("{}\t{}".format("EMISSIONS/EMIS_LIN/Evol_Emis_Trafic.dat", "EMISSIONS/EMIS_LIN/Mod_Trafic.dat"))

    # DEPRECATED : olf method
    def make_vol_emi_traffic(self,run,df_emi,listPathOut,name_id,list_id_network,fill_hh_empty=False) : #,date_start_end):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="make emissions files")
            listPath = []
            listDate = []
            for ts in sorted(set(df_emi["hh"])):
                time = [int(ts), 0, 0]
                nameFile = '{}_{:0>2}{:0>2}{:0>2}.dat'.format(parameters.emi_rues, time[0], time[1], time[2])
                # get emi_rues files
                df1 = df_emi[df_emi["hh"] == ts][[name_id] + ["{}_g/s".format(_) for _ in self.__listPols]]
                df1 = df1[[name_id, "no2_g/s", "no_g/s", "pm10_g/s"]]
                df1 = df1.rename(columns={name_id: "Id", "no2_g/s": "NO2", "no_g/s": "NO", "pm10_g/s": "PM"})

                if list_id_network!=None:
                    self.__logger.logSep(cl=self, method=sys._getframe(), message="search links without emissions and set it at 0.0")
                    missing_ids = set(list_id_network) - set(df1["Id"])
                    new_rows = pd.DataFrame({"Id": list(missing_ids), "NO2": 0.0, "NO": 0.0, "PM":0.0})
                    df1 = pd.concat([df1, new_rows], ignore_index=True)
                    df1 = df1.set_index("Id").loc[list_id_network].reset_index()

                df1.to_csv("{}{}".format(listPathOut[0], nameFile), sep="\t", index=False)


                date = "01/01/2008 {:0>2}:{:0>2}".format(time[0], time[1])
                listDate.append(date)
                path = '{}{}'.format("EMISSIONS/EMIS_LIN/", nameFile)
                listPath.append(path)


            df_evol = pd.DataFrame({"Date": listDate, "Fich_Emis": listPath})

            df_evol.to_csv("{}{}".format(listPathOut[0], "Evol_Emis_Trafic.dat"), sep="\t", index=False)

            # df Mod_Temp_Trafic
            df_mod = pd.DataFrame({"Date": listDate, "Coeff_Modul": 1.0})
            df_mod.to_csv("{}{}".format(listPathOut[0], "Mod_Temp_Trafic.dat"), sep="\t", index=False)

            # source lin
            with open("{}{}".format(listPathOut[0], "Sources_Lin.dat"), 'w') as file:
                # Write each item on a new line
                file.write("{}\t{}\n".format("Fich_Evol_Emis", "Fich_Modul"))
                file.write("{}\t{}".format("EMISSIONS/EMIS_LIN/Evol_Emis_Trafic.dat", "EMISSIONS/EMIS_LIN/Mod_Trafic.dat"))


    def make_vol_emi_traffic_test(self,run,df_emi,listPathOut,name_id,list_id_network) : #,date_start_end):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="make emissions files")
            listPath = []
            listDate = []
            for ts in sorted(set(df_emi["hh"])):
                time = [int(ts), 0, 0]
                nameFile = '{}_{:0>2}{:0>2}{:0>2}.dat'.format(parameters.emi_rues, time[0], time[1], time[2])
                # get emi_rues files
                df1 = df_emi[df_emi["hh"] == ts][[name_id] + ["{}_g/s".format(_) for _ in self.__listPols]]
                df1 = df1[[name_id, "no2_g/s", "no_g/s", "pm10_g/s"]]
                df1 = df1.rename(columns={name_id: "Id", "no2_g/s": "NO2", "no_g/s": "NO", "pm10_g/s": "PM"})

                if list_id_network!=None:
                    self.__logger.logSep(cl=self, method=sys._getframe(), message="search links without emissions and set it at 0.0")
                    missing_ids = set(list_id_network) - set(df1["Id"])
                    new_rows = pd.DataFrame({"Id": list(missing_ids), "NO2": 0.0, "NO": 0.0, "PM":0.0})
                    df1 = pd.concat([df1, new_rows], ignore_index=True)
                    df1 = df1.set_index("Id").loc[list_id_network].reset_index()

                df1.to_csv("{}{}".format(listPathOut[0], nameFile), sep="\t", index=False)

                # get Evol_Emis_Trafic
                # start_date = datetime.strptime(date_start_end[0], "%d/%m/%Y")
                # end_date = datetime.strptime(date_start_end[1], "%d/%m/%Y")
                # date_list = [(start_date + timedelta(days=i)).strftime("%d/%m/%Y") for i in range((end_date - start_date).days + 1)]

                # for date in date_list: date += " {:0>2}:{:0>2}".format(time[0], time[1])

                date = "01/01/2008 {:0>2}:{:0>2}".format(time[0], time[1])
                listDate.append(date)
                path = '{}{}'.format("EMISSIONS/EMIS_LIN/", nameFile)
                listPath.append(path)

            df_evol = pd.DataFrame({"Date": listDate, "Fich_Emis": listPath})

            # sort by date
            # df_evol['Date'] = pd.to_datetime(df_evol['Date'])
            # df_evol['Date'] = df_evol['Date'].dt.strftime('%d/%m/%Y')
            # df_evol = df_evol.sort_values(by='Date')

            df_evol.to_csv("{}{}".format(listPathOut[0], "Evol_Emis_Trafic.dat"), sep="\t", index=False)

            # df Mod_Temp_Trafic
            df_mod = pd.DataFrame({"Date": listDate, "Coeff_Modul": 1.0})
            # df_mod['Date'] = pd.to_datetime(df_mod['Date'])
            # df_mod['Date'] = df_mod['Date'].dt.strftime('%d/%m/%Y')
            # df_mod = df_mod.sort_values(by='Date')
            # print(df_mod)
            df_mod.to_csv("{}{}".format(listPathOut[0], "Mod_Temp_Trafic.dat"), sep="\t", index=False)

            # source lin
            with open("{}{}".format(listPathOut[0], "Sources_Lin.dat"), 'w') as file:
                # Write each item on a new line
                file.write("{}\t{}\n".format("Fich_Evol_Emis", "Fich_Modul"))
                file.write("{}\t{}".format("EMISSIONS/EMIS_LIN/Evol_Emis_Trafic.dat", "EMISSIONS/EMIS_LIN/Mod_Trafic.dat"))

    def edit_data_input (self,run,path_data_input,line_input,new_line):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="edit donnees.dat file")
            with open(path_data_input, "r") as file:                lines = file.readlines()              # Read all lines
            lines[line_input-1] = new_line                  # Modify a specific line (e.g., change line 2, index 1)
            with open(path_data_input, "w") as file:  file.writelines(lines)            # Write back the modified content

    def make_sensors_input(self,run,listPathIn,listPathOut):
        if run :
            self.__logger.log(cl=self, method=sys._getframe(), message="make sensors files")
            gdf_sensors = gpd.read_file(listPathIn[0])

            gdf_sensors['X'] = gdf_sensors.geometry.x
            gdf_sensors['Y'] = gdf_sensors.geometry.y
            gdf_sensors['Z'] =  11.5
            gdf_sensors["Type"] = gdf_sensors.TYPE
            gdf_sensors['Fichier'] = "RECEPTEURS/Conc-CAPTEUR_Test.txt"

            gdf_sensors = gdf_sensors.rename(columns={"ID": "Id"}) # "id_sir": "Id"
            gdf_sensors = gdf_sensors[["Id", "X", "Y", "Z", "Type", "Fichier"]]
            gdf_sensors.to_csv("{}{}".format(listPathOut[0], "Recepteurs.dat"), sep="\t", index=False)

            # with open("{}{}".format(listPathOut[0], "test.dat"), 'w') as file:
            #     file.write("{}\t{}\t{}\t{}\t{}\n".format("Date","NO2","NO","O3","PM"))