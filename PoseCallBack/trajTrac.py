import rospy
import numpy as np 
import math
import time
import sympy
from math import *
from sympy import *
from std_msgs.msg import Int32
from std_msgs.msg import Float32
from std_msgs.msg import Float32MultiArray
from scipy.optimize import linprog


#pos, steering, speed, 

def updateSpeed(data):
	'''
	Speed call back function
	'''
	global rps2mps
	global v
	global w
	
	v = data.data * rps2mps
	

def updatePose(data):
	global x
	global y
	global theta
	global uold
	global xs
	global ys
	global t_init
	pose = data.data
	x = pose[0]
	y = pose[1]
	theta = pose[2]/180.*math.pi

	xss = xs
	yss = ys

	xr,yr,thetar,wr,vr = refState(xss,yss,time.time()-t_init)
	print time.time()-t_init
	
	uold= CLF(xr,yr,thetar,wr,vr,x,y,theta,uold)
	
def sat(a,b,c):
	if(a<b):
		return b
	elif(a>c):
		return c
	else:
		return a


def updateGoal(data):
	global start
	global goal

	start = [x,y,theta]
	goal = data.data
	traj(start,goal)




def refState(xss,yss,t):
	xr = xss[0]+xss[1]*t+xss[2]*t**2+xss[3]*t**3
	yr = yss[0]+yss[1]*t+yss[2]*t**2+yss[3]*t**3
	dxr = xss[1]+2.*xss[2]*t+3.*xss[3]*t**2
	dyr = yss[1]+2.*yss[2]*t+3.*yss[3]*t**2
	ddxr = 2.*xss[2]+6.*xss[3]*t
	ddyr = 2.*yss[2]+6.*yss[3]*t
	thetar = math.atan2(dyr,dxr)
	vr = dxr*math.cos(thetar) + dyr*math.sin(thetar)
	wr = 1./vr*(ddyr*math.cos(thetar) - ddxr*math.sin(thetar))



	return xr,yr,thetar,wr,vr




def traj(start, goal):
	global dt
	global unitSpeed
	global xs
	global ys
	global t_init

	v = 1.0
	t_init = time.time()
	t0 = 0.0
	tf = (((abs(start[0]-goal[0]))**2+(abs(start[1]-goal[1]))**2)**0.5)/unitSpeed
	print "distance & time", tf*unitSpeed, tf
	if(tf<(0.20/unitSpeed)):
		xs = np.array([start[0],0.,0.,0.])
		ys = np.array([start[1],0.,0.,0.])
		print "reach goal xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
		return xs, ys
		pass

	#tf = 10.
	#print tf

	#A = np.array([[1.,0.,0.,0.,0.,0.,0.,0.],[0.,0.,0.,0.,1.,0.,0.,0.],[0.,math.sin(start[2]),0.,0.,0.,-1.*math.cos(start[2]),0.,0.],[0.,math.sin(start[2]),0.,0.,0.,math.cos(start[2]),0.,0.],[1.,tf,tf**2,tf**3,0.,0.,0.,0.],[0.,0.,0.,0.,1.,tf,tf**2,tf**3],[0,math.sin(goal[2]),2.*math.sin(goal[2])*tf,3.*math.sin(goal[2])*tf**2,0,math.cos(goal[2]),2.*math.cos(goal[2])*tf,3.*math.cos(goal[2])*tf**2],[0,math.sin(goal[2]),2.*math.sin(goal[2])*tf,3.*math.sin(goal[2])*tf**2,0,-1.*math.cos(goal[2]),-2.*math.cos(goal[2])*tf,-3.*math.cos(goal[2])*tf**2]])
	
	A = np.array([[1.,t0,t0**2,t0**3,0.,0.,0.,0.],\
				[0.,0.,0.,0.,1.,t0,t0**2,t0**3],\
				[1.,tf,tf**2,tf**3,0.,0.,0.,0.],\
				[0.,0.,0.,0.,1.,tf,tf**2,tf**3],\
				[0.,1.*sin(start[2]),2.*t0*sin(start[2]),3.*t0**2*sin(start[2]),0.,-1.*cos(start[2]),-2.*t0*cos(start[2]),-3.*t0**2*cos(start[2])],\
				[0.,1.*sin(goal[2]),2.*tf*sin(goal[2]),3.*tf**2*sin(goal[2]),0.,-1.*cos(goal[2]),-2.*tf*cos(goal[2]),-3.*tf**2*cos(goal[2])],\
				[0.,1.*cos(start[2]),2.*t0*cos(start[2]),3.*t0**2*cos(start[2]),0.,1.*sin(start[2]),2.*t0*sin(start[2]),3.*t0**2.*sin(start[2])],\
				[0.,1.*cos(goal[2]),2.*tf*cos(goal[2]),3.*tf**2*cos(goal[2]),0.,1.*sin(goal[2]),2.*tf*sin(goal[2]),3.*tf**2*sin(goal[2])]])
	'''
	A = np.array([[1.,t0,t0**2,t0**3,0.,0.,0.,0.],\
				[0.,0.,0.,0.,1.,t0,t0**2,t0**3],\
				[1.,tf,tf**2,tf**3,0.,0.,0.,0.],\
				[0.,0.,0.,0.,1.,tf,tf**2,tf**3],\
				[0.,math.sin(1).,2*t0,3*t0**2,0.,0.,0.,0.],\
				[0.,0.,0.,0.,0.,1.,2*t0,3*t0**2],\
				[0.,1.,2*tf,3*tf**2,0.,0.,0.,0.],\
				[0.,0.,0.,0.,0.,1.,2*tf,3*tf**2]])
	
	q,p = symbols('q p')
	print "=============================================="
	test = nsolve([p+q**2-4., math.exp(p)+p*q-3.],[p,q],[1.,1.])

	print test
	'''


	b = np.array([start[0],\
				start[1],\
				goal[0],\
				goal[1],\
				0.0,\
				0.0,\
				v,\
				v_final])
	A = A.astype(np.float64)
	b = b.astype(np.float64)
	#print A
	#print b

	ab = np.linalg.solve(A,b)
	xs = np.array([ab[0],ab[1],ab[2],ab[3]])
	ys = np.array([ab[4],ab[5],ab[6],ab[7]])
	#print "xs", xs
	#print "ys", ys
	#print "received Goal+++++++++"

	examx = xs[0]+xs[1]*tf+xs[2]*tf**2+xs[3]*tf**3
	examy = ys[0]+ys[1]*tf+ys[2]*tf**2+ys[3]*tf**3
	print "exam", examx, examy

	return xs, ys, t_init
	





def CLF(x_r, y_r, theta_r, w_r, v_r, x, y, theta, old):
	
	global cc1
	global cc2
	global xs
	global ys
	global ms2rps
	global w_max
	global w_min
	global v_max
	global v_min




	eta_w = 2.25
	eta_v = 0.75
	w_min = -1.0
	w_max = 1.0
	v_min = 0.0
	v_max = 0.2

	print "x,y,theta", x_r, y_r
	print "dist", abs(x_r-x), abs(y_r-y), ((x_r-x)**2+(y_r-y)**2)**0.5
	print xs, ys



	x2 = math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r)

	print x2, theta
	xb0 = theta_r - theta - (math.cos(theta)*(y - y_r) - math.sin(theta)*(x - x_r))/((math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r))**2 + (math.cos(theta)*(y - y_r) - math.sin(theta)*(x - x_r))**2 + 1.)**(1/2)
 

	print "etaaaa" , -1.*eta_v*x2
	u0 = sat(eta_w*xb0, w_min, w_max)
	u1 = sat(-1.*eta_v*x2,v_min,v_max)



	u = [u0, u1]


	#F = c1*u1 + c2*u2 + c
	'''
	c1 = (((math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r))\
		/((math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r))**2 + \
		(math.cos(theta)*(y - y_r) - math.sin(theta)*(x - x_r))**2 + 1.)**(1/2) - 1.)**\
		(theta - theta_r + (math.cos(theta)*(y - y_r) - math.sin(theta)*\
		(x - x_r))/((math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r))**2 +\
		(math.cos(theta)*(y - y_r) - \
		math.sin(theta)*(x - x_r))**2 + 1.)**(1/2)))/\
		((theta - theta_r + (math.cos(theta)*(y - y_r) - math.sin(theta)*(x - x_r))/\
		((math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r))**2 +\
		(math.cos(theta)*(y - y_r) - math.sin(theta)*(x - x_r))**2 + 1.)**(1/2))**2 + 1.)**(1/2)
		'''
	'''
	c1 = (((math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r))/\
        ((math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r))**2 + \
        (math.cos(theta)*(y - y_r) - math.sin(theta)*(x - x_r))**2 + 1.)**(1/2) - 1.)*\
        (theta - theta_r + (math.cos(theta)*(y - y_r) - math.sin(theta)*\
        (x - x_r))/((math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r))**2 +\
        (math.cos(theta)*(y - y_r) - math.sin(theta)*(x - x_r))**2 + 1.)**(1/2)))/\
        ((theta - theta_r + (math.cos(theta)*(y - y_r) - math.sin(theta)*(x - x_r))/\
        ((math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r))**2 +\
        (math.cos(theta)*(y - y_r) - math.sin(theta)*(x - x_r))**2 + 1.)**(1/2))**2 + 1.)**(1/2)


	#c1 = 1.
	c2 = (2.*(math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r)))/\
		((math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r))**2 + \
		(math.cos(theta)*(y - y_r) - math.sin(theta)*(x - x_r))**2 + 1.)**(1/2) - \
		((math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r))*(math.cos(theta)*(y - y_r) - \
		math.sin(theta)*(x - x_r))*(theta - theta_r + (math.cos(theta)*(y - y_r) - \
		math.sin(theta)*(x - x_r))/((math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r))**2 + \
		(math.cos(theta)*(y - y_r) - math.sin(theta)*(x - x_r))**2 + 1.)**(1/2)))/\
		(((theta - theta_r + (math.cos(theta)*(y - y_r) - math.sin(theta)*(x - x_r))/\
		((math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r))**2 + (math.cos(theta)*(y - y_r) - \
		math.sin(theta)*(x - x_r))**2 + 1.)**(1/2))**2 + 1.)**(1/2)*\
		((math.cos(theta)*(x - x_r) + math.sin(theta)*(y - y_r))**2 + \
		(math.cos(theta)*(y - y_r) - math.sin(theta)*(x - x_r))**2 + 1.)**(3/2))

	print "c1c2", c1, c2
	F = [-c1, c2]

	SteerUB = np.array([3.0/(old[1]+0.000000001),w_r+1.5, math.tan(0.5)*old[1]*l])
	SteerLB = np.array([3.0/(old[1]+0.000000001),-(w_r-1.5), math.tan(-0.5)*old[1]*l])
	print SteerUB
	print SteerLB
	g = [min(SteerUB), -1*min(SteerLB),min([20,old[1]+cc2]),-1*min([-1.2,-old[1]+2.*cc2,-0.1])]
	print g
	
	if (F[0]>0.):
		u[0] = g[1]
	elif(F[0]<0.):
		u[0] = g[0]
	else:
		print "c1 not a number"
		u[0] = 0.


	if (F[1]>0.):
		u[1] = g[3]
	elif(F[1]<0.):
		u[1] = g[2]
	else:
		print "c2 not a number"
		u[1] = 0.


	'''
	'''

	
	H = [[ 1., 0.],[-1., 0.],[ 0., 1.],[ 0.,-1.]]
	#u1 steer: 
	#u2 velocity:
	#print "old", old
	#print [3.0/(old[1]+0.000000001), math.tan(0.5)*old[1]/0.4,w_r+0.5]
	print "old", old
	
	print g
	g = [10.,10.,10.,10.]
	res = linprog(F,H,g)
	print res
	u = res.x
	'''
	print u
	#steer = math.atan(l/(max(v+0.1,u[1]))*u[0])
	steer = math.atan(l/(v+0.1)*u[0])
	nextSpeed = u[1]*ms2rps

	w = v/l*math.tan(steer)
	pwmSteer = int((-1*steer)/0.5*(13107-10130)+10000)
	st = sat(pwmSteer,7153,13107)
	print "Speed & steer", nextSpeed, steer/3.1415*180.
	if (nextSpeed<0.001):
		nextSpeed = 0.0
	pubSteer.publish(st)
	pubSpeed.publish(nextSpeed)

	print "steer", steer, nextSpeed
	print "================================================="
	return u




def initMessages():
	global pubSpeed
	global pubSteer
	rospy.init_node('TrajectoryTracking')
	pubSpeed = rospy.Publisher("/racer/ACC/nextSpeed", Float32, queue_size = 0)
	pubSteer = rospy.Publisher("racer/teensy/steer", Int32, queue_size = 1)

	speedSub = rospy.Subscriber("/racer/teensy/rpm", Float32, updateSpeed)
	#poseSub = rospy.Subsciber("/racer/map/pose",Float32MultiArray,updatePose)
	poseSub = rospy.Subscriber("/vicon/Pose",Float32MultiArray,updatePose)
	goalSub = rospy.Subscriber("/racer/map/goal", Float32MultiArray,updateGoal)
	rospy.spin()




def initValues():
	global rps2mps
	global ms2rps
	global ms2rps
	global dt 
	global x 
	global y 
	global theta 
	global w 
	global v
	global unitSpeed

	global start
	global goal
	global v_final

	global xs
	global ys
	global l

	global uold

	global cc2

	rps2mps = 0.1109
	ms2rps = 1./rps2mps
	x = 0
	y = 0
	theta = 0
	w = 0
	v = 0
	unitSpeed = 1.5

	start = [x,y,theta]
	goal = [10.,10.,0.]
	v_final = 0.
	l = 0.4



	uold = [0.000000001,0.0000000001]


	cc2 = 0.15



if __name__ == "__main__":
	global rps2mps
	global ms2rps
	global dt 
	global x 
	global y 
	global theta 
	global w 
	global v
	global unitSpeed

	global start
	global goal
	global v_final

	global xs
	global ys

	global uold
	initValues()
	
	try:
		initMessages()
	except rospy.ROSInterruptException:
		rospy.logerr('Could not start TrajectoryTracking node.')






	



