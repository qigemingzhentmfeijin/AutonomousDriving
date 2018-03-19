import rospy
from std_msgs.msg import Float32MultiArray
import time




if __name__ == '__main__':
	rospy.init_node("fakegoal")
	oldTime = time.time()
	goal = Float32MultiArray()

	goal.data = [0.5,0.5,0.]

	pub = rospy.Publisher("/racer/map/goal",Float32MultiArray,queue_size = 10)

	while(True):
		rospy.sleep(0.5)
		if(time.time()-oldTime>1):
			pub.publish(goal)
			oldTime = time.time()
			print time.time()


	rospy.spin()
