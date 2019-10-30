import argparse
import asyncio
import sys
import os
import toml
from videocutter import version, Controller


def main():
    parser = get_args_parser()

    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    if args.config_file is None:
        parser.print_help()
        parser.exit()

    config_file = args.config_file
    if not os.path.exists(config_file):
        print("Config file not found")
        parser.exit()

    with open(config_file, mode="r") as cf:
        config_object = toml.load(cf)

    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    controller = Controller(config_object)
    loop.run_until_complete(controller.do_the_thing())
    loop.close()


def get_args_parser():
    parser = argparse.ArgumentParser(description='Video cutter via ffmpeg.', prog='python vcut.py')
    required_params = parser.add_argument_group('required arguments')
    required_params.add_argument('-c, --config', help="the config file to use for the video cutting.",
                                 default=None,
                                 dest='config_file', required=True)
    parser.add_argument('--version', action='version', version=f'HSS Bearing ANN {version}')

    return parser


if __name__ == '__main__':
    main()
