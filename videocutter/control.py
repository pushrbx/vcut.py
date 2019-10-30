from ffmpeg import FFmpeg
import os


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

        if type(config['from']) is not str\
                or type(config['duration']) is not str\
                or type(config['video_file_path']) is not str\
                or type(config['output_file_path']) is not str\
                or type(config['ffmpeg_path']) is not str:
            return False

        if not os.path.exists(config['video_file_path']):
            raise IOError(f"File not found: {config['video_file_path']}")

        if type(config['use_copy']) is not bool:
            return False

        return True

    async def do_the_thing(self) -> None:
        if self.config['ffmpeg_path'] is not None and self.config['ffmpeg_path'] != '':
            ffmpeg = FFmpeg(self.config['ffmpeg_path'])
        else:
            ffmpeg = FFmpeg()

        ffmpeg = ffmpeg.option('ss', self.config['from']).input(
            os.path.abspath(self.config['video_file_path']))

        output_file = self.config['output_file_path']
        duration = self.config['duration']
        if self.config['use_copy']:
            ffmpeg = ffmpeg.output(output_file, c='copy', t=duration)
        else:
            ffmpeg = ffmpeg.output(output_file, t=duration)

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
