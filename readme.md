# Simple ffmpeg video cutter

This is a simple console application which helps a bit with
cutting videos (mp4) with ffmpeg. It takes a toml configuration file in which you can set the start time, 
the encoding duration, the source file, the target file, the path to ffmpeg,
and whether you want it to re-encode the video or just copy it.

## Usage

Clone the repo, create and activate a virtual env in your favourite terminal/console, then install dependencies:
```bash
pip install -r requirements.txt
```

Run the app:

```
python vcut.py -c <yourconfigfile.toml>
```

You can find the structure and the required fields in the `config.sample.toml` file.