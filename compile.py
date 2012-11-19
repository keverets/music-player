#!/usr/bin/python
# MusicPlayer, https://github.com/albertz/music-player
# Copyright (c) 2012, Albert Zeyer, www.az2000.de
# All rights reserved.
# This code is under the 2-clause BSD license, see License.txt in the root directory of this project.

import os, sys
from glob import glob
os.chdir(os.path.dirname(__file__))

def sysExec(cmd):
    print " ".join(cmd)
    r = os.system(" ".join(cmd))
    if r != 0: sys.exit(r)

LinkPython = False
UsePyPy = False

def link(outfile, infiles, options):
	if not LinkPython:
		options += ["-undefined", "dynamic_lookup"]
	if sys.platform == "darwin":
		if LinkPython: options += ["-framework","Python"]
		sysExec(
			["libtool", "-dynamic", "-o", outfile] +
			infiles +
			options + 
			["-lc"]
		)
	else:
		if LinkPython: options += ["-lpython2.7"]
		sysExec(
			["ld"] +
			["-L/usr/local/lib"] +
			infiles +
			options +
			["-lc"] +
			["-shared", "-o", outfile]
		)

CFLAGS = os.environ.get("CFLAGS", "").split()

def cc(files, options):
	if UsePyPy:
		options += ["-I", "/usr/local/Cellar/pypy/1.9/include"]
	else:
		options += [
			"-I", "/System/Library/Frameworks/Python.framework/Headers/", # mac
			"-I", "/usr/include/python2.7", # common linux/unix
		]
	options += ["-fpic"]
	sysExec(["cc"] + options + CFLAGS + ["-c"] + files)

sysExec(["mkdir","-p","build"])
os.chdir("build")

staticChromaprint = False
UseSwResample = True

ffmpegFiles = ["../ffmpeg.c"] + \
	(glob("../chromaprint/*.cpp") if staticChromaprint else [])

cc(
	ffmpegFiles,
	[
		"-std=c99",
		"-DHAVE_CONFIG_H",
		"-g",
	] +
	(["-DUSE_SWRESAMPLE"] if UseSwResample else []) +
	(["-I", "../chromaprint"] if staticChromaprint else [])
)

link(
	"../ffmpeg.so",
	[os.path.splitext(os.path.basename(fn))[0] + ".o" for fn in ffmpegFiles],
	[
		"-lavutil",
		"-lavformat",
		"-lavcodec",
		"-lportaudio",
	] +
	(["-lswresample"] if UseSwResample else []) +
	([] if staticChromaprint else ["-lchromaprint"])
)

