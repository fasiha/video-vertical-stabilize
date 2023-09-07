## Background and results

I took a long, 2~ish minute video of the sunset with my camera on a plank that I was also sitting on, and between the wind and my shifting weight, the video had a lot of up-down shake. And vidstab via [VidStabGui](https://github.com/hlorand/vidstabgui) couldn't stabilize it because the only sharp shapes in the frame were the horizon and the moving sun.

https://github.com/fasiha/video-vertical-stabilize/assets/37649/fe598ccb-8554-4253-b96a-0d81073e5b2f

> Above: Original video. A thin orange band separates gray clouds and a dark ocean, through which the fiery orb of the sun appears and moves through

With ChatGPT 3.5's help I cobbled together this script to vertically-stabilize it using only the left third third of the red channel ([direct link to ChatGPT session](https://chat.openai.com/share/6e72b2f0-3683-4c6c-aac6-908e76781096)). It's intended to be more for study/demo than actual reuse, but here's the output:

https://github.com/fasiha/video-vertical-stabilize/assets/37649/d12bbdf9-2dfd-4ebe-9aa9-8c7b031d7e3e

> Above: Result: same as above but much less vertical swaying

1. My first instinct was to find the row (y index) with the sharpest gradient in the left-third of the frame (the sun was in the middle/right of the frame). In short, use the y-gradient to find the horizon. This didn't stabilize well, I think because the gradient didn't yield accurate enough offsets. However, ChatGPT did a *fantastic* job with all the ffmpeg video-to-PNGs and OpenCV (gradient, video output) boilerplate. I was able to improve its output by suggesting the use of [`numpy.roll`](https://numpy.org/doc/stable/reference/generated/numpy.roll.html).
2. My long-unused digital signal processing knowledge sheepishly volunteered a suggestion: correlation? ChatGPT again filled out most of the detail, and again I suggested it use specialized functions like [`scipy.signal.correlate`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate.html) and [`scipy.signal.correlation_lags`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlation_lags.html#scipy.signal.correlation_lags) (instead of trying to convert the correlation's index into actual pixel offsets).
   1. (The code also has some unused functionality to upsample the input to get finer correlations to improve the stabilization, but once I used the full-resolution 1080p video, the resulting stabilization was acceptable, especially after downsampling to 480p.)

## Setup

If you'd like to run the script yourself, install Python ([official downloads](https://www.python.org/downloads/) but your operating system might come with it already).

I personally like using [conda](https://docs.conda.io/projects/miniconda/en/latest/) to create a virtual environment just for this project. You don't have to do this but if you want to, run the following in your command prompt (FreeCodeCamp has handbooks for [macOS/Unix](https://www.freecodecamp.org/news/command-line-for-beginners/) and [Windows](https://www.freecodecamp.org/news/command-line-commands-cli-tutorial/)):
```sh
conda create -n opencv-stabilize
conda activate opencv-stabilize
conda install -c conda-forge python
```

Next, make sure you have some dependencies installed: run the following in the same command prompt:
```sh
python -m pip install ipython scipy opencv-python-headless tqdm
```

Now, download [`gpt-stab.py`](./gpt-stab.py), `cd` into the directory you saved it, and run it like so:
```sh
python gpt-stab.py input.mp4 output.mp4
```
(You can provide the path to your `input.mp4` or just copy your real video into the same directory as the script and rename it `input.mp4` if you don't want to mess about.) This will produce `output.mp4` in the same directory.

Finally I prepared both input and output for bundling with this repo using `ffmpeg` (I install this from [Homebrew](https://brew.sh)), by speeding up 8x and reducing to 480p:
```sh
ffmpeg -i input.mp4 -vf "setpts=0.125*PTS,scale=480:-2" input-small.mp4
ffmpeg -i output.mp4 -vf "setpts=0.125*PTS,scale=480:-2" output-small.mp4
```

## Acknowledgements

I have to give a shoutout to [Simon Willison](https://fedi.simonwillison.net/@simon/111009811211160193) whose toot inspired me to dive into this little mini-project instead of just give up and accept an unstabilized video:

> One of the things that I'm really enjoying about working with LLMs is that I feel liberated from /syntax/
>
> I'm used to spending a substantial portion of my intellectual energy when I'm writing code thinking about the very specific syntactic rules of the programming language I'm working in
>
> When I'm writing with Copilot, GPT-4 or Claude I hardly spend any time thinking about that at all, which frees me up to spend more time thinking about more interesting, higher level problems instead
>
> In the past I've habitually stuck to the languages I know best - Python, JavaScript, SQL - because I'm so much more productive in a language where the syntax has been baked deep into my brain
>
> I've been spreading my wings a whole lot more over the past six months - Bash, jq, AppleScript, even Go - because syntactical minutiae is no longer a barrier for me to be productive with them
