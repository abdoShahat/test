# from streamlit_webrtc import webrtc_streamer, RTCConfiguration
from turtle import color
import av
import cv2
from landmark import detect_landmarks, normalize_landmarks, plot_landmarks
from mediapipe.python.solutions.face_detection import FaceDetection
import numpy as np
from streamlit_webrtc import AudioProcessorBase,RTCConfiguration,VideoProcessorBase,WebRtcMode,webrtc_streamer
from aiortc.contrib.media import MediaPlayer
from PIL import ImageColor
import streamlit as st

# cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
# Left_shadow = [190,189,56,221,28,222,27,223,29,224,30,225,113,247,246]
Left_shadow = [189,221,222,223,224,225,113,130,246,161,160,159,158,157,173]
# Right_shadow = [414,413,286,441,258,442,257,443,259,444,260,445,467,342,263]
# Right_shadow = [414,413,441,442,443,444,445,342,359,467,260,259,257,258,286,463,414,441,398,414,441,384,286,414,385,258,442,386,257,443,387,259,444,388,260,445,466,467]  # left in streamlit 

Right_shadow = [413,414,442,443,444,445,342,467,260,259,257,258,286,414,384,385,386,387,388,466,263,398,414,286,384,286,258,385,258,257,386,257,259,387,259,260,388,260,467,466,467,359,263]

color = []

option = st.selectbox(
     'How would you like to be contacted?',
     ('color_1', 'color_2', 'color_3', 'color_4', 'color_5'))

if option =='color_1':
    color = [63, 64, 108] 
elif option == 'color_2':
    color = [54, 79, 115]
elif option == 'color_3':
    color = [10, 5, 120]
elif option == 'color_4':
    color = [60,60,60]
elif option == 'color_5':
    color = [105, 71, 59]
else :
    color = [45, 15, 5]


class VideoProcessor:
	def recv(self, frame):
         try:
            frm = frame.to_ndarray(format="rgb24")
            ret_landmarks = detect_landmarks(frm, True)
            height, width, _ = frm.shape
            feature_landmarks = None
            feature_landmarks_left = normalize_landmarks(ret_landmarks,height,width,Left_shadow)
            mask_left = shadow_mask(frm,feature_landmarks_left,color)
            print('color is ',color)
            feature_landmarks_right = normalize_landmarks(ret_landmarks,height,width,Right_shadow)
            mask_right = shadow_mask(frm,feature_landmarks_right,color)
            mask  = mask_left+mask_right
            output = cv2.addWeighted(frm,1.0,mask,0.4, 0.0)
            print('here 1')
            return av.VideoFrame.from_ndarray(output, format='rgb24')
         except:
             VideoProcessor


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

# ctx =webrtc_streamer(
#     key="example",
#     video_processor_factory=VideoProcessor,
#     rtc_configuration={ # Add this line
#         "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
#     }
# )

# ctx =webrtc_streamer(
#     key="example",
#     video_processor_factory=VideoProcessor,
#     rtc_configuration=RTCConfiguration(
#     {
#       "RTCIceServer": [{
#         "urls": ["stun:stun.l.google.com:19302"],
# 	"username": "user",
# 	"credential": "password",
#       }]
#     }
# )
# )

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

webrtc_ctx = webrtc_streamer(
    key="object-detection",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    video_processor_factory=VideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True
)
