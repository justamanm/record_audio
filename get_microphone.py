import time

import pyaudio
import wave
import numpy as np

from remove_noise import process_noise




class Audio:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 48000
        self.RECORD_SECONDS = 10
        self.WAVE_OUTPUT_FILENAME = "cache.wav"

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)

    def save(self, filename, data):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(data)
        wf.close()

    def start(self):
        frames = []
        threshhold = 1800
        threshhold = 300
        while True:
            print("*" * 10, "开始录音：请在5秒内输入语音")
            frames = []
            num = int(self.RATE / self.CHUNK * self.RECORD_SECONDS)
            print(num)
            # num *= 2
            time.clock()
            for i in range(0, num):
                data = self.stream.read(self.CHUNK)
                # print(data)
                # # 判断data
                audio_data = np.fromstring(data, dtype=np.short)
                # large_sample_count = np.sum(audio_data > 800)
                temp = np.max(audio_data)
                print('', )
                if temp > threshhold:
                    print("检测到信号，当前值：" + str(temp))
                else:
                    print("声音过小，请调大音量（当前值：" + str(temp) + "）")
                frames.append(data)
            print(time.clock())
            print("*" * 10, "录音结束\n")
            break

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        str_data = b''.join(frames)
        fs = self.RATE
        wave_data = process_noise(str_data, fs)

        wave_data = np.fromstring(wave_data, dtype=np.short)  # 将声音文件数据转换为数组矩阵形式
        wave_data.shape = -1, self.CHANNELS  # 按照声道数将数组整形，单声道时候是一列数组，双声道时候是两列的矩阵
        wave_data = wave_data.T  # 将矩阵转置

        self.save(self.WAVE_OUTPUT_FILENAME, wave_data)
        self.save("cache_origin.wav", str_data)
        return wave_data, self.RATE

    def run(self):
        self.status = int(input("现在开始吗(1/0)? :"))
        if self.status:
            return self.start()
        else:
            return


if __name__ == '__main__':
    a = Audio()
    a.run()
