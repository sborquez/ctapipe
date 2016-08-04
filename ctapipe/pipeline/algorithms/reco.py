from time import sleep
import threading
import subprocess
import os
from ctapipe.core import Component
from traitlets import Unicode
from ctapipe.pipeline.algorithms.build_command import build_command


class Reco(Component):


    executable = Unicode('/tmp', help='directory contianing data files').tag(
        config=True, allow_none=False)
    out_extension  = 'recoevent'
    output_dir = Unicode( help='directory contianing produced files').tag(
        config=True, allow_none=False)

    def init(self):
        if not os.path.exists(self.output_dir):
            try:
                os.mkdir(self.output_dir)
            except OSError:
                self.log.info("{} : could not create output directory {}"
                    .format(self.section_name, self.output_dir))
                return False
        return True

    def run(self, input_file):
        cmd, output_file = build_command(self.executable, input_file,
             self.output_dir, self.out_extension)
        proc = subprocess.Popen(cmd)
        proc.wait()
        return output_file

    def finish(self):
        self.log.info('--- {} finish ---'.format(self.section_name))
