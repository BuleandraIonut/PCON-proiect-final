import cv2
import mediapipe as mp
from pythonosc import udp_client

# setup osc
osc = udp_client.SimpleUDPClient("127.0.0.1", 8999)

# mediapipe init
mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_mesh

# init models w/ good params
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
face = mp_face.FaceMesh(
    max_num_faces=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# cam setup
cap = cv2.VideoCapture(0)

# landmark indices
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
FINGER_TIPS = [4, 8, 12, 16, 20]
FINGER_PIPS = [2, 6, 10, 14, 18]

def is_hand_closed(landmarks):
    """check if hand closed based on finger positions"""
    count = 0
    # thumb check
    if landmarks.landmark[4].x > landmarks.landmark[2].x - 0.05:
        count += 1
    # other fingers
    for tip, pip in zip(FINGER_TIPS[1:], FINGER_PIPS[1:]):
        if landmarks.landmark[tip].y > landmarks.landmark[pip].y - 0.03:
            count += 1
    # closed if 4+ fingers down
    return not count >= 4

def classify_hand(hand_landmarks, handedness):
    """get hand type - mediapipe returns mirrored"""
    label = handedness.classification[0].label
    return "Left" if label == "Right" else "Right"

# main loop
while True:
    ok, frame = cap.read()
    if not ok:
        continue
    
    # flip for mirror effect
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # face detection
    face_res = face.process(rgb)
    if face_res.multi_face_landmarks:
        f = face_res.multi_face_landmarks[0]
        nose = f.landmark[4]  # nose tip
        
        # send head pos
        osc.send_message("/cap", [nose.x, nose.y, nose.z])
        
        # eye detection - check left eye height
        eye_open = abs(f.landmark[LEFT_EYE_TOP].y - f.landmark[LEFT_EYE_BOTTOM].y) > 0.01
        osc.send_message("/ochi", int(eye_open))
    
    # hand detection
    hand_res = hands.process(rgb)
    if hand_res.multi_hand_landmarks and hand_res.multi_handedness:
        # track both hands
        hands_data = {"Left": None, "Right": None}
        
        # process each detected hand
        for hand_landmarks, handedness in zip(hand_res.multi_hand_landmarks, hand_res.multi_handedness):
            hand_type = classify_hand(hand_landmarks, handedness)
            hands_data[hand_type] = hand_landmarks
        
        # left hand -> mana1
        if hands_data["Left"]:
            h = hands_data["Left"]
            # wrist pos
            osc.send_message("/mana1", [
                h.landmark[0].x,
                h.landmark[0].y,
                h.landmark[0].z
            ])
            # check closed (inverted: 0=closed, 1=open)
            closed = is_hand_closed(h)
            osc.send_message("/mana1_inchisa", int(not closed))
        
        # right hand -> mana2
        if hands_data["Right"]:
            h = hands_data["Right"]
            # wrist pos
            osc.send_message("/mana2", [
                h.landmark[0].x,
                h.landmark[0].y,
                h.landmark[0].z
            ])
            # check closed (inverted: 0=closed, 1=open)
            closed = is_hand_closed(h)
            osc.send_message("/mana2_inchisa", int(not closed))
    
    # quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# cleanup
cap.release()
cv2.destroyAllWindows()
hands.close()
face.close()