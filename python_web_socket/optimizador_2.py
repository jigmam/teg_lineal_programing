import re
import sys
import json
import numpy as np
from datetime import date, timedelta
import requests
import pandas as pd
from optimizer_class import pulp_solver
import psycopg2
from loguru import logger
import traceback
# pjson_demanda = sys.argv[1]
env = 'test'
if env == 'test':
  update_url = 'https://api-test.bitacore.com/v1/update-end-date'
  BC_DATABASE = {
      'database': 'backup23062022',
      'user': 'postgres',
      'password': 'postgres',
      'host': '127.0.0.1',
      'port': 5432,
  }
try:
    # Connecting to the database
    db_connection = psycopg2.connect(**BC_DATABASE)

    logger.debug("Connected to Database.")

except psycopg2.Error:
    logger.error(f"Error:\n{traceback.format_exc()}")
    sys.exit(50)



class optimizer_birds:
    def __init__(
      self, 
      demand:np.array,
      posture:np.array, 
      previos:np.array,
      date:np.array,
      lower_bound:int,
      upper_bound:int,
      algoritm:str,
      diference:int,
      optimizer:str,
      previos_days
      ):
      self.u = upper_bound
      self.l = lower_bound
      self.previos = previos
      self.demanda = demand
      self.posture = posture
      self.index_x = np.arange(len(demand)).tolist()
      self.index_y = np.arange(len(self.previos)).tolist()
      self.algoritm = algoritm
      self.diference = diference
      self.optimizer = optimizer
      self.date = date
      self.previos_days = previos_days

    def define_values(self):
      # try:
      self.lineal_program = pulp_solver("Minimicing")
      self.lineal_program.create_variable("lot_size",self.index_x,0,"integer")
      # self.lineal_program.create_variable("previos_lot_size",self.index_y,0,"integer")
      self.lineal_program.create_variable("binary_lot_size",self.index_x,0,"binary")
      # self.lineal_program.create_variable("binary_previos_lot_size",self.index_y,0,"binary")
      # self.lineal_program.create_variable("excess",self.index_x,0,"continuous")
      # self.lineal_program.create_variable("deficit",self.index_x,0,"continuous")
      self.lineal_program.create_objetive_function("lot_size")
      # except Exception as e:
      #   logger.error("Error in define_values")
      #   logger.error(e)

    def define_constraints(self):
      self.isalojamiento = np.array([])
      # today = date.today()
      # fecha = self.start_date.split("-")
      # last_posture = len(self.posture)
      # fechaAlojamiento = date(int(fecha[0]), int(fecha[1]), int(fecha[2]))
      # last_date = fechaAlojamiento - timedelta(days=last_posture*7)
      # diasprevios = int((fechaAlojamiento - last_date).days/7)
      # if(self.algoritm!="Sin alojamiento"):
      #     self.lineal_program.create_constraint_by_name_array(
      #       "previos_lot_size", 1, self.previos,
      #       1, "==", [*range(0, len(self.index_y), 1)]
      #     )
      #     self.isalojamiento = np.concatenate([self.isalojamiento, self.previos], axis=0)

      # else:
      #     self.lineal_program.create_constraint_by_name_array("previos_lot_size", 1, np.zeros(len(self.previos)),1,"==",[*range(0,len(self.index_y)-diasprevios)])
      
      if(self.algoritm!="Sin alojamiento"):
        self.lineal_program.create_constraint_by_name_array("lot_size", 1, self.previos, 1, "==", [*range(0, self.previos_days)])
        # self.lineal_program.create_constraint_by_name_array("lot_size",1,self.previos,1,"==",np.where(self.previos > 0)[0])
        self.lineal_program.create_constraint_by_name_name("binary_lot_size", self.l, "lot_size", 1, "<=", [*range(self.previos_days, len(self.index_x))])
        self.lineal_program.create_constraint_by_name_name("lot_size", 1, "binary_lot_size", self.u, "<=", [*range(self.previos_days, len(self.index_x))])
        self.isalojamiento = np.concatenate([self.isalojamiento, self.previos[0:self.previos_days],np.zeros(len(self.index_x) - self.previos_days)], axis=0)
      else:
        self.lineal_program.create_constraint_by_name_name("binary_lot_size",self.l,"lot_size",1,"<=",[*range(0,len(self.index_x))])
        self.lineal_program.create_constraint_by_name_name("lot_size",1,"binary_lot_size",self.u,"<=",[*range(0,len(self.index_x))])
        
      #   self.isalojamiento = np.concatenate([self.isalojamiento,np.zeros(len(self.index_x))],axis=0)
      # # else:
      # #   self.lineal_program.create_constraint_by_name_array("previos_lot_size",1,np.zeros(len(self.previos)),1,"==",[*range(0,len(self.index_y)-diasprevios)])
      # self.lineal_program.create_constraint_by_name_array_with_condition("previos_lot_size",1,self.previos,1,">=",np.where(self.previos >= self.l)[0][-diasprevios:])
      # self.lineal_program.create_constraint_by_name_array_with_condition("previos_lot_size",1,self.previos + self.u*np.ones(len(self.previos)),1,"<=",np.where(self.previos >= self.l)[0][-diasprevios:])

      # self.lineal_program.create_constraint_by_name_name("binary_previos_lot_size",self.l,"previos_lot_size",1,"<=",np.where(self.previos < self.l)[0][-diasprevios+len(np.where(self.previos >= self.l)[0][-diasprevios:]):])
      # self.lineal_program.create_constraint_by_name_name("previos_lot_size",self.u,"binary_previos_lot_size",1,"<=",np.where(self.previos < self.l)[0][-diasprevios+len(np.where(self.previos >= self.l)[0][-diasprevios:]):])
      
      

      self.posture = np.flip(self.posture)
      self.matriz = np.zeros((len(self.index_x),len(self.index_x)))

      
      for i in range(0,len(self.index_x)):
          for j in range(i,i + len(self.posture)):
            if (j < len(self.index_x)):
              self.matriz[j,i]=self.posture[j-i]
      self.production = np.dot(
        self.matriz,
        self.lineal_program.get_variable_by_name("lot_size")
      )
      if(self.optimizer=="1"):
        self.optimizer_by_diference()
      elif(self.optimizer=="2"):
        self.optimizer_by_satifation()
      elif(self.optimizer=="3"):
        self.optimizer_by_excess()

    def optimizer_by_diference(self):
      residue = np.roll(self.production - self.demanda, 1)
      residue[0] = 0
      # production =  (((self.production[self.demanda>0] + residue[self.demanda>0])/self.demanda[self.demanda>0])*100 - 100)[self.previos_days:]
      diference_min  =  (100 - self.diference)/100
      diference_max  =  (100 + self.diference)/100

      # self.lineal_program.make_constraint(production,self.diference*np.ones(len(production)),"<=",[*range(0, len(production))])
      # self.lineal_program.make_constraint(production ,-1*self.diference*np.ones(len(production)),">=",[*range(0, len(production))])
      self.lineal_program.make_constraint(
        self.production + residue,
        diference_min*self.demanda,">=",[*range(self.previos_days, len(self.index_x))])
      self.lineal_program.make_constraint(
        self.production + residue,
        diference_max*self.demanda,"<=",[*range(self.previos_days, len(self.index_x))])
      
    def optimizer_by_satifation(self):

      residue = np.roll(self.production - self.demanda, 1)
      residue[0] = 0
      type_list = [*range(self.previos_days, len(self.index_x))]
      if(self.algoritm=="Sin alojamiento"):
        type_list = np.where(self.demanda >= 0)[0]


      self.lineal_program.make_constraint(
        self.production + residue,
        self.demanda,">=",type_list)

    def optimizer_by_excess(self):
      residue = np.roll(self.production - self.demanda, 1)
      residue[0] = 0

      # self.lineal_program.make_constraint(
      #   self.lineal_program.get_variable_by_name("excess") - self.lineal_program.get_variable_by_name("deficit"),
      #   self.demanda,"==",np.where(self.demanda == 0)[0])
      self.lineal_program.make_constraint(
        self.production + residue +  self.lineal_program.get_variable_by_name("excess") - self.lineal_program.get_variable_by_name("deficit"),
        self.demanda,"==",np.where(self.demanda >= 0)[0])

    def solve_problem(self):
      self.define_values()
      self.define_constraints()
      logger.debug("init")
      self.lineal_program.solve_problem()
      
      lot_size = [x.varValue for x in self.lineal_program.get_variable_by_name("lot_size")]
      produc = np.dot(self.matriz,lot_size)
      dif = []
      difnro = []
      dif = produc.copy()
      
      
      totalresidue = produc - self.demanda
      residue = np.roll(totalresidue, 1)
      residue[0] = 0
      residue[residue < 0] = 0
      totalresidue[totalresidue < 0] = 0
      produc = produc + residue - totalresidue
      difnro = produc - self.demanda
      dif[self.demanda!=0] = (((produc[self.demanda!=0]-self.demanda[self.demanda!=0])/self.demanda[self.demanda!=0]))*100
      dif[self.demanda==0] = 0

      formatDays = np.array(['-']*(0))
      difnro = np.concatenate([formatDays,difnro],axis=0).tolist()
      dif = np.concatenate([formatDays,dif],axis=0).tolist()
      produc = np.concatenate([formatDays,produc],axis=0).tolist()
      self.demanda = np.concatenate([formatDays,self.demanda],axis=0).tolist()
      # result = np.concatenate([formatDays,result],axis=0).tolist()
      self.isalojamiento = np.concatenate([self.isalojamiento,formatDays],axis=0).tolist()
      result = pd.DataFrame(columns=["dates","diferenceNro","difference","production","demand","lot_size","isPrevios"])
      if(self.lineal_program.get_solution() == 1):
        result["dates"] = self.date.tolist()
        result["diferenceNro"] = difnro
        result["difference"] = dif
        result["production"] = produc
        result["demand"] = self.demanda
        result["lot_size"] = lot_size
        if len(self.isalojamiento) is 0:
          result["isPrevios"] = np.zeros(len(result["lot_size"]))
        else:
          result["isPrevios"] = self.isalojamiento
        logger.debug("factible")
      else:
        logger.error("infactible")
      result.to_csv("result.csv",index=False)
      result = result.loc[((result.index >= self.previos_days) | (result['lot_size'] > 0))]
      result = result.to_json(orient="records")
      parsed = json.loads(result)
      return json.dumps(parsed, indent=4)





def main(date_init,date_end,diference,algoritm,optimizer_id,breed_id,scenario_id):
  algoritm = algoritm
  diference = diference
  optimizer_id = optimizer_id
  scenario_id = scenario_id
  breed_id = breed_id
  date_init = date_init
  date_end = date_end
  DBcurveposture = f"""
    SELECT 
      theorical_performance 
    FROM public.txposturecurve 
    WHERE breed_id = {breed_id} 
    order by week ASC"""
  curve = pd.read_sql(DBcurveposture, db_connection)
  days_before = pd.Timestamp(date_init) - pd.DateOffset(weeks=len(curve))
  DBfindBreeding2 = f'''SELECT  a.execution_date,SUM(a.execution_quantity)::INTEGER as previos
                        FROM public.txhousingway_detail a 
                        LEFT JOIN txhousingway t on a.housing_way_id = t.housing_way_id
                        LEFT JOIN public.osshed b on a.shed_id = b.shed_id 
                        LEFT JOIN public.osfarm c on a.farm_id = c.farm_id 
                        LEFT JOIN oscenter e on a.center_id = e.center_id
                        LEFT JOIN osfarm f on a.executionfarm_id = f.farm_id
                        LEFT JOIN oscenter g on a.executioncenter_id = g.center_id
                        LEFT JOIN osshed h on a.executionshed_id = h.shed_id
                        WHERE 
                          t.scenario_id = {scenario_id} 
                          and a.execution_date BETWEEN '{days_before.strftime('%Y-%m-%d')}' and '{date_end}'
                          and t.breed_id = {breed_id}  
                          and a.incubator_plant_id <> 0 
                          and a.programmed_disable is null or false
                        GROUP BY a.execution_date ORDER BY a.execution_date ASC'''
  hossing = pd.read_sql(DBfindBreeding2, db_connection) 
  hossing["execution_date"] = pd.to_datetime(hossing["execution_date"])
  hossing.set_index("execution_date",inplace=True)
  print(hossing)
  
  urlGoalsResults = 'http://127.0.0.1:3000/scenario_param/getParameterGoal'
  res = requests.post(urlGoalsResults, 
    json={
      "scenario_id": scenario_id,
      "filter_breed" : [breed_id],
      "filter_stage" : []
      }
    )
  data_to_erp = pd.DataFrame(res.json()["data_to_erp"]).dropna()
  data_to_erp = data_to_erp[["fecha","value","breed_id","product_id"]]
  data_to_erp["breed_id"] = data_to_erp["breed_id"].astype(int)
  data_to_erp["product_id"] = data_to_erp["product_id"].astype(int)
  data_to_erp["fecha"]  = pd.to_datetime(data_to_erp.fecha, dayfirst=True)
  data_to_erp.rename(columns={"value":"demand"},inplace=True)
  data_to_erp.to_csv("data_to_erp.csv")
  data_to_erp = data_to_erp.loc[(data_to_erp.breed_id == breed_id) & (data_to_erp.product_id == 2)]
  data_to_erp = data_to_erp.drop_duplicates(subset=["fecha"], keep="last")
  data_to_erp.set_index("fecha", inplace=True)
  daterange = pd.date_range(start=days_before, end=pd.Timestamp(date_end),freq='D')
  data_to_erp = data_to_erp.reindex(daterange, fill_value=0)
  hossing = hossing.reindex(daterange, fill_value=0)
  hossing = pd.merge(hossing, data_to_erp, left_index=True, right_index=True)
  hossing = hossing.resample('W').agg({'previos': 'sum', 
                                 'demand': 'sum'})
  parameter = pd.read_sql(f"""
    SELECT 
      max_housing, 
      min_housing, 
      difference 
    FROM 
      public.md_optimizer_parameter
    where active = true and breed_id={breed_id}""", db_connection)
  print(optimizer_id)
  lower_bound = parameter["min_housing"][0]
  upper_bound = parameter["max_housing"][0]
  diference = parameter["difference"][0]
  print(lower_bound, upper_bound)
  optimizer = optimizer_birds(
      np.array(hossing["demand"]),
      np.array(curve["theorical_performance"]),
      np.array(hossing["previos"]),
      np.array(hossing.index.astype(str).to_list()),
      lower_bound,
      upper_bound,
      algoritm,
      diference,
      optimizer_id,
      len(hossing.loc[hossing.index < date_init])
  )
  
  return optimizer.solve_problem()




# print(main())