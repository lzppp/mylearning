from __future__ import print_function
import math
import random
from simanneal import Annealer
import networkx as nx
import time

class recalculatebySA(Annealer):
    upk = 1.1
    upmax = 5
    def anneal(self):
        """Minimizes the energy of a system by simulated annealing.

        Parameters
        state : an initial arrangement of the system

        Returns
        (state, energy): the best state and energy found.
        """
        step = 0
        self.start = time.time()

        # Precompute factor for exponential cooling from Tmax to Tmin
        if self.Tmin <= 0.0:
            raise Exception('Exponential cooling requires a minimum "\
                "temperature greater than zero.')
        Tfactor = -math.log(self.Tmax / self.Tmin)

        # Note initial state
        T = self.Tmax
        E = self.energy()
        prevState = self.copy_state(self.state)
        prevEnergy = E
        perT = T
        tt = 0
        self.best_state = self.copy_state(self.state)
        self.best_energy = E
        trials, accepts, improves = 0, 0, 0
        reward = 0
        if self.updates > 0:
            updateWavelength = self.steps / self.updates
            self.update(step, T, E, None, None)

        # Attempt moves to new states
        while step < self.steps and not self.user_exit:
            step += 1
            
            T = self.Tmax * math.exp(Tfactor * step / self.steps) * self.Tmin / self.Tmax#* (self.steps - step + 1) / self.steps#
            if tt != 0:
                 T = T * (self.upk**tt)
            perT = T
            self.move()
            E = self.energy()
            dE = E - prevEnergy
            trials += 1
            tt += 1
            P = math.exp(-dE / T) < random.random()#protable of stay , T up P down
            if dE > 0.0 and P:
                # Restore previous state
                #tt += 1
                self.state = self.copy_state(prevState)
                E = prevEnergy
                reward += 1
            else:
                # Accept new state and compare to best state
                accepts += 1
                if dE < 0.0:
                    improves += 1
                
                prevState = self.copy_state(self.state)
                prevEnergy = E
                if E < self.best_energy:
                    tt = 0
                    self.best_state = self.copy_state(self.state)
                    self.best_energy = E
            if self.updates > 1:
                if (step // updateWavelength) > ((step - 1) // updateWavelength):
                    self.update(
                        step, T, E, accepts / trials, improves / trials)
                    trials, accepts, improves = 0, 0, 0

        # line break after progress output
        print('')

        self.state = self.copy_state(self.best_state)
        if self.save_state_on_exit:
            self.save_state()
        # Return best state and energy
        return self.best_state, self.best_energy

    def distance(self , tpath ,graph):
        '''
            cost+=graph[][]['cost']
        '''
        if len(tpath) == 2:
            return self.graph[tpath[0]][tpath[1]]['delay']
        elif len(tpath) == 1:
            return 0
        
        else:
            cost = 0
            for i in range(0,len(tpath)-1):
                cost = cost + self.graph[tpath[i]][tpath[i+1]]['delay']
        return cost
    def bandcalculate(self , band , cost , tpath):
        if len(tpath) == 2:
            self.bandadd(tpath[0] , tpath[1] , band , cost)
            if band[(tpath[0] , tpath[1])]>self.graph[tpath[0]][tpath[1]]['bw']:
                return False
        elif len(tpath) == 1:
            return True
        else:
            for i in range(0,len(tpath)-1):
                self.bandadd(tpath[i] , tpath[i+1] , band , cost)
                if band[(tpath[i] , tpath[i+1])]>self.graph[tpath[i]][tpath[i+1]]['bw']:
                    return False
        return True

    def bandadd(self , a ,b , band , cost):
        if band.setdefault((a , b)) != None:
            band[(a,b)] += cost
            band[(b,a)] += cost
        else:
            band[(a,b)] = cost
            band[(b,a)] = cost


    def __init__(self , state , graph):
        self.graph = graph
        self.path = {}
        self.flow = {}
        super(recalculatebySA, self).__init__(state) 
    def move(self):
        #2 method to move ?!? 
        '''all random
        for flowkey in self.flow.keys():
            self.state[flowkey] = self.path[flowkey][random.randint(0, len(self.path[flowkey]) - 1)]
        '''
        
        #'''random select a key better
        li = list(self.flow.keys())
        flowkey = li[random.randint(0, len(li) - 1)]
        #random select a path
        self.state[flowkey] = self.path[flowkey][random.randint(0, len(self.path[flowkey]) - 1)]
        #'''


    def energy(self):
        '''
            all the cost
            add the limit
        '''
        e = 0
        band = {}
        for flowkey in self.flow.keys():
            
            e = e + self.distance(self.state[flowkey] , self.graph)
            if self.bandcalculate(band , self.flow[flowkey]['bw'] ,self.state[flowkey]) == False:
                e = 65535
                return e

        return e
def read():
    file = open('d:\\data.txt','r')
    text = file.readlines()
    flow = {}
    for i in range(0,len(text)):
        text[i] = text[i][0:len(text[i])-1]
        tmp = text[i].split(',')
        src = int(tmp[0].split(':')[1])
        dst = int(tmp[1].split(':')[1])
        bw = int(tmp[2].split(':')[1])
        ipsrc = "10.0.0."+tmp[0].split(':')[1]
        ipdst = "10.0.0."+tmp[1].split(':')[1]
        flow[(ipsrc,ipdst)] = {'ip_src':ipsrc,'ip_dst':ipdst,'src':src,'dst':dst,'bw':bw} 
    file.close()
    return flow
if __name__ == '__main__':
    '''
        test function
    '''
    # init a graph
    g = nx.Graph()
    g.add_edge(1,2,weight=1)
    g.add_edge(1,3,weight=1)
    g.add_edge(2,4,weight=1)
    g.add_edge(3,4,weight=1)
    g[1][2]['delay'] = 2
    g[1][3]['delay'] = 2
    g[2][4]['delay'] = 2
    g[3][4]['delay'] = 2
    g[1][2]['bw'] = 100
    g[1][3]['bw'] = 100
    g[2][4]['bw'] = 100
    g[3][4]['bw'] = 100
    g.add_edge(2,3,weight=1)
    g[2][3]['delay'] = 3
    g[2][3]['bw'] = 100
    #init some flows
    flow = {}
    path = {}
    selectpath = {}
    app = []
   
    '''
    for a in nx.shortest_simple_paths(g, source=1,target=4, weight='cost'):
        app.append(a)
    print (app)
    
    flow[('10.0.0.1','10.0.0.4')] = {'ip_src':'10.0.0.1','ip_dst':'10.0.0.4','src':1,'dst':4,'bw':1} 
    flow[('10.0.0.2','10.0.0.3')] = {'ip_src':'10.0.0.2','ip_dst':'10.0.0.3','src':2,'dst':3,'bw':1} 
    flow[('10.0.0.4','10.0.0.2')] = {'ip_src':'10.0.0.4','ip_dst':'10.0.0.2','src':4,'dst':2,'bw':1} 
    flow[('10.0.0.4','10.0.0.1')] = {'ip_src':'10.0.0.4','ip_dst':'10.0.0.1','src':4,'dst':1,'bw':1} 
    flow[('10.0.0.3','10.0.0.4')] = {'ip_src':'10.0.0.3','ip_dst':'10.0.0.4','src':3,'dst':4,'bw':1} 
    
    '''
    flow = read()
    for flowkey in flow.keys():
            '''
                generator must change to list or dict
            '''
            path[flowkey] = []
            for a in nx.shortest_simple_paths(g, source=flow[flowkey]['src'],
                                             target=flow[flowkey]['dst'], weight='delay'):
                path[flowkey].append(a)
    for flowkey in flow:
            selectpath[flowkey] = path[flowkey][random.randint(0, len(path[flowkey]) - 1)]
            #print self.selectpath[flowkey]
    tsp = recalculatebySA(selectpath , g )
    tsp.path = path
    tsp.flow = flow
    tsp.copy_strategy = "method"
    tsp.TMax = 350000
    tsp.Tmin = 100
    tsp.steps = 2400
    # tsp.updates = 25
    #test bwcalculate
    '''
    bw = {}
    print (
    tsp.bandcalculate(bw , 1 , [2,3]) and
    tsp.bandcalculate(bw , 1 , [1,2,4]) and
    tsp.bandcalculate(bw , 1 , [3,4]) and
    tsp.bandcalculate(bw , 1 , [4,3,1]) and
    tsp.bandcalculate(bw , 1 , [4,2])
    )

    #print (result)
    '''
    begin = time.time()
    
    # p = tsp.auto(0.001)
    # print (p)
    # tsp.TMax = p['tmax']
    # tsp.Tmin = p['tmin']
    # tsp.steps = p['steps']
    bsa = time.time()
    print ( "ger time %f"%(bsa - begin))
    state, e = tsp.anneal()
    print ("cost %d" % e )
    print (state)
    print ( "time %f"%(time.time() - bsa))