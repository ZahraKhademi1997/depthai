import depthai_sdk
from depthai_sdk import OakCamera, RecordType
from depthai_sdk.args_parser import ArgsParser
from depthai_sdk.components.parser import mono_resolution
import argparse
import datetime


parser = argparse.ArgumentParser()
parser.add_argument('--recordStreams', action='store_true', help="Record frames to file")
parser.add_argument('--saveStreamsTo', type=str, help="Save frames to directory", default="/home/zahra/Desktop/data_collection/")
args= ArgsParser.parseArgs(parser=parser)

with OakCamera(args=args) as oak:
    # cams = oak.create_all_cameras()
    # left = oak.camera('left')
    # right = oak.camera('right')
    
    left = oak.create_camera('left')
    # right = oak.create_camera('right')
    right = None
    # if left is not None and right is not None:
    if left is not None:
        # stereo = oak.create_stereo(left=left, right=right)
        stereo = oak.create_stereo(left=left)
        oak.visualize(stereo)
    # Sync & save all streams
    # if args["recordStreams"]:
    #     oak.record(cams, args["saveStreamsTo"], RecordType.VIDEO_LOSSLESS).configure_syncing(True, 50)
    # oak.visualize(cams, fps=True)
    # if args["recordStreams"]:
    #     # oak.record([left, right], args["saveStreamsTo"], RecordType.VIDEO).configure_syncing(True, 50)
    #     oak.record([left, right], args["saveStreamsTo"], RecordType.VIDEO)
    # oak.visualize([left, right], fps=True)
    
    if args["recordStreams"] and left is not None:
        oak.record([left], args["saveStreamsTo"], RecordType.VIDEO)  # Record only the left camera
        oak.visualize(left, fps=True)

    oak.start(blocking=True)
