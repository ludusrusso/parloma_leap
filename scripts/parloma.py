#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from tf.msg import tfMessage
import tf
import collections
from serial_bridge.msg import generic_serial

pub = rospy.Publisher('/serial_topic', generic_serial, queue_size=10)


class Trans2Cmd:

    """Docstring for Trans2Cmd. """

    def __init__(self, transforms):
        """TODO: to be defined1. """
        self.fingers = ['thumb', 'index', 'middle', 'ring', 'pinky']
        self.hands = ['right', 'left']
        self.refs = ['proximal', 'intermediate', 'distal']

        self.extracted_data = collections.defaultdict(lambda: collections.defaultdict(dict))

        for tr in transforms:
            info = tr.child_frame_id.split('_')
            if len(info) > 2 and info[2] in self.fingers and info[3] in self.refs:
                self.extracted_data[info[0]][info[2]][info[3]] = [a for a in get_rpy_from_tr(tr)]

        for finger in self.fingers:
            print sum([self.extracted_data['right'][finger][r][0] for r in self.refs])
            # print self.extracted_data['right'][finger]



    def get_cmd(self):
        pass

def get_motor_id_by_frame(frame_id):
    if frame_id.find('thumb') >= 0:
        return 0
    elif frame_id.find('index') >= 0:
        return 1
    elif frame_id.find('middle') >= 0:
        return 2
    elif frame_id.find('ring') >= 0:
        return 3
    elif frame_id.find('pinky') >= 0:
        return 4

def get_rpy_from_tr(tr):
    r = tr.transform.rotation
    q = (r.x, r.y, r.z, r.w)
    roll, pitch, yaw = tf.transformations.euler_from_quaternion(q)
    return roll, pitch, yaw


def pub_commands(hand, finger, transforms,k):
    a = 0.0;
    b = 0.0;
    c = 0.0;

    for tran in transforms:
        if tran.child_frame_id.find(hand)>= 0 and tran.child_frame_id.find(finger) >= 0:
            if tran.child_frame_id.find('proximal') >= 0:
                a, pittt, _ = get_rpy_from_tr(tran)
                if tran.child_frame_id.find('middle') >= 0:
                    print pittt
            elif tran.child_frame_id.find('intermediate') >= 0:
                b,_ ,_  = get_rpy_from_tr(tran)
            elif tran.child_frame_id.find('distal') >= 0:
                c, _ , _  = get_rpy_from_tr(tran)

    to_s = -(a+b+c)*180/3.1415
    if (to_s >= 0 and to_s <= 180):
        msg = generic_serial()
        msg.msg = [242, get_motor_id_by_frame(finger), int((180-to_s))]

        pub.publish(msg)

def get_hand_ct_from_transform(transfs):

    # if tr.child_frame_id.find('proximal') >= 0 and tr.child_frame_id.find('right') >= 0:
    #     r = tr.transform.rotation
    #     q = (r.x, r.y, r.z, r.w)
    #     roll, pitch, yaw = tf.transformations.euler_from_quaternion(q)
    #     #print tr.child_frame_id, -roll*180/3.14
    #     to_s = -roll*180/3.14
    #     if (to_s >= 0 and to_s <= 180):
    #         msg = generic_serial()
    #         msg.msg = [242, get_motor_id_by_frame(tr.child_frame_id), 180-int(2*to_s)]
    #         pub.publish(msg)
    for tr in transfs:
        if tr.child_frame_id == 'right_hand':
            r = tr.transform.rotation
            q = (r.x, r.y, r.z, r.w)
            roll, pitch, yaw = tf.transformations.euler_from_quaternion(q)
            to_s = 90 - 180*yaw/3.14
            if (to_s >= 0 and to_s <= 180):
                msg = generic_serial()
                msg.msg = [242, 8, int(to_s)]
                pub.publish(msg)



def callback(data):

    # tc = Trans2Cmd(data.transforms)

    if callback.flag%4 == 0:
        pub_commands('right', 'index', data.transforms, 1)
        pub_commands('right', 'middle', data.transforms, 1)
        pub_commands('right', 'thumb', data.transforms, 1)
        pub_commands('right', 'pinky', data.transforms, 1)
        pub_commands('right', 'ring', data.transforms, 1)
        get_hand_ct_from_transform(data.transforms)

    callback.flag += 1
    #print len(data.transforms)
    # for tf in data.transforms:
        # get_hand_ct_from_transform(tf)
    #if data.transforms[0].child_frame_id.find('proximal') >= 0:
        #r = data.transforms[0].transform.rotation
        #q = (r.x, r.y, r.z, r.w)
        #print data.transforms[0].child_frame_id,  tf.transformations.euler_from_quaternion(q)
    

callback.flag = 1

def listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("/tf", tfMessage, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()

