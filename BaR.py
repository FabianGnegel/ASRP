"""
Created on Mon Oct 11 15:48:41 2021

@author: fabiangnegel
"""

import cplex
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import math
import time

def readData(directory):
    comment_line = re.compile('#');
        
    # ------------------------
    # reading timedelta.dat
    # ------------------------
    
    file = open(directory+"/timedelta.dat", "r")
    timedelta_data = file.read()
    file.close()
    
    entries = re.split("\n+", timedelta_data)
    
    timedelta = 1
    
    for line in entries:
        if comment_line.search(line) == None:
            datas = re.split("\s+", line)
            if len(datas) == 2:
                ID,timedelta = datas
                timedelta = int(timedelta) # conversion from string to int
    
    
    # ---------------------
    # reading airplanes.dat
    # ---------------------
    
    
    file = open(directory+"/airplanes.dat", "r")
    airplanes_data = file.read()
    file.close()
    
    entries = re.split("\n+", airplanes_data)
    
    planeData = {}
    
    for line in entries:
        if comment_line.search(line) == None:
            datas = re.split("\s+", line)
            if len(datas) == 18:
                #print datas
                ID,cost,seats,origin,departure_min_fuel,departure_max_fuel,destination,arrival_min_fuel,arrival_max_fuel,required_fueltype,fuel,speed,max_fuel,empty_weight,add_turnover_time,reserve_fuel,contingence_ratio,pilot_weight = datas
                planeData[ID] = {'cost':float(cost),
                                    'seats':int(seats),
                                    'origin':origin,
                                    'departure_min_fuel':float(departure_min_fuel),
                                    'departure_max_fuel':float(departure_max_fuel),
                                    'destination':destination,
                                    'arrival_min_fuel':float(arrival_min_fuel),
                                    'arrival_max_fuel':float(arrival_max_fuel),
                                    'required_fueltype':int(required_fueltype),
                                    'fuel':float(fuel),
                                    'speed':float(speed),
                                    'max_fuel':float(max_fuel),
                                    'empty_weight':float(empty_weight),
                                    'add_turnover_time':int(add_turnover_time),
                                    'reserve_fuel':float(reserve_fuel),
                                    'contingence_ratio':float(contingence_ratio),
                                    'pilot_weight':float(pilot_weight)
                            }
    
    
    # --------------------
    # reading airports.dat
    # --------------------
    
    file = open(directory+"/airports.dat", "r")
    airports_data = file.read()
    file.close()
    
    entries = re.split("\n+", airports_data)
    
    airportData = {}
    
    for line in entries:
        if comment_line.search(line) == None:
            datas = re.split("\s+", line)
            if len(datas) == 2:
                #print datas
                ID, turnover_time = datas
                airportData[ID]={'turnover_time':int(turnover_time),'fuel':{}}
    
    
    # ------------------------
    # reading timedelta.dat
    # ------------------------
    
    file = open(directory+"/timedelta.dat", "r")
    timedelta_data = file.read()
    file.close()
    
    entries = re.split("\n+", timedelta_data)
    
    timedelta = 1
    
    for line in entries:
        if comment_line.search(line) == None:
          datas = re.split("\s+", line)
          if len(datas) == 2:
              ID,timedelta = datas
              timedelta = int(timedelta) # conversion from string to int
    
    # ---------------------
    # reading distances.dat
    # ---------------------
    
    file = open(directory+"/distances.dat", "r")
    distances_data = file.read()
    file.close()
    
    entries = re.split("\n+", distances_data)
    
    tripData = {p:{} for p in planeData}
    
    for p in planeData:
        for line in entries:
            if comment_line.search(line) == None:
                datas = re.split("\s+", line)
                if len(datas) == 3:
                    #print datas
                    origin, destination, dist = datas
                    if origin!=destination:
                        if not origin in tripData[p]:
                            tripData[p][origin]={}
                        tripData[p][origin][destination]={'distance':float(dist)}
    
    
    # -----------------
    # reading fuels.dat
    # -----------------
    
    
    file = open(directory+"/fuels.dat", "r")
    fuels_data = file.read()
    file.close()
    
    entries = re.split("\n+", fuels_data)
    
    for line in entries:
        if comment_line.search(line) == None:
            datas = re.split("\s+", line)
            if len(datas) == 3:
                airport, fuelID, isAvailable = datas
                airportData[airport]['fuel'][int(fuelID)] = int(isAvailable)
    
    
    
    # --------------------
    # reading requests.dat
    # --------------------
    
    
    file = open(directory+"/requests.dat", "r")
    requests_data = file.read()
    file.close()
    
    entries = re.split("\n+", requests_data)
    
    requestData = {}
    
    for line in entries:
        if comment_line.search(line) == None:
            datas = re.split("\s+", line)
            if len(datas) == 11:
                #print datas
                ID,origin,destination,earliest_departure_time,earliest_departure_day,latest_arrival_time,latest_arrival_day,passengers,weight,max_stops,max_detour = datas

                requestData[ID]={'origin':origin,
                                 'destination':destination,
                                 'earliest_departure_time':int(earliest_departure_time),
                                 'earliest_departure_day':int(earliest_departure_day),
                                 'latest_arrival_time':int(latest_arrival_time),
                                 'latest_arrival_day':int(latest_arrival_day),
                                 'passengers':int(passengers),
                                 'weight':float(weight),
                                 'earliest_departure': 1440 * (int(earliest_departure_day) - 1) +int(earliest_departure_time),
                                 'latest_arrival' : 1440 * (int(latest_arrival_day) - 1) + int(latest_arrival_time),
                                 'max_stops':int(max_stops),
                                 'max_detour':float(max_detour)
                    }
    
    
    # ------------------------
    # reading weightlimits.dat
    # ------------------------
    
    file = open(directory+"/weightlimits.dat", "r")
    weightlimits_data = file.read()
    file.close()
    
    entries = re.split("\n+", weightlimits_data)

    for line in entries:
        if comment_line.search(line) == None:
            datas = re.split("\s+", line)
            if len(datas) == 4:
                #print datas
                airport, airplane, max_takeoff_weight, max_landing_weight = datas
                if not 'max_takeoff_weight' in planeData[airplane]:
                    planeData[airplane]['max_takeoff_weight']={}
                    planeData[airplane]['max_landing_weight']={}
                if not 'max_takeoff_weight' in airportData[airport]:
                    airportData[airport]['max_takeoff_weight']={}
                    airportData[airport]['max_landing_weight']={}
                planeData[airplane]['max_takeoff_weight'][airport]=float(max_takeoff_weight)
                planeData[airplane]['max_landing_weight'][airport]=float(max_landing_weight)
                airportData[airport]['max_takeoff_weight'][airplane]=float(max_takeoff_weight)
                airportData[airport]['max_landing_weight'][airplane]=float(max_landing_weight)
    
    # --------------------------------
    # generating further instance data
    # --------------------------------
    
    # travelcost
    
    for p in planeData:
        for i in tripData[p]:
            for j in tripData[p][i]:
                tripData[p][i][j]['travelcost'] = tripData[p][i][j]['distance'] * planeData[p]['cost']
    
    
    for p in planeData:
        for i in tripData[p]:
            for j in tripData[p][i]:
                tripData[p][i][j]['travel_time'] = int( math.floor(tripData[p][i][j]['distance'] / ( (planeData[p]['speed'] /60)*5))*5)
    
    
    
    for i in airportData:
        airportData[i]['turnover_timesteps'] = {}
        for p in planeData:
            airportData[i]['turnover_timesteps'][p]= int(max(1,math.ceil((airportData[i]['turnover_time'] + planeData[p]['add_turnover_time']) / timedelta)))
    
    
    
    for p in planeData:
        for i in tripData[p]:
            for j in tripData[p][i]:
                tripData[p][i][j]['travel_timesteps'] = int(max(1,math.ceil(tripData[p][i][j]['travel_time'] / timedelta)))
    
    
    
    for p in planeData:
        for i in tripData[p]:
            for j in tripData[p][i]:
                tripData[p][i][j]['turnover_travel_timesteps'] = int(tripData[p][i][j]['travel_timesteps'] + airportData[i]['turnover_timesteps'][p])
    
    
    
    for i in airportData:
        airportData[i]['max_takeoff_payload'] = {}
        for p in planeData:
            airportData[i]['max_takeoff_payload'][p]= planeData[p]['max_takeoff_weight'][i] - planeData[p]['empty_weight'] - planeData[p]['reserve_fuel'] - planeData[p]['pilot_weight']
    
    
    for i in airportData:
        airportData[i]['max_landing_payload'] = {}
        for p in planeData:
            airportData[i]['max_landing_payload'][p]= planeData[p]['max_landing_weight'][i] - planeData[p]['empty_weight'] - planeData[p]['reserve_fuel'] - planeData[p]['pilot_weight']
    
    
    
    for p in planeData:
        for i in tripData[p]:
            for j in tripData[p][i]:
                tripData[p][i][j]['fuel_consumption'] = math.ceil(tripData[p][i][j]['travel_time'] * planeData[p]['fuel'] * planeData[p]['speed'] * planeData[p]['contingence_ratio']/60.0)
    
    
    for p in planeData:
        for i in tripData[p]:
            for j in tripData[p][i]:
                tripData[p][i][j]['max_trip_payload'] = min(airportData[i]['max_takeoff_payload'][p] + tripData[p][i][j]['fuel_consumption'],airportData[j]['max_landing_payload'][p])
    
    
    
    for p in planeData:
        for i in tripData[p]:
            for j in tripData[p][i]:
                tripData[p][i][j]['max_trip_fuel'] = planeData[p]['max_fuel'] - tripData[p][i][j]['fuel_consumption']- planeData[p]['reserve_fuel'] 
    
    
    
    
    
    for r in requestData:
        requestData[r]['earliest_departure_timesteps'] = int(math.ceil((requestData[r]['earliest_departure_time']+ 1440 * (requestData[r]['earliest_departure_day'] - 1)) / timedelta))
      
    
    for r in requestData:
        requestData[r]['latest_arrival_timesteps'] = int(math.floor((requestData[r]['latest_arrival_time']+ 1440 * (requestData[r]['latest_arrival_day'] - 1)) / timedelta))
      
    
    direct_flight_timesteps = {}
    
    direct_flight_timesteps = {}
    
    for p in planeData:
        for r in requestData:
            if planeData[p]['origin'] == requestData[r]['origin']:
                direct_flight_timesteps[p,r] = 0
            else:
                direct_flight_timesteps[p,r] = tripData[p][planeData[p]['origin']][requestData[r]['origin']]['turnover_travel_timesteps']
    
    max_refuel_flight_timesteps = {}
    
    
    for p in planeData:
        for r in requestData:
            max_refuel_flight_timesteps[p,r] = 0
            for i in airportData:
                if (airportData[i]['fuel'][planeData[p]['required_fueltype']] == 1 and i != planeData[p]['origin'] and i != requestData[r]['origin']):
                    aux = tripData[p][planeData[p]['origin']][i]['turnover_travel_timesteps'] + tripData[p][i][requestData[r]['origin']]['turnover_travel_timesteps']
                    max_refuel_flight_timesteps[p,r] = max(max_refuel_flight_timesteps[p,r],aux)
    
        #print "max_refuel_flight_timesteps plane ",p,", request ",r,": ",max_refuel_flight_timesteps[p,r]
    
    plane_min_timestep = {}
    
    for p in planeData:
        plane_min_timestep[p] = 99999
        
        for r in requestData:
            if requestData[r]['passengers'] <= planeData[p]['seats']:
                aux = requestData[r]['earliest_departure_timesteps']  - airportData[requestData[r]['origin']]['turnover_timesteps'][p] - max(direct_flight_timesteps[p,r], max_refuel_flight_timesteps[p,r])
                plane_min_timestep[p] = int(min(plane_min_timestep[p],aux))
                planeData[p]['plane_min_timestep'] = plane_min_timestep[p] 
    
      #print "plane ",p," min timestep: ",plane_min_timestep[p]
    
    
    
    for p in planeData:
        planeData[p]['plane_max_timestep']= 0
        
        for r in requestData:
            if requestData[r]['passengers'] <= planeData[p]['seats']:
                aux = requestData[r]['latest_arrival_timesteps']  + max(direct_flight_timesteps[p,r],max_refuel_flight_timesteps[p,r])
                planeData[p]['plane_max_timestep']  = int(max(planeData[p]['plane_max_timestep'],aux))
    
      #print "plane ",p," max timestep: ",plane_max_timestep[p]

    for r in requestData:
        requestData[r]['max_turnover_timesteps'] = 0
        for p in planeData:
            requestData[r]['max_turnover_timesteps']  = max(requestData[r]['max_turnover_timesteps'] , airportData[requestData[r]['origin']]['turnover_timesteps'][p])
    
   
    for i in airportData:
        airportData[i]['min_return_time'] = {}
        for p in planeData:
            min_out = 10000
            min_in = 10000
            for j in tripData[p][i]:
                if tripData[p][i][j]['turnover_travel_timesteps']  < min_out:
                    min_out = tripData[p][i][j]['turnover_travel_timesteps'] 
                
            for k in tripData[p]:
                if k != i and i in tripData[p][k].keys():
                    if tripData[p][k][i]['turnover_travel_timesteps']:
                        min_in = tripData[p][k][i]['turnover_travel_timesteps'] 
            airportData[i]['min_return_time'][p] = min_in+min_out
    for i in airportData:
        airportData[i]['min_refuel_trip'] = {p:100000 for p in planeData}
        for p in planeData:
            for j in tripData[p][i]:
                if airportData[j]['fuel'][planeData[p]['required_fueltype']] == 1:
                    airportData[i]['min_refuel_trip'][p] = min(airportData[i]['min_refuel_trip'][p] , tripData[p][i][j]['fuel_consumption'])

    """
    TRIP0 = {}
    
    for i,j in TRIP:
      if i != j:
        TRIP0[i,j] = TRIP[i,j]
    
    
    requestData_TRIP = {}
    
    for r in requestData:
      requestData_TRIP[r] = {}
    
      for i,j in TRIP:
        if i != requestData[r].request_arrival and j != requestData[r].request_departure:
          requestData_TRIP[r][i,j] = TRIP[i,j]
    
    
    requestData_TRIP0 = {}
    
    for r in requestData:
      requestData_TRIP0[r] = {}
    
      for i,j in TRIP0:
        if i != requestData[r].request_arrival and j != requestData[r].request_departure:
          requestData_TRIP0[r][i,j] = TRIP0[i,j]
    
    
    min_refuel_trip = {}
    
    for i in AIRPORT:
      for p in planeData:
        min_refuel_trip[i,p] = 99999
        for j in AIRPORT:
          if (i,j) in TRIP:
            if AIRPORT[j].fuel[planeData[p].required_fueltype] == '1':
              min_refuel_trip[i,p] = min(min_refuel_trip[i,p], fuelconsumption[i,j,p])
    
    
    plane_solution_arrival_time = {}
    plane_solution_arrival_timestep = {}
    
    for p,i,j,hh,mm in planeData_SOLUTION:
      plane_solution_arrival_time[p,i,j,hh,mm] = 60 * int(hh) + int(mm);
      plane_solution_arrival_timestep[p,i,j,hh,mm] = math.ceil(plane_solution_arrival_time[p,i,j,hh,mm] / timedelta)
    
    
    request_solution_arrival_time = {}
    request_solution_arrival_timestep = {}
    
    for p,r,i,j,hh,mm in requestData_SOLUTION:
      request_solution_arrival_time[p,r,i,j,hh,mm] = 60 * int(hh) + int(mm);
      request_solution_arrival_timestep[p,r,i,j,hh,mm] = math.ceil(request_solution_arrival_time[p,r,i,j,hh,mm] / timedelta)
      
      
    planeData_TIMESTEP = {}
    
    for p in planeData:
      planeData_TIMESTEP[p] = {}
      
      for t in range(plane_min_timestep[p], plane_max_timestep[p] + 1):
        planeData_TIMESTEP[p][t] = 1
        
    
    requestData_TIMESTEP = {}
    
    for r in requestData:
      max_turnover_timesteps = 0
      for p in planeData:
        max_turnover_timesteps = max(max_turnover_timesteps, turnover_timesteps[requestData[r].request_departure,p])
      
      requestData_TIMESTEP[r] = range(earliest_departure_timesteps[r] - max_turnover_timesteps, latest_arrival_timesteps[r] + 1)
    
    
    min_timestep = 99999
    max_timestep = 0
    
    for p in planeData:
      min_timestep = min(min_timestep, plane_min_timestep[p])
      max_timestep = max(max_timestep, plane_max_timestep[p])
      
    TIMESTEP = range(min_timestep, max_timestep + 1)
    
    
    TIMEFREEplaneDataSOLUTION = {}
    
    for p,i,j,hh,mm in planeData_SOLUTION:
      TIMEFREEplaneDataSOLUTION[p,i,j] = 1
      
    
    TIMEFREErequestDataSOLUTION = {}
    
    for p,r,i,j,hh,mm in requestData_SOLUTION:
      TIMEFREErequestDataSOLUTION[p,r,i,j] = 1
      
       
    
    multiple_arc_use = {}
    
    for p,i,j,hh,mm in planeData_SOLUTION:
      if (p,i,j) in multiple_arc_use:
        multiple_arc_use[p,i,j] += 1
      else:
        multiple_arc_use[p,i,j] = 1
    """
    return (airportData,tripData,requestData,planeData)

bigNum=1000000
eps = 1/bigNum

class Plane(object):
    def __init__(self,planeData,name,graph,tripData):
        self.name = name
        self.graph = graph
        self.cost = planeData['cost']
        self.seats = planeData['seats']
        self.origin = planeData['origin']
        self.departure_min_fuel = planeData['departure_min_fuel']
        self.departure_max_fuel = planeData['departure_max_fuel']
        self.destination = planeData['destination']
        self.arrival_min_fuel = planeData['arrival_min_fuel']
        self.arrival_max_fuel = planeData['arrival_max_fuel']
        self.required_fueltype = planeData['required_fueltype']
        self.fuel = planeData['fuel']
        self.speed = planeData['speed']
        self.max_fuel = planeData['max_fuel']
        self.empty_weight = planeData['empty_weight']
        self.add_turnover_time = planeData['add_turnover_time']
        self.reserve_fuel = planeData['reserve_fuel']
        self.contingence_ratio = planeData['contingence_ratio']
        self.pilot_weight = planeData['pilot_weight']
        self.max_takeoff_weight = planeData['max_takeoff_weight']
        self.max_landing_weight = planeData['max_landing_weight']
        self.plane_min_timestep = planeData['plane_min_timestep']
        self.plane_max_timestep = planeData['plane_max_timestep']
        self.createConstraints(self.graph.modelHandler,tripData)
    def createConstraints(self,modelHandler,tripData):
        names = [f"start_{self.name}"]
        thevars = []
        thecoefs = []
        pairs= [cplex.SparsePair(thevars,thecoefs)]
        rhs= [1.0]
        senses = ["E"]
        self.startConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)
        if self.graph.addMinFuelStopCuts and (self.origin == self.destination or self.departure_max_fuel - tripData[self.name][self.origin][self.destination]['fuel_consumption']) < self.arrival_min_fuel:
            names = [f"minFuelStop_{self.name}"]
            thevars = []
            thecoefs = []
            pairs= [cplex.SparsePair(thevars,thecoefs)]
            rhs= [1.0]
            senses = ["G"]
            self.minFuelStopCuts = modelHandler.addConstraints(names,pairs,senses,rhs)
            names = [f"minFuelStop2_{self.name}"]
            thevars = []
            thecoefs = []
            pairs= [cplex.SparsePair(thevars,thecoefs)]
            rhs= [1.0]
            senses = ["G"]
            self.minFuelStopCuts2 = modelHandler.addConstraints(names,pairs,senses,rhs)



class Request():
    def __init__(self,name,requestData,graph,tripData):
        self.name = name
        self.graph = graph
        self.origin = requestData['origin']
        self.destination = requestData['destination']
        self.earliest_departure_time = requestData['earliest_departure_time']
        self.earliest_departure_day = requestData['earliest_departure_day']
        self.latest_arrival_time =requestData['latest_arrival_time']
        self.latest_arrival_day = requestData['latest_arrival_day']
        self.passengers = requestData['passengers']
        self.weight = requestData['weight']
        self.earliest_departure = requestData['earliest_departure']
        self.latest_arrival = requestData['latest_arrival']
        self.earliest_departure_timesteps = requestData['earliest_departure_timesteps']
        self.latest_arrival_timesteps = requestData['latest_arrival_timesteps']
        self.max_stops = requestData['max_stops']

        self.max_detour = requestData['max_detour']
        self.max_detour = (1 +self.max_detour) * tripData['0'][self.origin][self.destination]['distance']
        self.max_turnover_timesteps = requestData['max_turnover_timesteps']
        self.createConstraints(self.graph.modelHandler)
        
        return        
    def createConstraints(self,modelHandler):
        names = [f"serve_{self.name}"]
        thevars = []
        thecoefs = []
        pairs= [cplex.SparsePair(thevars,thecoefs)]
        rhs= [1.0]
        senses = ["E"]
        self.serveConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)
        names = [f"stops_{self.name}"]
        thevars = []
        thecoefs = []
        pairs= [cplex.SparsePair(thevars,thecoefs)]
        rhs= [self.max_stops+1]
        senses = ["L"]
        self.stopsConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)
        names = [f"detour_{self.name}"]
        thevars = []
        thecoefs = []
        pairs= [cplex.SparsePair(thevars,thecoefs)]
        rhs= [self.max_detour]
        senses = ["L"]
        self.detourConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)


class Airport():
    def __init__(self,name,airportData,graph):
        self.graph = graph
        self.requests = graph.requests
        self.modelHandler = graph.modelHandler
        self.planes = graph.planes
        self.trips = graph.trips
        self.turnover_time = airportData['turnover_time']
        self.turnover_timesteps = airportData['turnover_timesteps']
        self.fuel = airportData['fuel']
        self.max_takeoff_weight = airportData['max_takeoff_weight']
        self.max_landing_weight = airportData['max_landing_weight']
        self.turnover_timesteps = airportData['turnover_timesteps']
        self.max_takeoff_payload = airportData['max_takeoff_payload']
        self.max_landing_payload = airportData['max_landing_payload']
        self.min_return_time = airportData['min_return_time']
        self.min_refuel_trip = airportData['min_refuel_trip']
        self.name=name
        self.createConstraints()
        self.copyList = {}
        for p,plane in self.planes.items():
            self.copyList[p]=[airportCopy(self,plane,0,1)]
    def createVariables(self):
        return
    def createConstraints(self):
        modelHandler = self.modelHandler
        self.maxVisitsConstraints1 = []
        self.maxVisitsConstraints2 = []
        if self.graph.addMaxVisitCuts == 1 and sum([self.fuel[self.planes[p].required_fueltype] for p in self.planes]) == 0:
            names = [f"max_visits1_{self.name}"]
            thevars = []
            thecoefs = []
            pairs= [cplex.SparsePair(thevars,thecoefs)]
            rhs= [sum([1 for r,req in self.requests.items() if req.origin == self.name or req.destination == self.name ])+sum([1 for p,pla in self.planes.items() if pla.origin == self])]
            senses = ["L"]
            self.maxVisitsConstraints1 = modelHandler.addConstraints(names,pairs,senses,rhs)
            names = [f"max_visits2_{self.name}"]
            thevars = []
            thecoefs = []
            pairs= [cplex.SparsePair(thevars,thecoefs)]
            rhs= [sum([1 for r,req in self.requests.items() if req.origin == self.name or req.destination == self.name ])+sum([1 for p,pla in self.planes.items() if pla.destination == self])]
            senses = ["L"]
            self.maxVisitsConstraints2 = modelHandler.addConstraints(names,pairs,senses,rhs)
    def addCopy(self,p):
        self.copyList[p][-1].isHighestIndex=0
        #add the constraints since it is not highest anymore
        self.copyList[p].append(airportCopy(self,self.planes[p],len(self.copyList[p]),1))


class airportCopy():
    def __init__(self,airportObject,planeObject,copyID,isHighestIndex):
        self.plane=planeObject
        self.planeID=planeObject.name
        self.copyID=copyID
        self.airport=airportObject
        self.name = airportObject.name
        self.isHighestIndex=isHighestIndex
        self.departuringRequests=[]
        self.arrivingRequests=[]
        self.ingoingTrips = []
        self.outgoingTrips = []
        self.varsForNext = []
        self.ingoingYVars = []
        self.outgoingYVars = []
        self.ingoingXVars = {r:[] for r in self.airport.graph.requests}
        self.outgoingXVars = {r:[] for r in self.airport.graph.requests}
        self.createVariables()
        self.addToExistingConstraints()
        self.createConstraints()
    def createConstraints(self):
        requests = self.airport.graph.requests
        modelHandler = self.airport.graph.modelHandler
        names = ["yFlow"+self.getNameAppendix()]
        thevars = self.ydepVarIndices+self.yarrVarIndices
        thecoefs= [1]*len(self.ydepVarIndices)+[-1]*len(self.yarrVarIndices)
        pairs= [cplex.SparsePair(thevars,thecoefs)]
        senses = ["E"]
        rhs = [0]
        self.yFlowConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)
        
        self.xFlowConstraints = {}
        for r in requests:
            names = ["xFlow"+self.getNameAppendix()+f"_{r}"]
            thevars = self.xdepVarIndices[r]+self.xarrVarIndices[r]
            thecoefs= [1]*len(self.xdepVarIndices[r])+[-1]*len(self.xarrVarIndices[r])
            pairs= [cplex.SparsePair(thevars,thecoefs)]
            senses = ["E"]
            rhs = [0]
            self.xFlowConstraints[r] = modelHandler.addConstraints(names,pairs,senses,rhs)
        names = ["tFlow"+self.getNameAppendix()]
        thevars = self.tdepVarIndices+self.tarrVarIndices
        thecoefs= [1]*len(self.tdepVarIndices)+[-1]*len(self.tarrVarIndices)
        pairs= [cplex.SparsePair(thevars,thecoefs)]
        senses = ["L"]
        rhs = [0]
        self.tFlowConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)
        names = ["fFlow"+self.getNameAppendix()]
        thevars = self.fdepVarIndices+self.farrVarIndices
        thecoefs= [1]*len(self.fdepVarIndices)+[-1]*len(self.farrVarIndices)
        pairs= [cplex.SparsePair(thevars,thecoefs)]
        if self.airport.fuel[self.plane.required_fueltype]==1:
            senses = ["L"]
        else:
            senses = ["E"]
        rhs = [0]
        self.fFlowConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)
        
        if self.plane.origin == self.name:
            names = ["setFDep1"+self.getNameAppendix()]
            thevars = self.ydepVarIndices+self.fdepVarIndices
            thecoefs= [-self.plane.departure_min_fuel]*len(self.ydepVarIndices)+[1]*len(self.fdepVarIndices)
            pairs= [cplex.SparsePair(thevars,thecoefs)]
            senses = ["G"]
            rhs = [0]
            self.setFDep1Constraints = modelHandler.addConstraints(names,pairs,senses,rhs)
            names = ["setFDep2"+self.getNameAppendix()]
            thevars = self.ydepVarIndices+self.fdepVarIndices
            thecoefs= [-self.plane.departure_max_fuel]*len(self.ydepVarIndices)+[1]*len(self.fdepVarIndices)
            pairs= [cplex.SparsePair(thevars,thecoefs)]
            senses = ["L"]
            rhs = [0]
            self.setFDep2Constraints = modelHandler.addConstraints(names,pairs,senses,rhs)
            names = ["settdep1"+self.getNameAppendix()]
            thevars = self.ydepVarIndices+self.tdepVarIndices
            thecoefs= [-self.plane.plane_min_timestep]*len(self.ydepVarIndices)+[1]*len(self.tdepVarIndices)
            pairs= [cplex.SparsePair(thevars,thecoefs)]
            senses = ["G"]
            rhs = [0]
            self.settdep1Constraints = modelHandler.addConstraints(names,pairs,senses,rhs)
            #names = ["settdep2"+self.getNameAppendix()]
            #thevars = self.ydepVarIndices+self.tdepVarIndices
            #thecoefs= [-self.plane.plane_min_timestep]*len(self.ydepVarIndices)+[1]*len(self.tdepVarIndices)
            #pairs= [cplex.SparsePair(thevars,thecoefs)]
            #senses = ["L"]
            #rhs = [0]
            #self.settdep2Constraints = modelHandler.addConstraints(names,pairs,senses,rhs)
        if self.plane.destination == self.name:
            names = ["setFarr1"+self.getNameAppendix()]
            thevars = self.yarrVarIndices+self.farrVarIndices
            thecoefs= [-self.plane.arrival_min_fuel]*len(self.yarrVarIndices)+[1]*len(self.farrVarIndices)
            pairs= [cplex.SparsePair(thevars,thecoefs)]
            senses = ["G"]
            rhs = [0]
            self.setFArr1Constraints = modelHandler.addConstraints(names,pairs,senses,rhs)
            names = ["setFarr2"+self.getNameAppendix()]
            thevars = self.yarrVarIndices+self.farrVarIndices
            thecoefs= [-self.plane.arrival_max_fuel]*len(self.yarrVarIndices)+[1]*len(self.farrVarIndices)
            pairs= [cplex.SparsePair(thevars,thecoefs)]
            senses = ["L"]
            rhs = [0]
            self.setFArr2Constraints = modelHandler.addConstraints(names,pairs,senses,rhs)
            
        if self.copyID != 0:
            names = ["boundByPrevious"+self.getNameAppendix()]
            thevars = self.airport.copyList[self.plane.name][self.copyID-1].varsForNext+[]
            thecoefs= len(thevars)*[-5]
            pairs= [cplex.SparsePair(thevars,thecoefs)]
            senses = ["L"]
            rhs = [0]
            self.boundByPreviousConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)
            #constraint for predecessor copy
            names = ["max1ingoing"+self.airport.copyList[self.plane.name][self.copyID-1].getNameAppendix()]
            thevars = self.airport.copyList[self.plane.name][self.copyID-1].ingoingYVars+[]
            thecoefs= len(thevars)*[1]
            pairs= [cplex.SparsePair(thevars,thecoefs)]
            senses = ["L"]
            if self.plane.origin == self.name:
                rhs = [0]
            else:
                rhs = [1]
            self.airport.copyList[self.plane.name][self.copyID-1].max1ingoingConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)
            #constraint for predecessor copy
            names = ["max1outgoing"+self.airport.copyList[self.plane.name][self.copyID-1].getNameAppendix()]
            thevars = self.airport.copyList[self.plane.name][self.copyID-1].outgoingYVars+[]
            thecoefs= len(thevars)*[1]
            pairs= [cplex.SparsePair(thevars,thecoefs)]
            senses = ["L"]
            rhs = [1]
            self.airport.copyList[self.plane.name][self.copyID-1].max1outgoingConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)

        #trigger maximal one in/outgoing if not newest#reminder that new variables have to be registered in this constraint
        #trigger bound by previous for last one if not first#reminder that new variables have to be registered in this constraint
        #trigger no return to start
        return
    def createVariables(self):
        modelHandler = self.airport.modelHandler
        requests = self.airport.requests
        planes = self.airport.planes
        self.ydepVarIndices = []
        self.fdepVarIndices = []
        self.tdepVarIndices = []
        if self.plane.origin == self.name:
            names = ["ydep"+self.getNameAppendix()]
            obj=[ 0] 
            lb = [0]
            ub=[1]
            types = ["B"]
            self.ydepVarIndices = modelHandler.addVariables(names,obj,lb,ub,types)
            if self.copyID != 0:
                for branch in self.airport.graph.modelHandler.branchDictionary[self.airport.copyList[self.plane.name][self.copyID-1].ydepVarIndices[0]]:
                    branch.vars.append(self.ydepVarIndices[0])
            names = ["fdep"+self.getNameAppendix()]
            obj=[ 0] 
            lb = [0]
            ub=[bigNum]
            types = ["C"]
            self.fdepVarIndices = modelHandler.addVariables(names,obj,lb,ub,types)
            names = ["tdep"+self.getNameAppendix()]
            obj=[ 0] 
            lb = [0]
            ub=[self.plane.plane_max_timestep]
            types = ["C"]
            self.tdepVarIndices = modelHandler.addVariables(names,obj,lb,ub,types)
        self.xdepVarIndices={}
        self.xarrVarIndices={}
        for r in requests:
            if requests[r].origin == self.name:
                names = ["xdep"+self.getNameAppendix()+f"_{r}"]
                obj=[ 0] 
                lb = [0]
                ub=[1]
                types = ["B"]
                self.xdepVarIndices[r] = list(modelHandler.addVariables(names,obj,lb,ub,types))
                if self.copyID != 0:
                    for branch in self.airport.graph.modelHandler.branchDictionary[self.airport.copyList[self.plane.name][self.copyID-1].xdepVarIndices[r][0]]:
                        branch.vars.append(self.xdepVarIndices[r][0])
            else:
                self.xdepVarIndices[r] = []
            if requests[r].destination == self.name:
                names = ["xarr"+self.getNameAppendix()+f"_{r}"]
                obj=[ 0] 
                lb = [0]
                ub=[1]
                types = ["B"]
                self.xarrVarIndices[r] = list(modelHandler.addVariables(names,obj,lb,ub,types))
                if self.copyID != 0:
                    for branch in self.airport.graph.modelHandler.branchDictionary[self.airport.copyList[self.plane.name][self.copyID-1].xarrVarIndices[r][0]]:
                        branch.vars.append(self.xarrVarIndices[r][0])
            else:
                self.xarrVarIndices[r]=[]
        self.yarrVarIndices = []
        self.farrVarIndices = []
        self.tarrVarIndices = []
        
        if planes[self.planeID].destination == self.name:   
            names = ["yarr"+self.getNameAppendix()]
            obj=[ 0] 
            lb = [0]
            ub=[1]
            types = ["B"]
            self.yarrVarIndices = modelHandler.addVariables(names,obj,lb,ub,types)
            if self.copyID != 0:
                for branch in self.airport.graph.modelHandler.branchDictionary[self.airport.copyList[self.plane.name][self.copyID-1].yarrVarIndices[0]]:
                    branch.vars.append(self.yarrVarIndices[0])
            names = ["farr"+self.getNameAppendix()]
            obj=[ 0] 
            lb = [0]
            ub=[bigNum]
            types = ["C"]
            self.farrVarIndices = modelHandler.addVariables(names,obj,lb,ub,types)
            names = ["tarr"+self.getNameAppendix()]
            obj=[ 0] 
            lb = [0]
            ub=[self.plane.plane_max_timestep]
            types = ["C"]
            self.tarrVarIndices = modelHandler.addVariables(names,obj,lb,ub,types)
        return
    def addToExistingConstraints(self):
        modelHandler = self.airport.graph.modelHandler
        requests = self.airport.graph.requests
        for r in requests:
            if requests[r].origin == self.name:
                #print(f"adding {self.xdepVarIndices[r][0]} to {r}")
                modelHandler.changeConstraintCoefficient(requests[r].serveConstraints[0],self.xdepVarIndices[r][0],1)
        if self.airport.name == self.plane.origin:
            modelHandler.changeConstraintCoefficient(self.plane.startConstraints[0],self.ydepVarIndices[0],1)
        if self.airport.graph.addMinFuelStopCuts:
            if self.name == self.plane.destination and self.airport.fuel[self.plane.required_fueltype]==1:
                modelHandler.changeConstraintCoefficient(self.plane.minFuelStopCuts2[0],self.yarrVarIndices[0],1.0)
        return
    def addDeparturingRequest(self,request):
        self.departuringRequests.append(request)
    def addArrivingRequest(self,request):
        self.arrivingRequests.append(request)
    def getNameAppendix(self):
        return f"_{self.airport.name}_{self.copyID}_{self.planeID}"


class Trip():
    def __init__(self,originObject,destinationObject,planeObject,tripData,graph):
        self.origin = originObject.name
        self.destination = destinationObject.name
        self.originObject = originObject
        self.destinationObject = destinationObject
        self.plane = planeObject
        self.planeName = planeObject.name
        self.graph = graph
        self.requests = graph.requests
        self.modelHandler = graph.modelHandler
        self.planes = graph.planes
        self.trips = graph.trips
        self.distance = tripData['distance']
        self.travelcost = tripData['travelcost']
        self.traveltime = tripData['travel_time']
        self.travel_timesteps = tripData['travel_timesteps']
        self.turnover_travel_timesteps = tripData['turnover_travel_timesteps']
        self.max_trip_payload = tripData['max_trip_payload']
        self.max_trip_fuel = tripData['max_trip_fuel']
        self.fuel_consumption = tripData['fuel_consumption']
        self.initializeCopies()
    def initializeCopies(self):
        self.copyList=[TripCopy(self.originObject.copyList[self.planeName][0],self.destinationObject.copyList[self.planeName][0],self)]
    def createVariables(self):
        return
    def initilizeConstraints(self):
        return
    def addCopy(self,originObject,destinationObject,predecessor=0):
        self.copyList.append(TripCopy(originObject,destinationObject,self,predecessor))

class TripCopy():
    def __init__(self,originObject,destinationObject,trip,predecessor=0):
        self.trip=trip
        self.origin=originObject.name
        self.originObject = originObject
        self.originObject.outgoingTrips.append(self)
        self.destination = destinationObject.name
        self.destinationObject = destinationObject
        self.destinationObject.ingoingTrips.append(self)
        self.plane = trip.plane
        self.planeName= self.plane.name
        self.originCopyID = originObject.copyID
        self.destinationCopyID=destinationObject.copyID
        self.createVariables(predecessor)
        self.createConstraints()
        self.addToExistingConstraints()
    def createConstraints(self):
        modelHandler = self.trip.graph.modelHandler
        planes = self.trip.graph.planes
        requests = self.trip.graph.requests
        thevars = list(self.yVarIndices)
        thecoefs = [-self.plane.seats]
        for r in requests:
            thevars += self.xVarIndices[r]
            thecoefs += [requests[r].passengers]
        names = ["seatlimit"+self.getNameAppendix()]
        pairs = [cplex.SparsePair(thevars,thecoefs)]
        senses = ['L']
        rhs=[0]
        self.seatCapacityConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)
        names  = ["noflight_nofuel" + self.getNameAppendix()]
        thevars = self.fVarIndices+self.yVarIndices
        thecoefs = [1.0,-self.trip.max_trip_fuel]
        pairs = [cplex.SparsePair(thevars,thecoefs)]
        senses = ["L"]
        rhs = [0.0]
        self.noflightnoFuelConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)
        #fuel capacity constraints
        names  = ["noFlightnoTime" + self.getNameAppendix()]
        thevars = self.tVarIndices+self.yVarIndices
        thecoefs = [1.0,-self.trip.planes[self.planeName].plane_max_timestep]
        pairs = [cplex.SparsePair(thevars,thecoefs)]
        senses = ["L"]
        rhs = [0.0]
        self.noflightnoTimeConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)
        names  = ["aFlightaTime" + self.getNameAppendix()]
        thevars = self.tVarIndices+self.yVarIndices
        thecoefs = [1.0,-self.trip.planes[self.planeName].plane_min_timestep]
        pairs = [cplex.SparsePair(thevars,thecoefs)]
        senses = ["G"]
        rhs = [0.0]
        self.aFlightaTimeConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)
        if self.destinationObject.airport.fuel[self.plane.required_fueltype] != 1:
            names  = ["aFlightaFuel" + self.getNameAppendix()]
            thevars = self.fVarIndices+self.yVarIndices
            thecoefs = [-1.0,self.destinationObject.airport.min_refuel_trip[self.planeName]]
            pairs = [cplex.SparsePair(thevars,thecoefs)]
            senses = ["L"]
            rhs = [0.0]
            self.aFlightaFuelConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)
        names  = ["weightlimit" + self.getNameAppendix()]
        thevars = []+self.yVarIndices
        thecoefs = [-self.trip.max_trip_payload]
        for r in requests:
            thevars += self.xVarIndices[r]
            thecoefs += [requests[r].weight]
        pairs = [cplex.SparsePair(thevars,thecoefs)]
        senses = ["L"]
        rhs = [0.0]
        self.weightlimitConstraints = modelHandler.addConstraints(names,pairs,senses,rhs)
        self.timeWindowConstraints = []
        for r in requests:
            names  = ["timeWindow1" + self.getNameAppendix()+f"_{r}"]
            thevars = self.tVarIndices+ self.xVarIndices[r]
            thecoefs = [1,-planes[self.planeName].plane_max_timestep]
            pairs = [cplex.SparsePair(thevars,thecoefs)]
            senses = ["G"]
            rhs = [requests[r].earliest_departure_timesteps-planes[self.planeName].plane_max_timestep - self.originObject.airport.turnover_timesteps[self.plane.name]]
            self.timeWindowConstraints += modelHandler.addConstraints(names,pairs,senses,rhs)
            
            names  = ["timeWindow2" + self.getNameAppendix()+f"_{r}"]
            thevars = self.tVarIndices+self.xVarIndices[r]+ self.yVarIndices
            thecoefs = [1]+[2*planes[self.planeName].plane_max_timestep]+[-planes[self.planeName].plane_max_timestep]
            pairs = [cplex.SparsePair(thevars,thecoefs)]
            rhs = [requests[r].latest_arrival_timesteps+planes[self.planeName].plane_max_timestep - self.trip.turnover_travel_timesteps]
            senses=["L"]
            self.timeWindowConstraints += modelHandler.addConstraints(names,pairs,senses,rhs)
            
        #cutting planes
        
        self.mustHaveRequest1Constraints = []
        if self.trip.graph.mustServeRequestCuts:
            if self.destinationObject.airport.name != self.plane.destination and self.destinationObject.airport.fuel[self.plane.required_fueltype] != 1:
                thevars = list(self.yVarIndices)
                thecoefs = [1.0]
                for r in requests:
                    thevars += self.xVarIndices[r]
                    thecoefs += [-1.0]
                for outgoingTrip in self.destinationObject.outgoingTrips:
                    for r in requests:
                        if self.destinationObject.airport.name == requests[r].origin:
                            thevars += outgoingTrip.xVarIndices[r]
                            thecoefs += [-1.0]
                names = ["mustHaveRequest1"+self.getNameAppendix()]
                pairs = [cplex.SparsePair(thevars,thecoefs)]
                senses = ['L']
                rhs=[0]
                self.mustHaveRequest1Constraints = modelHandler.addConstraints(names,pairs,senses,rhs)
            self.mustHaveRequest2Constraints = []
        if self.trip.graph.mustServeRequestCuts:
            if (not (self.originObject.airport.name == self.plane.origin and self.originCopyID == 0)) and self.originObject.airport.fuel[self.plane.required_fueltype] != 1:
                thevars = list(self.yVarIndices)
                thecoefs = [1.0]
                for r in requests:
                    thevars += self.xVarIndices[r]
                    thecoefs += [-1.0]
                for ingoingTrip in self.originObject.ingoingTrips:
                    for r in requests:
                        if self.originObject.airport.name == requests[r].destination:
                            thevars += ingoingTrip.xVarIndices[r]
                            thecoefs += [-1.0]
                names = ["mustHaveRequest2"+self.getNameAppendix()]
                pairs = [cplex.SparsePair(thevars,thecoefs)]
                senses = ['L']
                rhs=[0]
                self.mustHaveRequest2Constraints = modelHandler.addConstraints(names,pairs,senses,rhs)
        self.timeOrderCuts = []
        if self.trip.graph.addTimeOrderCuts:
            if self.destinationCopyID != 0:
                names  = ["timeOrder" + self.getNameAppendix()]
                thevars = self.tVarIndices+ self.yVarIndices
                thecoefs = [1,-planes[self.planeName].plane_max_timestep]
                for ingoingTrip in self.trip.graph.nodes[self.destinationObject.name].copyList[self.planeName][self.destinationCopyID-1].ingoingTrips:
                    thevars += ingoingTrip.tVarIndices
                    thecoefs+= [-1]
                pairs = [cplex.SparsePair(thevars,thecoefs)]
                senses = ["G"]
                rhs = [self.originObject.airport.min_return_time[self.planeName]-planes[self.planeName].plane_max_timestep]
                self.timeOrderCuts = modelHandler.addConstraints(names,pairs,senses,rhs)

    def createVariables(self,predecessor):
        modelHandler = self.trip.graph.modelHandler
        requests = self.trip.graph.requests
        self.xVarIndices = {}
        for r in requests:
            names = ['x'+self.getNameAppendix()+f'_{r}' ]
            obj=[ 0  ] 
            lb = [0  ]
            ub = [1]
            types = ["B"]
            self.xVarIndices[r] = modelHandler.addVariables(names,obj,lb,ub,types)
            if predecessor != 0:
                for branch in self.trip.graph.modelHandler.branchDictionary[predecessor.xVarIndices[r][0]]:
                    branch.vars.append(self.xVarIndices[r][0])
        names = ['y'+self.getNameAppendix()]
        obj=[ self.trip.travelcost]
        lb = [0]
        ub=[5]
        types = ["I"]
        self.yVarIndices = modelHandler.addVariables(names,obj,lb,ub,types)
        if predecessor != 0:
                for branch in self.trip.graph.modelHandler.branchDictionary[predecessor.yVarIndices[0]]:
                    branch.vars.append(self.yVarIndices[0])
        names = ['f'+self.getNameAppendix()]
        obj=[ 0] 
        lb = [0]
        ub=[bigNum]
        types = ["C"]
        self.fVarIndices = modelHandler.addVariables(names,obj,lb,ub,types)
        names = ['t'+self.getNameAppendix()]
        obj=[ 0] 
        lb = [0]
        ub=[bigNum]
        types = ["C"]
        self.tVarIndices = modelHandler.addVariables(names,obj,lb,ub,types)
        #weight variables
        return
    def getNameAppendix(self):
        return f"_{self.origin}_{self.destination}_{self.originCopyID}_{self.destinationCopyID}_{self.plane.name}"
    def addToExistingConstraints(self):
        modelHandler = self.trip.graph.modelHandler
        requests = self.trip.graph.requests
        for r in requests:
            modelHandler.changeConstraintCoefficient(self.originObject.xFlowConstraints[r][0],self.xVarIndices[r][0],-1.0)
            self.originObject.outgoingXVars[r].append(self.xVarIndices[r][0])
            modelHandler.changeConstraintCoefficient(self.destinationObject.xFlowConstraints[r][0],self.xVarIndices[r][0],1.0)
            self.destinationObject.ingoingXVars[r].append(self.xVarIndices[r][0])
        modelHandler.changeConstraintCoefficient(self.originObject.fFlowConstraints[0],self.fVarIndices[0],-1.0)
        modelHandler.changeConstraintCoefficient(self.destinationObject.fFlowConstraints[0],self.fVarIndices[0],1.0)
        modelHandler.changeConstraintCoefficient(self.originObject.fFlowConstraints[0],self.yVarIndices[0],-self.trip.fuel_consumption)
        
        modelHandler.changeConstraintCoefficient(self.originObject.tFlowConstraints[0],self.tVarIndices[0],-1.0)
        modelHandler.changeConstraintCoefficient(self.destinationObject.tFlowConstraints[0],self.tVarIndices[0],1.0)
        modelHandler.changeConstraintCoefficient(self.destinationObject.tFlowConstraints[0],self.yVarIndices[0],self.trip.turnover_travel_timesteps)
        
        modelHandler.changeConstraintCoefficient(self.originObject.yFlowConstraints[0],self.yVarIndices[0],-1.0)
        self.originObject.outgoingYVars.append(self.yVarIndices[0])
        modelHandler.changeConstraintCoefficient(self.destinationObject.yFlowConstraints[0],self.yVarIndices[0],1.0)
        self.destinationObject.ingoingYVars.append(self.yVarIndices[0])
        
        self.originObject.varsForNext.append(self.yVarIndices[0])
        if self.destinationCopyID != 0:
            modelHandler.changeConstraintCoefficient(self.destinationObject.boundByPreviousConstraints[0],self.yVarIndices[0],1.0)
        if self.destinationObject.isHighestIndex == 0:
            modelHandler.changeConstraintCoefficient(self.destinationObject.max1ingoingConstraints[0],self.yVarIndices[0],1.0)
        if self.originObject.isHighestIndex == 0:
            modelHandler.changeConstraintCoefficient(self.originObject.max1outgoingConstraints[0],self.yVarIndices[0],1.0)
        
        if self.originObject.isHighestIndex == 0:
            const = self.originObject.airport.copyList[self.plane.name][self.originCopyID+1].boundByPreviousConstraints[0]
            modelHandler.changeConstraintCoefficient(const,self.yVarIndices[0],-5.0)
        
        
        for r in requests:
            modelHandler.changeConstraintCoefficient(requests[r].stopsConstraints[0],self.xVarIndices[r][0],1.0)
            modelHandler.changeConstraintCoefficient(requests[r].detourConstraints[0],self.xVarIndices[r][0],self.trip.distance)
        #must have request constraints
        if self.trip.graph.mustServeRequestCuts:
            for ingoingTrip in self.originObject.ingoingTrips:
                if ingoingTrip.mustHaveRequest1Constraints != []:
                    for r in requests:
                        if requests[r].origin == self.originObject.airport.name:
                            modelHandler.changeConstraintCoefficient(ingoingTrip.mustHaveRequest1Constraints[0],
                                                                     self.xVarIndices[r][0],-1.0)
        if self.trip.graph.mustServeRequestCuts:
            for outgoingTrip in self.destinationObject.outgoingTrips:
                if outgoingTrip.mustHaveRequest2Constraints != []:
                    for r in requests:
                        if requests[r].destination == self.destinationObject.airport.name:
                            modelHandler.changeConstraintCoefficient(outgoingTrip.mustHaveRequest2Constraints[0],
                                                                     self.xVarIndices[r][0],-1.0)
        if self.trip.graph.addTimeOrderCuts and self.destinationCopyID !=  len(self.trip.graph.nodes[self.destinationObject.name].copyList[self.planeName])-1:
            for ingoingTrip in self.trip.graph.nodes[self.destinationObject.name].copyList[self.planeName][self.destinationCopyID+1].ingoingTrips:
                modelHandler.changeConstraintCoefficient(ingoingTrip.timeOrderCuts[0],self.tVarIndices[0],-1.0)
        
        if self.trip.graph.addMinFuelStopCuts:
            if self.destinationObject.airport.fuel[self.plane.required_fueltype] == 1:
                modelHandler.changeConstraintCoefficient(self.plane.minFuelStopCuts[0],self.yVarIndices[0],1.0)
            if self.originObject.airport.fuel[self.plane.required_fueltype] == 1:
                modelHandler.changeConstraintCoefficient(self.plane.minFuelStopCuts2[0],self.yVarIndices[0],1.0)
        
        if self.trip.graph.addMaxVisitCuts and len(self.originObject.airport.maxVisitsConstraints1) >0:
            modelHandler.changeConstraintCoefficient(self.originObject.airport.maxVisitsConstraints1[0],self.yVarIndices[0],1.0)
        if self.trip.graph.addMaxVisitCuts and len(self.destinationObject.airport.maxVisitsConstraints2) >0:
            modelHandler.changeConstraintCoefficient(self.destinationObject.airport.maxVisitsConstraints2[0],self.yVarIndices[0],1.0)
        return
  



class modelHandler():
    def __init__(self):
        self.model=cplex.Cplex()
        self.model.set_results_stream(None)
        self.model.set_log_stream(None)
        self.model.set_warning_stream(None)
        self.model.parameters.threads.set(1)
        self.constNum = 0
        self.varNum = 0
        self.integerIndices = []
        self.branchHistory = {}
        self.branchDictionary = {}
        self.constName2idx = {}
        self.name2idx = {}
        self.idx2name = {}
    def addVariables(self,names,objs,lbs,ubs,types):
        oldInds=self.model.variables.get_num()
        
        self.integerIndices += [oldInds+idx for idx,varType in enumerate(types) if varType == 'B' or varType =='I']
        types = ['C']*len(types)
        self.branchHistory.update({idx:[] for idx in self.integerIndices})
        self.branchDictionary.update({idx:[] for idx in self.integerIndices})
        self.model.variables.add(names = names,
                            types=types,obj=objs,
                            lb = lbs,ub = ubs)
        self.name2idx.update({name:oldInds+j for j,name in enumerate(names)})
        self.idx2name.update({oldInds+j:name for j,name in enumerate(names)})
        self.varNum = len(self.name2idx)

        return list(range(oldInds,oldInds+len(names)))
    def addConstraints(self,names,thevars,senses,rhs):
        oldInds=self.constNum
        self.model.linear_constraints.add(names=names,lin_expr = thevars, 
                                                     senses = senses, rhs = rhs)
        self.constName2idx.update({name:oldInds+j for j,name in enumerate(names)})
        self.constNum += len(names)
        return list(range(oldInds,oldInds+len(names)))
    def changeConstraintCoefficient(self,consIdx,varIdx,coeff):
        self.model.linear_constraints.set_coefficients([(consIdx,varIdx,coeff)]) 
    def solveLpRelaxation(self,node,tol=0.0001):

        model = self.model
        branchAmount = len(node.branches)
        model.linear_constraints.add(names = node.branchNames,lin_expr = node.branchLinExprs,senses = node.branchSenses,rhs = node.branchRhs)
        if (len(node.dualValues)==model.linear_constraints.get_num()) and (len(node.row_status)==model.linear_constraints.get_num()) and  (len(node.col_status)==model.variables.get_num()):
            model.parameters.advance.set(2)
            self.model.set_problem_type(0)
            model.start.set_start(col_status=node.col_status,row_status=node.row_status,
                                  row_dual=node.dualValues,col_primal=[],row_primal=[],col_dual=[])
            #model.start.set_start(col_status=[],row_status=[],
            #                      row_dual=node.dualValues,col_primal=[],row_primal=[],col_dual=[])
        self.model.set_problem_type(0)
        self.model.parameters.lpmethod.set(2)
        feas = self.solveModel()
        node.updatedLpRelaxation = 1
        #model.parameters.advance.set(0)
        if not feas:
            node.feasible = 0
            node.lowerBound = 1000000
            model.linear_constraints.delete(range(model.linear_constraints.get_num()-branchAmount,model.linear_constraints.get_num()))
            return 0
        else:
            solution = model.solution
            node.dualValues = solution.get_dual_values()
            node.col_status = solution.basis.get_basis()[0]
            node.row_status = solution.basis.get_basis()[1]
            node.primalValues = solution.get_values()
            node.lowerBound = solution.get_objective_value()
            
            node.integerValues = {idx:node.primalValues[idx] for idx in self.integerIndices}
            node.fractionals = {idx:val for idx,val in node.integerValues.items() if abs(round(val,0)-val)>tol}
        model.linear_constraints.delete(range(model.linear_constraints.get_num()-branchAmount,model.linear_constraints.get_num()))
        node.feasible = 1
        #self.tree.total_relaxation_time += time.time() - t0
        return 1
    def solveModel(self):
        #start = time.time()
        self.model.solve()
        #print(time.time()-start)
        #input("Enter to continue\n")
        return self.model.solution.is_primal_feasible()

class Graph():
    def __init__(self,airportData,tripData,requestData,planeData):
        self.mustServeRequestCuts = 1
        self.addTimeOrderCuts = 1
        self.addMinFuelStopCuts = 1
        self.addMaxVisitCuts = 1
        self.nodes = {}
        self.modelHandler = modelHandler()
        self.requests = {}
        self.trips = {}
        self.planes = {}
        for plane,data in planeData.items():
            self.planes[plane] = Plane(data,plane,self,tripData)
        for name,data in requestData.items():
            self.requests[name]=Request(name,data,self,tripData)
        for name,data in airportData.items():
            self.nodes[name] = Airport(name,data,self)
        for p in self.planes:
            self.trips[p]= {}
            for name1,dic1 in tripData[p].items():
                self.trips[p][name1]={}
                for name2,data in dic1.items():
                    self.trips[p][name1][name2]=Trip(self.nodes[name1],self.nodes[name2],self.planes[p],data,self)
        for p in self.planes:
            if self.planes[p].origin == self.planes[p].destination:
                airport=self.planes[p].origin
                self.addNewCopy(airport,p)
        #self.addNewCopy('KHW','0')
    def addNewCopy(self,nodeName,p):
        oldIdx = len( self.nodes[nodeName].copyList[p])-1
        self.nodes[nodeName].addCopy(p)
        predecessor = 0
        for name2 in self.trips[p][nodeName]:
            for destinationCopy in self.nodes[name2].copyList[p]:
                for tripCopy in self.trips[p][nodeName][name2].copyList:
                    if tripCopy.destinationCopyID == destinationCopy.copyID and tripCopy.originCopyID == oldIdx:
                        predecessor = tripCopy
                if predecessor == 0:
                    input("Error: No predecessor found.")
                self.trips[p][nodeName][name2].addCopy(self.nodes[nodeName].copyList[p][-1],destinationCopy,predecessor)
        for name1 in self.trips[p]:
            if nodeName in self.trips[p][name1].keys():
                for oriCopy in self.nodes[name1].copyList[p]:
                    for tripCopy in self.trips[p][name1][nodeName].copyList:
                        if tripCopy.originCopyID == oriCopy.copyID and tripCopy.destinationCopyID == oldIdx:
                            predecessor = tripCopy
                    if predecessor == 0:
                        input("Error: No predecessor found.")
                    self.trips[p][name1][nodeName].addCopy(oriCopy,self.nodes[nodeName].copyList[p][-1],predecessor)
    def analysizeSolution(self):
        print(self.modelHandler.model.solution.get_objective_value())
        solVals = self.modelHandler.model.solution.get_values()
        self.solDic = {g.modelHandler.idx2name[idx]:val for idx,val in enumerate(solVals)if val > 0.01 and( g.modelHandler.idx2name[idx][0:2]=='y_' or g.modelHandler.idx2name[idx][0:2]=='yd'or g.modelHandler.idx2name[idx][0:2]=='ya')}
        self.xSolDic = {g.modelHandler.idx2name[idx]:val for idx,val in enumerate(solVals)if val > 0.01 and g.modelHandler.idx2name[idx][0:2]=='x_'}
        solDic = {g.modelHandler.idx2name[idx]:val for idx,val in enumerate(solVals)if val > 0.01 and g.modelHandler.idx2name[idx][0:2]=='y_'}
        self.tarrSolDic =  {g.modelHandler.idx2name[idx]:val for idx,val in enumerate(solVals)if val > 0.01 and g.modelHandler.idx2name[idx][0:2]=='ta'}
        self.tSolDic =  {g.modelHandler.idx2name[idx]:val for idx,val in enumerate(solVals)if val > 0.01 and g.modelHandler.idx2name[idx][0:2]=='t_'}
        self.fSolDic =  {g.modelHandler.idx2name[idx]:val for idx,val in enumerate(solVals)if val > 0.01 and g.modelHandler.idx2name[idx][0:2]=='f_'}
        airportNum = {p:{airport:0 for airport in self.nodes} for p in self.planes}
        
        for key, val in self.xSolDic.items():
            tourData = re.split('_',key)
            if tourData[2] == self.requests[tourData[-1]].destination:
                tkey = f"t_{tourData[1]}_{tourData[2]}_{tourData[3]}_{tourData[4]}_{tourData[5]}"
                print(f'{tourData[-1]} DUE: {self.requests[tourData[-1]].latest_arrival_timesteps} arrival time: {self.tSolDic[tkey]}')
        for key, val in self.xSolDic.items():
            tourData = re.split('_',key)
            if tourData[1] == self.requests[tourData[-1]].origin:
                tkey = f"t_{tourData[1]}_{tourData[2]}_{tourData[3]}_{tourData[4]}_{tourData[5]}"
                print(f'{tourData[-1]} Earliest: {self.requests[tourData[-1]].earliest_departure_timesteps-self.nodes[tourData[1]].turnover_timesteps[tourData[5]]}, departure time: {self.tSolDic[tkey]}')
        for key,amount in solDic.items():
            a=re.split('_',key)
            airportNum[a[5]][a[2]]+=amount
        added = 0
        for p in self.planes:
            for airport,visits in airportNum[p].items():
                if visits > len(self.nodes[airport].copyList[p]):
                    added=1
                    print(f"adding {p}, {airport}")
                    self.addNewCopy(airport,p)
            
        if added==0:
            print("Optimal Solution Found")
            print(self.modelHandler.model.solution.get_objective_value())
        return added
    def refineBySolution(self,node,doRefine=1):
        solVals = node.primalValues
        self.solDic = {self.modelHandler.idx2name[idx]:val for idx,val in enumerate(solVals)if val > 0.01 and self.modelHandler.idx2name[idx][0:2]=='y_'}
        airportNum = {p:{airport:0 for airport in self.nodes} for p in self.planes}
        
        for key,amount in self.solDic.items():
            a=re.split('_',key)
            airportNum[a[5]][a[2]]+=amount
        if doRefine:
            added = 0
            for p in self.planes:
                for airport,visits in airportNum[p].items():
                    if visits > len(self.nodes[airport].copyList[p]):
                        added=1
                        print(f"adding {p}, {airport}")
                        self.addNewCopy(airport,p)
            return added
        else:
            return 0
        



class TreeNode():
    def __init__(self,tree,branches,dualValues=[],col_status=[],row_status=[]):
        self.tree = tree
        self.branches = branches
        self.branchNames = [branch.name for branch in self.branches]
        self.branchLinExprs = [branch.getLinExpr() for branch in self.branches]
        self.branchSenses = [branch.sense for branch in self.branches]
        self.branchRhs = [branch.rhs for branch in self.branches]
        self.dualValues = dualValues
        self.col_status= col_status
        self.row_status= row_status
        self.lowerBound = 0
        self.fractionals = {}
        if self.tree.graph.modelHandler.solveLpRelaxation(self) and self.lowerBound < self.tree.ub:
            self.feasible = 1
        else:
            self.feasible = 0
    def getOneBranches(self):
        retval = 0
        for rhs in self.branchRhs:
            if abs(rhs-1) < eps:
                retval += 1
        return retval   
    def chooseBranchVar(self):
        #return self.branchVar, self.branchVal
        #t0 = time.time()
        maxScore = -1000000
        chosenVar = -1
        chosenVal = -1
        scores = []
        for varName,varVal in self.fractionals.items():
            #return varName,varVal
            score,has_history = self.calcScore(varName)
            if has_history:
                scores.append(score)
            if score > maxScore:
                maxScore = score
                chosenVar = varName
                chosenVal = varVal
        if len (scores)>0:
            self.tree.psiAvg = sum(scores)/len(scores)
        #self.tree.branchVariable_selection_time += time.time()-t0
        if chosenVar == -1:
            print (self.fractionals)
            print ("Error")
        return chosenVar, chosenVal
    def calcScore(self,varName):
        branchHistory = self.tree.graph.modelHandler.branchHistory
        
        if len(branchHistory[varName])>0:
            psi_0 = 0.0
            psi_1 = 0.0
            for tup in branchHistory[varName]:
                psi_0 += tup[0]
                psi_1 += tup[1]
            psi_0 = psi_0 /len(branchHistory[varName])
            psi_1 = psi_1 /len(branchHistory[varName])
            adder = 0
            if self.tree.graph.modelHandler.idx2name[varName][0] == 'y':
                adder = 100
            return adder+(5.0/6)*min(psi_0,psi_1)+1.0/6*max(psi_0,psi_1),1
        else:
            return self.tree.psiAvg,0.0



class Branch():
    def __init__(self,var,sense,rhs,branchDictionary):
        branchDictionary[var].append(self)
        self.var = str( var)
        self.vars = [var]
        self.name= self.var + str(rhs)
        self.sense = sense
        self.rhs = rhs
        
    def __repr__(self):
        return self.var +" sense: " +(self.sense)
    def __str__(self):
        return self.var +" sense: " +(self.sense)
    def getLinExpr(self):
        return cplex.SparsePair(self.vars,[1]*len(self.vars)) 


class Tree():
    def __init__(self,graph,controlParameters,heuristicUB):
        self.graph = graph
        self.timeLimit = controlParameters['timeLimit']
        self.heuristicUB = heuristicUB
        self.ub = heuristicUB
        self.lb = -bigNum
        self.printInterval = 6
        self.count = 0
        self.psiAvg = 0.0
        self.root = TreeNode(self,[])
        self.openNodes = [self.root]
    def conditionalPrint(self,string):
        if self.count % self.printInterval == 0:
            print (string)
    def chooseNode(self,selection=2,fac=100):
        if selection == 1:
            minInd = 0
            minVal= 100000000
            for i,node in enumerate(self.openNodes):
                #if (len(node.fractionals)==0):
                #    return self.openNodes.pop(i)
                if node.lowerBound < minVal:
                    minInd = i
                    minVal = node.lowerBound
            if  self.lb < minVal:
                self.lb=minVal
        if selection == 2:
            minInd = 0
            minVal= 100000000
            minLb = 100000000
            for i,node in enumerate(self.openNodes):
                if node.lowerBound - fac*node.getOneBranches() < minVal:
                    minInd = i
                    minVal = node.lowerBound - fac*node.getOneBranches() 
                if node.lowerBound < minLb:
                    minLb = node.lowerBound
            if self.lb < minLb:
                self.lb = minLb
        return self.openNodes.pop(minInd)
    def branch(self,node):
        branchVar,branchVal = node.chooseBranchVar()
        #print "branching"
        f_1 = float(int(branchVal)+1)-branchVal
        f_0 = branchVal-float(int(branchVal))
        
        new_node_list = [TreeNode(node.tree,node.branches+[Branch(branchVar,'L',float(int(branchVal)),self.graph.modelHandler.branchDictionary)],
                                                           node.dualValues+[0.0],node.col_status,node.row_status+[0]),
                             TreeNode(node.tree,node.branches+[Branch(branchVar,'G',float(int(branchVal)+1),self.graph.modelHandler.branchDictionary)],
                                      node.dualValues+[0.0],node.col_status,node.row_status+[0])]  
        if new_node_list[0].feasible:
            c_0 = (new_node_list[0].lowerBound-node.lowerBound)/f_0
        else:
            c_0 = self.psiAvg*f_0
        if new_node_list[1].feasible:
            c_1 = (new_node_list[1].lowerBound-node.lowerBound)/f_1
        else:
            c_1 = self.psiAvg*f_1
        self.graph.modelHandler.branchHistory[branchVar].append((c_0,c_1))
        for new_node1 in new_node_list:
            if new_node1.feasible:
                if new_node1.lowerBound < self.ub-eps:
                    self.openNodes.append(new_node1)
    def branchAndRefine(self):
        self.count=0
        #return
        t0 = time.time()
        while ( len(self.openNodes)>eps) and (time.time()-t0 < self.timeLimit):
            self.count+=1
            self.conditionalPrint("Current lower bound: %f" % (self.lb))
            self.conditionalPrint("Current best upper Bound: %f " % (self.ub))
            self.conditionalPrint(f"Number of open nodes: {len(self.openNodes)}\n Number of iterations: {self.count}")
            node = self.chooseNode()
            if node.updatedLpRelaxation == 0:
                self.graph.modelHandler.solveLpRelaxation(node)
            if not node.feasible or node.lowerBound >= self.ub-eps:
                continue
            if len(node.fractionals)>0:
                self.branch(node)
                continue
            if self.graph.refineBySolution(node):
                self.latestInfeasibleNode = node
                self.openNodes.append(node)
                newRoot = TreeNode(self,[])
                print ("current root lb = %.2f" % newRoot.lowerBound)
                if self.lb-newRoot.lowerBound<0.1:
                    print ("Root node has same lower bound as branch tree, restarting from root")
                    self.openNodes=[newRoot]
                    self.lb = newRoot.lowerBound
                else:
                    self.openNodes= [node for node in self.openNodes if node.lowerBound < self.ub -0.1]
                    for openNode in self.openNodes:
                        openNode.updatedLpRelaxation = 0
            else:
                if node.lowerBound < self.ub-eps:
                    #self.solution_path = self.vrp.solToPaths(sol)
                    print( "Integer feasible solution found, objective: %f" %node.lowerBound)
                    self.ub = node.lowerBound
                    self.openNodes= [node for node in self.openNodes if node.lowerBound < self.ub -0.1]
                    self.solutionNode = node
        self.solveTime= time.time()-t0
    def iterativeRefinement(self):
        self.count=0
        self.solutionNode = 0
        #return
        t0 = time.time()
        primalFeasible = 0
        while not primalFeasible  and (time.time()-t0 < self.timeLimit):
            while ( len(self.openNodes)>eps) and (time.time()-t0 < self.timeLimit):
                self.count+=1
                self.conditionalPrint("Current lower bound: %f" % (self.lb))
                self.conditionalPrint("Current best upper Bound: %f " % (self.ub))
                self.conditionalPrint(f"Number of open nodes: {len(self.openNodes)}\n Number of iterations: {self.count}")
                node = self.chooseNode()
                if node.updatedLpRelaxation == 0:
                    self.graph.modelHandler.solveLpRelaxation(node)
                if not node.feasible or node.lowerBound >= self.ub-eps:
                    continue
                if len(node.fractionals)>0:
                    self.branch(node)
                    continue
                if node.lowerBound < self.ub-eps:
                    #self.solution_path = self.vrp.solToPaths(sol)
                    print( "Integer feasible solution found, objective: %f" %node.lowerBound)
                    self.ub = node.lowerBound
                    self.openNodes= [node for node in self.openNodes if node.lowerBound < self.ub -0.1]
                    self.solutionNode = node
            if self.solutionNode==0:
                break
            primalFeasible = not self.graph.refineBySolution(self.solutionNode)
            self.solutionNode=0
            self.openNodes = [TreeNode(self,[])]
            self.lb=0
            self.ub = 30000
        self.solveTime= time.time()-t0

directories = {'BUF-AIV':('Testinstances/A2-BUF_A2-AIV',12615),
               'BUF-ANT':('Testinstances/A2-BUF_A2-ANT',20725),
               'BUF-BEE':('Testinstances/A2-BUF_A2-BEE',17634),
               'BUF-BOK':('Testinstances/A2-BUF_A2-BOK',12918),
               'BUF-EGL':('Testinstances/A2-BUF_A2-EGL',22114),
               'BUF-GNU':('Testinstances/A2-BUF_A2-GNU',17351),
               'BUF-JKL':('Testinstances/A2-BUF_A2-JKL',20775),
               'BUF-LEO':('Testinstances/A2-BUF_A2-LEO',24939),
               'BUF-NAS':('Testinstances/A2-BUF_A2-NAS',15932),
               'BUF-OWL':('Testinstances/A2-BUF_A2-OWL',16899),
               'BUF-ZEB':('Testinstances/A2-BUF_A2-ZEB',15926),
               'EGL-BEE':('Testinstances/A2-EGL_A2-BEE',16654),
               'EGL-GNU':('Testinstances/A2-EGL_A2-GNU',20239),
               'EGL-LEO':('Testinstances/A2-EGL_A2-LEO',19389),
               'GNU-BEE':('Testinstances/A2-GNU_A2-BEE',11312),
               'GNU-JKL':('Testinstances/A2-GNU_A2-JKL',11099),
               'GNU-LEO':('Testinstances/A2-GNU_A2-LEO',18541),
               'LEO-AIV':('Testinstances/A2-LEO_A2-AIV',13616),
               'LEO-ANT':('Testinstances/A2-LEO_A2-ANT',17382),
               'LEO-BEE':('Testinstances/A2-LEO_A2-BEE',19891),
               'LEO-BOK':('Testinstances/A2-LEO_A2-BOK',15373),
               'LEO-JKL':('Testinstances/A2-LEO_A2-JKL',17552),
               'LEO-NAS':('Testinstances/A2-LEO_A2-NAS',18232),
               'LEO-OWL':('Testinstances/A2-LEO_A2-OWL',15828),
               }


controlParameters = {'timeLimit':18000}


intToDir={i:dire for i,dire in enumerate(directories.keys())}

ints =  [int(intStr) for intStr in re.split("_",sys.argv[1])]
#g.modelHandler.solveModel()
#added = g.analysizeSolution()
"""
while added:
    g.modelHandler.solveModel()
    added = g.analysizeSolution()
"""
fileName = 'results.txt'
for inte in ints:
    airportData,tripData,requestData,planeData = readData(directories[intToDir[inte]][0])
    g=Graph(airportData,tripData,requestData,planeData)
    tree = Tree(g,controlParameters,directories[intToDir[inte]][1]+1)
    if sys.argv[2] == 'BaR':
        solTime = time.time()
        tree.branchAndRefine()
        solTime = time.time()-solTime
        file = open(fileName, "a")
        file.write(f"{intToDir[inte]}, alg: {sys.argv[2]}, nodes: {tree.count}, time: {solTime}\n")
        file.close()
    else:
        solTime = time.time()
        tree.iterativeRefinement()
        solTime = time.time()-solTime
        file = open(fileName, "a")
        file.write(f"{intToDir[inte]}, alg: {sys.argv[2]}, nodes: {tree.count}, time: {solTime}\n")
        file.close()