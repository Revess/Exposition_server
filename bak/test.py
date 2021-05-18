from math import sqrt,cos,pi
import matplotlib.pyplot as plt

two_pi = 2*pi
takel_1 = []
takel_2 = []
takel_3 = []
takel_4 = []
takel_5 = []
takel_6 = []
phase = 0
length = 100
b=6
tilt=45
'''
square fucntion
for i in range(length):
    output.append(sqrt((1+b**2)/((1+b**2)*(cos((two_pi*0)+phase)**2)))*cos((two_pi*0)+phase))
    phase+= two_pi*(1/length)
'''

def rope_function(position,phase,b=2,tilt=1):
    return (((sqrt((1+(b**2))/(1+((b**2)*(cos((two_pi*(position))+phase)**2))))*(cos((two_pi*(position))+phase)))+1)/2)*tilt

for i in range(length):
    takel_1.append(rope_function(0,phase,b,tilt))
    takel_2.append(rope_function(1/6,phase,b,tilt))
    takel_3.append(rope_function(2/6,phase,b,tilt))
    takel_4.append(rope_function(3/6,phase,b,tilt))
    takel_5.append(rope_function(4/6,phase,b,tilt))
    takel_6.append(rope_function(5/6,phase,b,tilt))
    phase+= (two_pi*(1/length))

plt.plot(takel_1)
plt.plot(takel_2)
plt.plot(takel_3)
plt.plot(takel_4)
plt.plot(takel_5)
plt.plot(takel_6)
plt.show()