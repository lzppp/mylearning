from __future__ import print_function
import math
import random
from simanneal import Annealer
import networkx as nx

class recalculatebySA(Annealer):
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
        
        #'''
        #random select a key
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
    g[1][2]['bw'] = 2
    g[1][3]['bw'] = 2
    g[2][4]['bw'] = 2
    g[3][4]['bw'] = 2
    g.add_edge(2,3,weight=1)
    g[2][3]['delay'] = 3
    g[2][3]['bw'] = 1
    #init some flows
    flow = {}
    path = {}
    selectpath = {}
    app = []
    '''
    for a in nx.shortest_simple_paths(g, source=1,target=4, weight='cost'):
        app.append(a)
    print (app)
    '''
    flow[('10.0.0.1','10.0.0.4')] = {'ip_src':'10.0.0.1','ip_dst':'10.0.0.4','src':1,'dst':4,'bw':1} 
    flow[('10.0.0.2','10.0.0.3')] = {'ip_src':'10.0.0.2','ip_dst':'10.0.0.3','src':2,'dst':3,'bw':1} 
    flow[('10.0.0.4','10.0.0.2')] = {'ip_src':'10.0.0.4','ip_dst':'10.0.0.2','src':4,'dst':2,'bw':1} 
    flow[('10.0.0.4','10.0.0.1')] = {'ip_src':'10.0.0.4','ip_dst':'10.0.0.1','src':4,'dst':1,'bw':1} 
    flow[('10.0.0.3','10.0.0.4')] = {'ip_src':'10.0.0.3','ip_dst':'10.0.0.4','src':3,'dst':4,'bw':1} 
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
    state, e = tsp.anneal()
    print (selectpath)
    print ("cost %d" % e )
    print (state)