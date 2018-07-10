import argparse
import rospy
import intera_interface
import intera_external_devices
import time
import record_data #file to record data.
import numpy as np

from avalos_sawyer import * 
from intera_interface import CHECK_VERSION
from intera_core_msgs.msg import JointCommand
from scipy import interpolate
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.interpolate import interp1d
from geometry_msgs.msg import (
    PoseStamped,
    Pose,
    Point,
    Quaternion,
)
from std_msgs.msg import Header
from sensor_msgs.msg import JointState
from intera_core_msgs.srv import (
    SolvePositionIK,
    SolvePositionIKRequest,
)


def save_matrix(_j,_name,_f):
    file2write=open(_name,'w')
    l=len(_j[0][:])
    time=np.linspace(0, (l-1)/float(_f), num=l)
    for n in range(l):
        file2write.write(str(time[n])+' , '+str(_j[0][n])+' , '+str(_j[1][n])+' , '+str(_j[2][n])+' , '+str(_j[3][n])+' , '+ str(_j[4][n])+' , '+str(_j[5][n])+' , '+str(_j[6][n])+'\n')
    file2write.close()
    print "save data en",_name
    return True
def generate_jerk(_a,_f):
    ext = len(_a[0])
    jk0=[]
    jk1=[]
    jk2=[]
    jk3=[]
    jk4=[]
    jk5=[]
    jk6=[]

    for n in range(ext-3):
        jk0.append((_a[0][n+1]-_a[0][n])*_f)
        jk1.append((_a[1][n+1]-_a[1][n])*_f)
        jk2.append((_a[2][n+1]-_a[2][n])*_f)
        jk3.append((_a[3][n+1]-_a[3][n])*_f)
        jk4.append((_a[4][n+1]-_a[4][n])*_f)
        jk5.append((_a[5][n+1]-_a[5][n])*_f)
        jk6.append((_a[6][n+1]-_a[6][n])*_f)
    for i in range(3):
        jk0.append(jk0[-1]) 
        jk1.append(jk1[-1]) 
        jk2.append(jk2[-1]) 
        jk3.append(jk3[-1]) 
        jk4.append(jk4[-1]) 
        jk5.append(jk5[-1]) 
        jk6.append(jk6[-1]) 
    ext= len(jk0)
    jk= [jk0,jk1,jk2,jk3,jk4,jk5,jk6]  
    print "Knots en jerk generados.",ext
    return jk,ext
def generate_acel(_v,_f):
    ext = len(_v[0])
    a0=[]
    a1=[]
    a2=[]
    a3=[]
    a4=[]
    a5=[]
    a6=[]

    for n in range(ext-2):
        a0.append((_v[0][n+1]-_v[0][n])*_f)
        a1.append((_v[1][n+1]-_v[1][n])*_f)
        a2.append((_v[2][n+1]-_v[2][n])*_f)
        a3.append((_v[3][n+1]-_v[3][n])*_f)
        a4.append((_v[4][n+1]-_v[4][n])*_f)
        a5.append((_v[5][n+1]-_v[5][n])*_f)
        a6.append((_v[6][n+1]-_v[6][n])*_f)
    for i in range(2):
        a0.append(a0[-1]) 
        a1.append(a1[-1]) 
        a2.append(a2[-1]) 
        a3.append(a3[-1]) 
        a4.append(a4[-1]) 
        a5.append(a5[-1]) 
        a6.append(a6[-1]) 
    ext= len(a0)
    a= [a0,a1,a2,a3,a4,a5,a6]  
    print "Knots en aceleracion generados.",ext
    return a,ext 
def generate_vel(_j,_f):
    ext = len(_j[0])
    v0=[]
    v1=[]
    v2=[]
    v3=[]
    v4=[]
    v5=[]
    v6=[]

    for n in range(ext-1):
        v0.append((_j[0][n+1]-_j[0][n])*_f)
        v1.append((_j[1][n+1]-_j[1][n])*_f)
        v2.append((_j[2][n+1]-_j[2][n])*_f)
        v3.append((_j[3][n+1]-_j[3][n])*_f)
        v4.append((_j[4][n+1]-_j[4][n])*_f)
        v5.append((_j[5][n+1]-_j[5][n])*_f)
        v6.append((_j[6][n+1]-_j[6][n])*_f)
    v0.append(v0[-1]) 
    v1.append(v1[-1]) 
    v2.append(v2[-1]) 
    v3.append(v3[-1]) 
    v4.append(v4[-1]) 
    v5.append(v5[-1]) 
    v6.append(v6[-1]) 
    ext= len(v0)
    v= [v0,v1,v2,v3,v4,v5,v6]  
    print "Knots en velocidad generados.",ext
    return v,ext  
def generate_path(_points,_time,_f):
    
    sp_0 = interpolate.InterpolatedUnivariateSpline(_time, _points[0][:],k=5)
    sp_1 = interpolate.InterpolatedUnivariateSpline(_time, _points[1][:],k=5)
    sp_2 = interpolate.InterpolatedUnivariateSpline(_time, _points[2][:],k=5)
    sp_3 = interpolate.InterpolatedUnivariateSpline(_time, _points[3][:],k=5)
    sp_4 = interpolate.InterpolatedUnivariateSpline(_time, _points[4][:],k=5)
    sp_5 = interpolate.InterpolatedUnivariateSpline(_time, _points[5][:],k=5)
    sp_6 = interpolate.InterpolatedUnivariateSpline(_time, _points[6][:],k=5)

    

    ts = np.linspace(_time[0], _time[-1], (_time[-1]-_time[0])*_f) 
    
    print "Valores en tiempo: \n" , len(ts)
    q0= sp_0(ts)
    q1= sp_1(ts)
    q2= sp_2(ts)
    q3= sp_3(ts)
    q4= sp_4(ts)
    q5= sp_5(ts)
    q6= sp_6(ts)

    q= [q0,q1,q2,q3,q4,q5,q6]
    ext = len(ts)
    print "Knots en posicion generados.",ext
    return q, ext
def ik_service_client(_x,_y,_z):
    _limb = intera_interface.Limb('right')
    ns = "ExternalTools/right/PositionKinematicsNode/IKService"
    iksvc = rospy.ServiceProxy(ns, SolvePositionIK)
    ikreq = SolvePositionIKRequest()
    hdr = Header(stamp=rospy.Time.now(), frame_id='base')
    poses = {
        'right': PoseStamped(
            header=hdr,
            pose=Pose(
                position=Point(
                    x=_x,
                    y=_y,
                    z=_z,
                ),
                orientation=Quaternion(
                    x=0.707,
                    y=0.707,
                    z=0.001,
                    w=0.001,
                ),
            ),
        ),
    }
    # Add desired pose for inverse kinematics
    ikreq.pose_stamp.append(poses["right"])
    # Request inverse kinematics from base to "right_hand" link
    ikreq.tip_names.append('right_hand')


    try:
        rospy.wait_for_service(ns, 5.0)
        resp = iksvc(ikreq)
    except (rospy.ServiceException, rospy.ROSException), e:
        rospy.logerr("Service call failed: %s" % (e,))
        return False

    # Check if result valid, and type of seed ultimately used to get solution
    if (resp.result_type[0] > 0):
        # Format solution into Limb API-compatible dictionary
        limb_joints = dict(zip(resp.joints[0].name, resp.joints[0].position))
        rospy.loginfo("Solucion IK ok.")
        print limb_joints
        _limb.move_to_joint_positions(limb_joints)
        return True
    else:
        rospy.logerr("INVALID POSE - No Valid Joint Solution Found.")
        rospy.logerr("Result Error %d", resp.result_type[0])
        return False

class Rdata():
    def __init__(self,_text):
    	self.file=_text
    	file=open(self.file,"w")
    	file.close()
        rospy.Subscriber("/robot/joint_states", JointState, self.talker)
        print("Init bridge")
        rate = rospy.Rate(100) # 10hz
        #while not rospy.is_shutdown():
        #    rate.sleep()


    def talker(self,data):

        if(data.name[0]=="head_pan"):
        	_file=open(self.file,"a")
    		_file.write(str(data.position[1])+","+str(data.position[2])+","+str(data.position[3])+","\
    		+str(data.position[4])+","+str(data.position[5])+","+str(data.position[6])+","+str(data.position[7])+\
    		","+str(data.velocity[1])+","+str(data.velocity[2])+","+str(data.velocity[3])+","\
    		+str(data.velocity[4])+","+str(data.velocity[5])+","+str(data.velocity[6])+","+str(data.velocity[7])+"\n")
    		_file.close()
        	