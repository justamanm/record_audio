import os
import sys
import time
import wave
import numpy as np
import array
import sounddevice as sd
from scipy.io import wavfile
import soundfile


class MyException(Exception):
    """
    �Զ�����쳣��
    """
    def __init__(self, *args):
        self.args = args


def preliminary_instruction():
    """
    �������� sounddevice ��ѯ������ز���
    :return:
    """
    # ���Ȼ�ȡ�뵱ǰ�������ӵ������豸������Ϣ
    drivers_tuple = sd.query_hostapis()
    print(drivers_tuple)  # ����һ����������������Ϣ��Ԫ��, Ԫ���ÿ��Ԫ��, ��һ�����ֵ�, ������ÿ����������ϸ��Ϣ

    for driver_msg_dict in drivers_tuple:
        # �ܹ���ȡÿ������������
        print(driver_msg_dict['name'], end=", ")  # MME, Windows DirectSound, ASIO, Windows WASAPI, Windows WDM-KS,

    # ��ѯ��ǰ�������õ���������
    devices_list = sd.query_devices()  # ����һ���б�

    # ÿ���豸��Ϣ, ���ֵ���ʽ����
    for device_msg_dict in devices_list:
        print(device_msg_dict)


# ������������, �Ǹ���������������, ��ȡ������������ �� id, ���� ��� �� ���� ��������
def get_input_device_id_by_name(channel_name):
    """
    ����: ����������������, ��ȡ ���� ���� id
    :return: ������������id
    """

    devices_list = sd.query_devices()
    for index, device_msg_dict in enumerate(devices_list):
        if channel_name == device_msg_dict["name"] and device_msg_dict["max_input_channels"] > 0:
            return index
    else:
        raise MyException("�Ҳ������豸!!!")


def get_output_device_id_by_name(channel_name):
    """
    ����: ����������������, ��ȡ ��� ���� id
    :return: �����������id
    """

    devices_list = sd.query_devices()
    for index, device_msg_dict in enumerate(devices_list):
        if channel_name == device_msg_dict["name"] and device_msg_dict["max_output_channels"] > 0:
            return index
    else:
        raise MyException("�Ҳ������豸!!!")


def read_data(audio_file_path, audio_channels):
    # wav��ʽ�ļ��� raw(pcm) ��ʽ���ֿ�, ��ͬ��ʽ, ��ȡ���������ݵķ�ʽ��һ��
    if audio_file_path.endswith(".wav"):
        data_array, sample_rate = soundfile.read(audio_file_path)
        return data_array

    elif audio_file_path.endswith(".pcm") or audio_file_path.endswith(".raw"):
        # ��һ����Ƶ�ļ�, �� raw(pcm) ��ʽΪ��
        data_array = array.array('h')
        with open(audio_file_path, "rb") as f:
            data_array.frombytes(f.read())

        # ����������, �������з�(���õ���Ƶ��˫����)
        data_array = data_array[::audio_channels]  # �м�������, �зֵĲ������Ǽ�, �������ܵ����г���һ������
        return data_array


def play_audio_file(audio_file_path, channel_id, audio_channels, sample_rate):

    # ������Ĭ�ϵ��������, ��Ϊ �Լ��趨������
    # sd.default.device ��һ���б�, ��һ��Ԫ����: Ĭ�ϵ������豸id;    �ڶ�����Ĭ�ϵ�����豸id
    sd.default.device[1] = channel_id

    # ��ѡ����, һ������, һ��������, ���⻹��һ��: blocking=True, ������, ���ʾ������ϵ�ǰ��Ƶ�����½��г���
    data_array = read_data(audio_file_path, audio_channels)
    sd.play(data_array, sample_rate)
    sd.wait()  # ��ʾ�ȵ�����Ƶ�ļ��������֮�������½��г���
    # time.sleep(20)  # ʹ�� time.sleep() ---> ���߼���, ��Ƶ�ļ��Ͳ��ż���, ʱ���Լ�����

    # ע: ���û�� �������� ����ʱ����, �����ֻ��һ������, ���Ქ����Ƶ


# ʹ�� sounddevice_example ¼����Ƶ, ��ʾҲ�����ö����
def do_record(channel_id, file_path):
    # ��������Ĭ��¼������id, id��ͬ, ���õ�¼������Ҳ�᲻ͬ, �� ����һ��, Ҳ֧�� �����+���߳�, �������ͬʱ¼��
    sd.default.device[0] = channel_id

    # �ٵ��ú���¼��
    sample_rate = 44100  # ��Ƶ������
    length = 10  # ʱ��, ��λ��
    record_data = sd.rec(frames=length*sample_rate, samplerate=sample_rate, channels=1, blocking=True)  # blocking=True, �ܹ���¼��ֱ��ʱ��

    wavfile.write(file_path, sample_rate, record_data)


# ��¼�߲�
def play_and_record(input_channel_id, output_channel_id, play_audio_file_path, rec_file_path, play_audio_channels=1,
                    play_audio_fs=44100, rec_file_channels=1):

    # ��������Ĭ���������������
    sd.default.device[0] = input_channel_id
    sd.default.device[1] = output_channel_id

    # ��ʼ��¼�߲�
    data_array = read_data(play_audio_file_path, play_audio_channels)
    rec_data = sd.playrec(data=data_array, samplerate=play_audio_fs, channels=rec_file_channels, blocking=True)

    # �洢¼���ļ�
    wavfile.write(rec_file_path, play_audio_fs, rec_data)


if __name__ == "__main__":
    preliminary_instruction()
    # file_path = r"F:\CloudMusic\download\FIRBetterLife.raw"
    file_path = r"F:\CloudMusic\download\EpicScoreFireHead.raw"
    output_id = get_output_device_id_by_name("����/���� (Realtek High Definition Audio(SST))")
    rec_file_path = os.getcwd() + "\\test_record.wav"
    input_id = get_input_device_id_by_name("��˷����� (Realtek High Definition Audio(SST))")

    # play_audio_file(rec_file_path, output_id, 1, 44100)  # ֻ����
    # do_record(channel_id, file_path)  # ֻ¼��

    # play_and_record(input_id, output_id, file_path, rec_file_path, play_audio_channels=2)  # ��¼�߲�

    # file_path = sys.argv[1]
    # output_id = int(sys.argv[2])
    # audio_channels = int(sys.argv[3])
    # fs = int(sys.argv[4])
    # play_audio_file(file_path, output_id, audio_channels, fs)  # ����shell����, ����̶�������������


