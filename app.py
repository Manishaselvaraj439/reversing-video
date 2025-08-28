import cv2
import speech_recognition as sr
import pyttsx3
import threading
import sys

engine = pyttsx3.init()
r = sr.Recognizer()

# ✅ Adjust microphone sensitivity for soft/slow voice
r.energy_threshold = 100
r.dynamic_energy_threshold = True
r.pause_threshold = 0.5

playing = True
speed = 30
running = True
cartoon_mode = False
bw_mode = False

def cartoonize(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255,
                                  cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(frame, 9, 250, 250)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon

def listen_command():
    global playing, speed, running, cartoon_mode, bw_mode
    while running:
        with sr.Microphone(device_index=1) as source:
            print("Say a command (reverse / start / stop / fast / slow / normal / cartoon / black and white / exit)...")
            audio = r.listen(source, phrase_time_limit=4)
        try:
            command = r.recognize_google(audio).lower()
            print("You said:", command)

            if "stop" in command:
                engine.say("Video stopped")
                engine.runAndWait()
                playing = False

            elif "start" in command:
                engine.say("Video started")
                engine.runAndWait()
                playing = True

            elif "fast" in command:
                engine.say("Fast forward activated")
                engine.runAndWait()
                speed = 10

            elif "slow" in command:
                engine.say("Slow motion activated")
                engine.runAndWait()
                speed = 120   # slow motion effect

            elif "normal" in command:
                engine.say("Normal speed activated")
                engine.runAndWait()
                speed = 30
                cartoon_mode = False
                bw_mode = False

            elif "cartoon" in command:
                engine.say("Cartoon mode activated")
                engine.runAndWait()
                cartoon_mode = True
                bw_mode = False

            elif "black and white" in command or "grayscale" in command:
                engine.say("Black and White mode activated")
                engine.runAndWait()
                bw_mode = True
                cartoon_mode = False

            elif "exit" in command or "quit" in command:
                engine.say("Exiting now")
                engine.runAndWait()
                running = False
                break

        except:
            pass

# --- Main ---
with sr.Microphone(device_index=1) as source:
    print("Say a command (reverse)...")
    audio = r.listen(source, phrase_time_limit=4)
try:
    command = r.recognize_google(audio).lower()
except:
    command = ""

if "reverse" in command:
    engine.say("Reversing the video now")
    engine.runAndWait()
    
    video_path = r"C:\\Users\\heyra\\OneDrive\\Desktop\\myvideoapp\\myvideo.avi"
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video file")
        sys.exit()
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()

    frames.reverse()

    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('reversed_video.avi', fourcc, fps, (width, height))
    for f in frames:
        out.write(f)
    out.release()
    print("Video reversed successfully!")

    # ✅ Start listening in background thread
    threading.Thread(target=listen_command, daemon=True).start()

    # ✅ Play reversed video
    cap = cv2.VideoCapture('reversed_video.avi')
    while running:
        if playing:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            if cartoon_mode:
                frame = cartoonize(frame)
            elif bw_mode:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            cv2.imshow("Reversed Video", frame)

        if cv2.waitKey(speed) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
else:
    engine.say("Command not recognized")
    engine.runAndWait()
