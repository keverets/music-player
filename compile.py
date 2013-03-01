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
	if sys.platform == "darwin":
		if LinkPython: options += ["-framework","Python"]
		else: options += ["-undefined", "dynamic_lookup"]
		sysExec(
			["libtool", "-dynamic", "-o", outfile] +
			infiles +
			options + 
			["-lc"]
		)
	else:
		if LinkPython: options += ["-lpython2.7"]
		sysExec(
			["c++"] +
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
	cppfiles = [f for f in files if os.path.splitext(f)[1] == ".cpp"]
	files = [f for f in files if f not in cppfiles]
	if cppfiles:
		cppoptions = ["-std=c++11"]
		sysExec(["c++"] + options + cppoptions + CFLAGS + ["-c"] + cppfiles)
	sysExec(["cc"] + options + CFLAGS + ["-c"] + files)

sysExec(["mkdir","-p","build"])
os.chdir("build")

staticChromaprint = False

ffmpegFiles = ["../ffmpeg.c"] + \
	glob("../ffmpeg_*.cpp") + \
	(glob("../chromaprint/*.cpp") if staticChromaprint else [])

cc(
	ffmpegFiles,
	[
		"-DHAVE_CONFIG_H",
		"-D__STDC_LIMIT_MACROS",
		"-g",
	] +
	(["-I", "../chromaprint"] if staticChromaprint else [])
)

link(
	"../ffmpeg.so",
	[os.path.splitext(os.path.basename(fn))[0] + ".o" for fn in ffmpegFiles],
	[
		"-lavutil",
		"-lavformat",
		"-lavcodec",
		"-lswresample",
		"-lportaudio",
	] +
	([] if staticChromaprint else ["-lchromaprint"])
)

if sys.platform == "darwin":
	guiCocoaCommonFiles = glob("../mac/MusicPlayer/*.m")
	cc(guiCocoaCommonFiles,	[])
	link(
		"../_guiCocoaCommon.dylib",
		[os.path.splitext(os.path.basename(fn))[0] + ".o" for fn in guiCocoaCommonFiles],
		["-framework", "Cocoa"]
	)

