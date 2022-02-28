from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
from landmark import detect_landmarks, normalize_landmarks, plot_landmarks
from mediapipe.python.solutions.face_detection import FaceDetection
import numpy as np

# cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
Left_shadow = [190,189,56,221,28,222,27,223,29,224,30,225,113,247,246]
Right_shadow = [414,413,286,441,258,442,257,443,259,444,260,445,467,342,263]
class VideoProcessor:
	def recv(self, frame):
         frm = frame.to_ndarray(format="bgr24")
         ret_landmarks = detect_landmarks(frm, True)
         height, width, _ = frm.shape
         feature_landmarks = None
         feature_landmarks_left = normalize_landmarks(ret_landmarks,height,width,Left_shadow)
         mask_left = shadow_mask(frm,feature_landmarks_left,[0, 0, 100])
         feature_landmarks_right = normalize_landmarks(ret_landmarks,height,width,Right_shadow)
         mask_right = shadow_mask(frm,feature_landmarks_right,[0, 0, 100])
         mask  = mask_left+mask_right
         output = cv2.addWeighted(frm,1.0,mask,0.4, 0.0)
         print('here 1')
         return av.VideoFrame.from_ndarray(output, format='bgr24')


def shadow_mask(src: np.ndarray, points: np.ndarray, color: list):
    """
        Given a src image, points of lips and a desired color
        Returns a colored mask that can be added to the src
        """
    print('here 2')   
    mask = np.zeros_like(src)  # Create a mask
    mask = cv2.fillPoly(mask, [points], color)  # Mask for the required facial feature
        # Blurring the region, so it looks natural
        # TODO: Get glossy finishes for lip colors, instead of blending in replace the region
    mask = cv2.GaussianBlur(mask, (7, 7), 5)
    return mask

ctx =webrtc_streamer(
    key="example",
    video_processor_factory=VideoProcessor,
    rtc_configuration={ # Add this line
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    }
)
