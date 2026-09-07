# video_codage

This project is a motion detection interface built using Python and libraries such as OpenCV, NumPy, and Tkinter. The goal was to enable users to select a video from their file system, detect motion within it, and visualize the result with the areas of motion highlighted.

The process begins by selecting the video and converting each frame to grayscale to simplify subsequent processing. Next, the absolute difference between successive frames is calculated to detect pixel-level changes, followed by binary thresholding to isolate areas of motion. Edge detection is then used to identify these areas, and rectangles are drawn around them to highlight them. Finally, the result is displayed to the user in a new window.
