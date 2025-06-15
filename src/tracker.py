import cv2
import mediapipe as mp
from pythonosc.udp_client import SimpleUDPClient
import time

# Configurare initiala
osc = SimpleUDPClient("127.0.0.1", 8999)
mp_holistic = mp.solutions.holistic

# Puncte landmark pentru ochi
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# Ultimele valori cunoscute pentru backup
last_values = {
   "cap": [0.5, 0.5, 0.0],
   "manaStanga": [0.5, 0.5, 0.0],
   "manaDreapta": [0.5, 0.5, 0.0],
   "ochi": 1,
   "manaStangaInchisa": 1,
   "manaDreaptaInchisa": 1
}

# Variabile pentru toggle ochi
eye_toggle_state = 1
eyes_closed_start_time = None
TOGGLE_DURATION = 0.75

"""""""""""""""""""""""
    pts[1] ---- pts[2]   
       |         |
pts[0] v1       v2    pts[3]    
       |         |    
    pts[5] ---- pts[4]    
     
←----------h----------→ 
"""""""""""""""""""""""
def get_eye_ratio(landmarks, points):
   """Calculeaza Eye Aspect Ratio"""
   pts = [[landmarks[p].x, landmarks[p].y] for p in points]
   v1 = abs(pts[1][1] - pts[5][1])
   v2 = abs(pts[2][1] - pts[4][1])
   h = abs(pts[0][0] - pts[3][0])
   return (v1 + v2) / (2.0 * h + 1e-6)

def get_head_position(face_landmarks):
   """Obtine pozitia capului din nasul"""
   if not face_landmarks:
       return None
   nose = face_landmarks.landmark[1]
   return [nose.x, nose.y, nose.z]

def toggle_eye_detection(ear_value):
   """Sistema de toggle pentru controlul prin ochi"""
   global eye_toggle_state, eyes_closed_start_time
   
   current_time = time.time()
   eyes_are_closed = ear_value < 0.22
   
   if eyes_are_closed:
       if eyes_closed_start_time is None:
           eyes_closed_start_time = current_time
       else:
           elapsed = current_time - eyes_closed_start_time
           if elapsed >= TOGGLE_DURATION:
               eye_toggle_state = 1 - eye_toggle_state
               eyes_closed_start_time = None
   else:
       if eyes_closed_start_time is not None:
           eyes_closed_start_time = None
   
   return eye_toggle_state

r"""
    
        4       8    12   16   20
        \       |     |    |    |
         3      7    11   15   19  
          \     |     |    |    |
           2    6    10   14   18
            \   |     |    |    |
             1  5     9   13   17
              \ |    /|   /    /
               \|   / |  /    /
                    0 
                
"""

def is_hand_closed(hand_landmarks):
   """Detectia inchiderii mainii"""
   if not hand_landmarks:
       return False
   
   lm = hand_landmarks.landmark
   
   # Verifica degetul mare si index
   thumb_closed = lm[4].y > lm[3].y
   index_closed = lm[8].y > lm[5].y
   
   return thumb_closed or index_closed

# Configurare camera
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
camera.set(cv2.CAP_PROP_FPS, 20)
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

def main_program():
   with mp_holistic.Holistic(
       min_detection_confidence=0.3,
       min_tracking_confidence=0.2,
       model_complexity=0,
       smooth_landmarks=True,
       refine_face_landmarks=True
   ) as holistic:
       
       try:
           while camera.isOpened():
               success, image = camera.read()
               if not success:
                   continue

               # Procesare frame
               image = cv2.flip(image, 1)
               rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
               results = holistic.process(rgb)
               
               # Procesare fata si cap
               if results.face_landmarks:
                   fl = results.face_landmarks.landmark
                   
                   # Pozitia capului
                   head_pos = get_head_position(results.face_landmarks)
                   if head_pos:
                       last_values["cap"] = head_pos
                       osc.send_message("/cap", head_pos)
                   
                   # Ochi
                   left_ear = get_eye_ratio(fl, LEFT_EYE)
                   right_ear = get_eye_ratio(fl, RIGHT_EYE)
                   avg_ear = (left_ear + right_ear) / 2
                   
                   eyes_state = toggle_eye_detection(avg_ear)
                   last_values["ochi"] = eyes_state
                   osc.send_message("/ochi", eyes_state)
               else:
                   # Trimite valori backup
                   osc.send_message("/cap", last_values["cap"])
                   osc.send_message("/ochi", last_values["ochi"])
                   global eyes_closed_start_time
                   eyes_closed_start_time = None
               
               # Mana stanga 
               if results.right_hand_landmarks:
                   wrist = results.right_hand_landmarks.landmark[0]
                   pos = [wrist.x, wrist.y, wrist.z]
                   
                   last_values["manaStanga"] = pos
                   osc.send_message("/manaStanga", pos)
                   
                   closed = is_hand_closed(results.right_hand_landmarks)
                   hand_state = 0 if closed else 1
                   last_values["manaStangaInchisa"] = hand_state
                   osc.send_message("/manaStangaInchisa", hand_state)
               else:
                   osc.send_message("/manaStanga", last_values["manaStanga"])
                   osc.send_message("/manaStangaInchisa", last_values["manaStangaInchisa"])
               
               # Mana dreapta
               if results.left_hand_landmarks:
                   wrist = results.left_hand_landmarks.landmark[0]
                   pos = [wrist.x, wrist.y, wrist.z]
                   
                   last_values["manaDreapta"] = pos
                   osc.send_message("/manaDreapta", pos)
                   
                   closed = is_hand_closed(results.left_hand_landmarks)
                   hand_state = 0 if closed else 1
                   last_values["manaDreaptaInchisa"] = hand_state
                   osc.send_message("/manaDreaptaInchisa", hand_state)
               else:
                   osc.send_message("/manaDreapta", last_values["manaDreapta"])
                   osc.send_message("/manaDreaptaInchisa", last_values["manaDreaptaInchisa"])
               
       except KeyboardInterrupt:
           pass
       
   camera.release()

if __name__ == "__main__":
   main_program()
   cv2.destroyAllWindows()
