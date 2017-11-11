#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import pyaudio
import wave
import fcntl
import termios
import sys
import os
import numpy as np
from scipy import *

FORMAT = pyaudio.paInt16
CHANNELS = 1        #モノラル
RATE = 44100        #サンプルレート
CHUNK = 2**10       #データ点数
RECORD_SECONDS = 5 #録音する時間の長さ

KEY_CODE_ENTER = 10

class  AudioStream:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            output=True )
        self.frames = []

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def input(self):
        return self.stream.read(CHUNK)

    def output(self, d):
        self.stream.write(d)

    def record(self, d):
        self.frames.append(d)
        return self.frames

# 入力を待たないキー入力チェッカー
def getkey():
    fno = sys.stdin.fileno()
    attr_old = termios.tcgetattr(fno)
    attr = termios.tcgetattr(fno)
    attr[3] = attr[3] & ~termios.ECHO & ~termios.ICANON # & ~termios.ISIG
    termios.tcsetattr(fno, termios.TCSADRAIN, attr)
    fcntl_old = fcntl.fcntl(fno, fcntl.F_GETFL)
    fcntl.fcntl(fno, fcntl.F_SETFL, fcntl_old | os.O_NONBLOCK)
    chr = 0
    try:
        # キーを取得
        c = sys.stdin.read(1)
        if len(c):
            while len(c):
                chr = (chr << 8) + ord(c)
                c = sys.stdin.read(1)
    finally:
        # stdinを元に戻す
        fcntl.fcntl(fno, fcntl.F_SETFL, fcntl_old)
        termios.tcsetattr(fno, termios.TCSANOW, attr_old)

    return chr

def resampling(frames):
    data = b''.join(frames)
    data = frombuffer(data,dtype = "int16")
    data = changePlaySpeed(data,1.8)
    data = int16(data).tostring()
    return data

def changePlaySpeed(inp,rate):
    outp = []
    for i in range(int(len(inp) / rate)):
        outp.append(inp[int(i * float(rate))])
    return array(outp)

def realtimeVoiceChanger():
    audioStream = AudioStream()
    print("終了する場合は[Enter]")
    while True:
        key = getkey()
        if key == KEY_CODE_ENTER: break
        input = audioStream.input()
        rec = audioStream.record(input)
        data = resampling(rec)
        audioStream.output(data)
        audioStream.frames = []

    del audioStream

if __name__ == '__main__':
    realtimeVoiceChanger()
