import sys
import cv2
import numpy as np
from tqdm import tqdm
import scipy.signal
from scipy.signal import resample


def stabilize_video_correlation(input_video, output_video):
    # Open the input video file
    cap = cv2.VideoCapture(input_video)

    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Get the dimensions of the frames
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    # Get the total number of frames in the video
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, frame_rate,
                          (frame_width, frame_height))

    # Initialize the previous frame
    ret, base_frame = cap.read()
    if not ret:
        return

    out.write(base_frame)

    for frame_num in tqdm(range(1, 60 * 5 * 0 or frame_count)):
        ret, frame = cap.read()
        if not ret:
            break

        # Align the current frame with the first frame using cross-correlation
        shift = align_frames(base_frame, frame)

        # Apply vertical shift to stabilize the frame
        stabilized_frame = np.roll(frame, int(np.round(shift)), axis=0)

        # Write the stabilized frame to the output video
        out.write(stabilized_frame)

        # this is terrible: don't go frame-by-frame, go from first frame to this
        # base_frame = stabilized_frame

    out.release()
    cap.release()


def align_frames(frame1, frame2, up=None):
    if up is None:
        lags = scipy.signal.correlation_lags(frame1.shape[0], frame2.shape[0])
    else:
        lags = scipy.signal.correlation_lags(int(frame1.shape[0] * up),
                                             int(frame2.shape[0] * up)) / up

    gray_frame1 = frame1[:, :, 2]  # use red
    gray_frame2 = frame2[:, :, 2]
    corr_peaks = []
    width = gray_frame2.shape[1]
    for i in range(width // 3):  # left third
        a = gray_frame1[:, i].astype(float)
        b = gray_frame2[:, i].astype(float)
        if up is not None:
            # TODO FIXME cache upsampled frame1 somehow
            a = resample(a, len(a) * up, window='blackman')

            b = resample(b, len(b) * up, window='blackman')
        c = scipy.signal.correlate(a, b)
        corr_peaks.append(lags[np.argmax(c)])

    return np.mean(corr_peaks) / (1 if up is None else up)


if __name__ == "__main__":
    input_video = sys.argv[1] if sys.argv[1:] else "input.mp4"
    output_video = sys.argv[2] if sys.argv[2:] else "output.mp4"

    stabilize_video_correlation(input_video, output_video)
