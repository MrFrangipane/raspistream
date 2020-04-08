import os
import logging
import subprocess


_ALSA_SNOOP_NAME = 'BufferedPiSound'


class Runner:

    def __init__(self, url='dummy://'):
        self.url = url

        self.cam_exposure = 'backlight'
        self.cam_brightness = 55
        self.cam_white_balance = 'auto'

        self.vid_framerate = 8
        self.vid_resolution = 512, 288

        self.aud_rate = 48000
        self.aud_input = 'hw:0,0'
        self.aud_bitrate = 128
        self.aud_channels = 2
        self.aud_buffer_size = 2048
        self.aud_thread_queue = 1024

        self.total_bitrate = 1024

        self._vid_width = None
        self._vid_height = None
        self._vid_bitrate = None
        self._vid_gop_size = None

    def _setup_asoundrc(self):
        filepath_asouncrd = os.path.expanduser('~/.asoundrc')
        filepath_asouncrd_bakcup = filepath_asouncrd + '.backup'

        if os.path.exists(filepath_asouncrd) and not os.path.exists(filepath_asouncrd_bakcup):
            os.rename(filepath_asouncrd, filepath_asouncrd_bakcup)

        with open(filepath_asouncrd, 'w+') as f_asoundrc:
            f_asoundrc.write('\n'.join([
                'pcm.{_aud_alsa_input} {{',
                '  type dsnoop',
                '  ipc_key 1026',
                '  slave {{',
                '    pcm "{aud_input}"',
                '    channels {aud_channels}',
                '    buffer_size {aud_buffer_size}',
                '    rate {aud_rate}',
                '  }}',
                '}}'
            ]).format(**vars(self)))

    def _call(self):
        command = " ".join([
            'raspivid',
            '-o - -t 0',
            '-fps {vid_framerate} -g {_vid_gop_size}',
            '-w {_vid_width} -h {_vid_height}',
            '-b {_vid_bitrate}',
            '-br {cam_brightness} -awb {cam_white_balance} -ex {cam_exposure}',
            '-p 180,160,512,288'
            '|',
            'ffmpeg',
            '-f alsa -ac 2 -thread_queue_size {aud_thread_queue} -use_wallclock_as_timestamps 1',
            '-i {_aud_alsa_input}',
            '-f h264 -r {vid_framerate} -thread_queue_size {aud_thread_queue}',
            '-i - -c:v copy -c:a libfdk_aac -b:a {aud_bitrate}k -tune zerolatency',
            '-bufsize {total_bitrate}k -maxrate {total_bitrate}k',
            '-f flv "{url}"'
        ]).format(**vars(self))

        logging.info(command)

        self._process = subprocess.call(command, shell=True)

    def run(self):
        self._aud_alsa_input = _ALSA_SNOOP_NAME
        self._vid_gop_size = self.vid_framerate * 2
        self._vid_bitrate = self.total_bitrate - self.aud_bitrate
        self._vid_width, self._vid_height = self.vid_resolution

        self._setup_asoundrc()
        self._call()
