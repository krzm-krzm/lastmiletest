#距離は100m換算の方がいいかもしれない

import gurobipy as gp

import numpy as np
import math
import random


x = [37, 49, 52, 20, 40, 21]
y = [52, 49, 64, 26, 30, 47]
n = len(x) #ステーション数
c =np.zeros((n,n)) #距離格納
RC = np.zeros((n,n))#ステーション間の燃料費格納
riyoukyaku=100 #利用客数
T= 8000#サービス稼働時間
V = 20 #trip時の平均時速(km/h)
Vs = (V*1000) / 3600 #trip時の平均秒速(m/s)
Vm = (V*1000) / 60 #trip時の平均分速(m/m)
cost = 100 / 30000 #配回送時の燃費(円/m)
kyaku=np.zeros((riyoukyaku,2)) #行は利用客、1列目に出発地、２列目に目的地
r = np.zeros((n,n,T))
I = np.array(range(riyoukyaku)) #利用客集合


def distance(x1,x2,y1,y2): #距離を求める関数
    d = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    return d

for i in range(n):  #ステーション間の距離を求める
    for j in range(n):
        c[i][j] = distance(x[i],x[j],y[i],y[j]) *100 #100は距離を100m換算してる
        RC[i][j] = math.ceil(c[i][j] * cost)

#重複なし
def rand_ints_nodup(a,b,k):
    ns = []
    while len(ns) < k:
        n = random.randint(a,b)
        if not n in ns:
            ns.append(n)
    return ns

t = [random.randint(0,1000) for i in range(riyoukyaku)] #サービスの稼働時間内の利用客の出発時間を設定

for i in range(riyoukyaku):
    a = rand_ints_nodup(0,5,2)
    kyaku[i,0] = int(a[0])
    kyaku[i,1] = int(a[1])

riyoukyaku_distance = np.zeros(riyoukyaku) #利用客の運転距離

for i in range(riyoukyaku):
    riyoukyaku_distance[i]=c[int(kyaku[i][0])][int(kyaku[i][1])]


origin = np.zeros(riyoukyaku) #利用客の出発場所
dest = np.zeros(riyoukyaku) #利用客の到着場所
for i in range(riyoukyaku):
    origin[i] = kyaku[i][0]
    dest[i] = kyaku[i][1]


P = np.zeros(riyoukyaku) #利用客ごとの運賃
for i in range(riyoukyaku):
    if riyoukyaku_distance[i] <= Vm*10:#10は初乗り10分のこと
        P[i]=200
    else:
        ikou =(riyoukyaku_distance[i] -Vm*10)/Vm *20
        P[i] = 200+round(ikou)


start =np.zeros(riyoukyaku) #利用客の出発時間
for i in range(riyoukyaku):
    start[i] = t[i]
end = np.zeros(riyoukyaku) #利用客の到着時間
for i in range(riyoukyaku):
    toutyaku = (riyoukyaku_distance[i])/(Vs)
    end[i] = t[i] + math.ceil(toutyaku)


model_1 = gp.Model(name ="Gurobitest")

z = {}
for i in range(riyoukyaku):
 z[i] = model_1.addVar(vtype = gp.GRB.BINARY,name = "binary")
r = np.zeros((n,n,T),dtype = np.object)
for i in  range(n):
    for j in range(n):
        for t in range(T):
            r[i,j,t] = model_1.addVar(lb= 0,ub = 3,vtype = gp.GRB.INTEGER,name = "yosohensu")

model_1.setObjective(gp.quicksum(P[i]*z[i] for i in range(riyoukyaku))-gp.quicksum(RC[i,j] for i in range(n) for j in range(n)) * gp.quicksum(r[i,j,t]  for i in range(n) for j in range(n) for t in range(T) if i != j),sense = gp.GRB.MAXIMIZE)

con_1 = np.zeros((n,T),dtype =np.object)
N = np.zeros((n,T))
N = N+3
for j in range(n):
    for t in range(T-1):
        con_1[j,t+1] = model_1.addConstr((N[j,t] - gp.quicksum(z[i] for i in range(riyoukyaku) if origin[i] == j and start[i] == t) -
                                     gp.quicksum(r[j,l,t]  for l in range(n) if l != j) +gp.quicksum(z[i] for i in range(riyoukyaku) if dest[i] == j and end[i] == t)
                                     +gp.quicksum(r[l,j,t]  for l in range(n) if l != j)) == N[j,t+1] , name ="seiyaku1")
con_2 = np.zeros((n,T),dtype = np.object)
for j in range(n):
    for t in range(T):
        con_2[j,t] =model_1.addConstr((gp.quicksum(z[i] for i in range(riyoukyaku) if origin[i] == j and start[i] == t) +
                                       gp.quicksum(r[j,l,t] for l in range(n) if l != j)) <= N[j,t] ,name = "seiyaku2")
model_1.optimize()
print("解")





