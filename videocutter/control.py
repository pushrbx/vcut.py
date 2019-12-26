from ffmpeg import FFmpeg
import os
import subprocess
import json
import math


def ceildiv(a, b):
    return int(math.ceil(a / float(b)))


class Controller(object):
    def __init__(self, config: dict):
        if len(config) == 0:
            raise ValueError('config should not be empty')

        if not self.valid(config):
            raise ValueError('invalid configuration')

        self.config = config

    def valid(self, config: dict) -> bool:
        if 'from' not in config:
            return False

        if 'duration' not in config:
            return False

        if 'video_file_path' not in config:
            return False

        if 'use_copy' not in config:
            return False

        if 'output_file_path' not in config:
            return False

        if 'ffmpeg_path' not in config:
            return False

        if 'ffprobe_path' not in config:
            return False

        if 'chunk_it' not in config:
            return False

        if type(config['from']) is not str\
                or type(config['duration']) is not str\
                or type(config['video_file_path']) is not str\
                or type(config['output_file_path']) is not str\
                or type(config['ffmpeg_path']) is not str\
                or type(config['ffprobe_path']) is not str\
                or type(config['chunk_it']) is not bool:
            return False

        if config['chunk_it'] and not config['ffprobe_path']:
            return False

        if not os.path.exists(config['video_file_path']):
            raise IOError(f"File not found: {config['video_file_path']}")

        if type(config['use_copy']) is not bool:
            return False

        if config['chunk_it'] and not os.path.exists(config['ffprobe_path']):
            raise IOError(f"File not found: {config['ffprobe_path']}")

        return True

    async def cut_video(self, cut_from, duration, video_file_path, output_path, use_copy):
        if self.config['ffmpeg_path'] is not None and self.config['ffmpeg_path'] != '':
            ffmpeg = FFmpeg(self.config['ffmpeg_path'])
        else:
            ffmpeg = FFmpeg()

        ffmpeg = ffmpeg.option('ss', cut_from).input(
            os.path.abspath(video_file_path))

        if use_copy:
            ffmpeg = ffmpeg.output(output_path, c='copy', t=duration)
        else:
            ffmpeg = ffmpeg.output(output_path, t=duration)

        @ffmpeg.on('start')
        def on_start(arguments):
            print('ffmpeg arguments: ', arguments)

        @ffmpeg.on('stderr')
        def on_stderr(line):
            print('ffmpeg out:', line)

        @ffmpeg.on('completed')
        def on_completed():
            print('Completed')

        @ffmpeg.on('terminated')
        def on_terminated():
            print('Terminated')

        @ffmpeg.on('error')
        def on_error(code):
            print('Error:', code)

        await ffmpeg.execute()

    def get_video_info(self, video_file_path):
        ffprobe_path = self.config['ffprobe_path']
        result = subprocess.Popen([ffprobe_path,
                                   '-print_format',
                                   'json',
                                   '-loglevel',
                                   'quiet',
                                   '-show_streams',
                                   video_file_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = "".join([x.decode() for x in result.stdout.readlines()])
        if result and result.startswith('{'):
            video_info = json.loads(result)
        else:
            video_info = {}

        return video_info

    async def do_the_thing(self) -> None:
        cut_from = self.config['from']
        video_file_path = self.config['video_file_path']
        output_file = self.config['output_file_path']
        duration = self.config['duration']
        use_copy = self.config['use_copy']
        chunk_it = self.config['chunk_it']

        if not chunk_it:
            await self.cut_video(cut_from, duration, video_file_path, output_file, use_copy)
        else:
            video_info = self.get_video_info(video_file_path)
            if len(video_info.keys()) == 0:
                print('Could not read video info.')
                return
            video_stream_info = video_info['streams'][0]
            video_duration = float(video_stream_info['duration'])
            chunk_duration = float(duration)

            chunk_count = ceildiv(video_duration, chunk_duration)
            if chunk_count == 1:
                print("Video length is less than thetarget split length.")
                return

            try:
                filebase = ".".join(output_file.split(".")[:-1])
                fileext = output_file.split(".")[-1]
            except IndexError as e:
                raise IndexError("No . in filename. Error: " + str(e))

            for n in range(0, chunk_count):
                if n == 0:
                    cut_from = 0
                else:
                    cut_from = chunk_duration * n

                await self.cut_video(f"{cut_from}", duration, video_file_path, f'{filebase}-{n+1}.{fileext}', use_copy)
