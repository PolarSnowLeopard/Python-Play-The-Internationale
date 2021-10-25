#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   mymusic.py
@Time    :   2021/10/21 14:03:09
@Author  :   YuFanWenShu
@Contact :   1365240381@qq.com

'''

# here put the import lib

import re
import numpy as np
import librosa
import IPython.display as ipd
import matplotlib.pyplot as plt
import soundfile as sf

class Music():
    def __init__(self, name=""):
        """
            Init an instance of MyMusic.

            Parameters
            ----------
                name : str, [optional]
                    Name of the music. Must be str.
        """
        #Judge the type of input.
        assert name is None or isinstance(name, str)

        self.__name = name
        self.__staff = None
        self.__wave = np.array([])
        self.__Fs = 8192
        self.__converter = Converter(self.__Fs)

    def load_staff(self,file_name):
        """
        Load the staff from a file.

        Parameters
        ----------
            file_name : str
                The file to read from.

        Returns
        -------
            state : bool
                Whether loaded the data successfully.
        """
        #Judge the input.
        assert isinstance(file_name, str), "file_name must be a string"
        assert len(file_name.split(".")) == 2, "Input error. \neg.'start.txt'"

        self.__staff = Staff(file_name)
        self.update_music()

    def save_staff(self,file_name):
        """
        Save the staff to a file.

        Parameters
        ----------
            file_name : str
                The file to save to.

        Returns
        -------
            state: bool
                Whether saved the data successfully.
        """

    def update_music(self):
        """
        Update the music(wave) by self.__staff.
        """
        self.__wave = self.__converter.gen_music(self.__staff)

    def save_music(self,file_name,file_type="wav"):
        """
        Save the music as an audio.

        Parameters
        ----------
            file_name : str
                The file to save to.
            file_type : str
                Type of the file to save to. Defaults to 'wav'
                and it means save the audio as "{file_name}.wav".

        Returns
        -------
            state : bool
                Whether successfully saved the music as an audio.
        """
        path = file_name.split(".")[0]+"."+file_type

        sf.write(path, self.__wave, self.__Fs, 'PCM_24')

    def play(self):
        """
        Play the music.
        """

    def draw_wave(self):
        """
        Draw the waveform according to self.__wave.
        """
        n = len(self.__wave)     # Number of samples.
        t = n/self.__Fs          # Range of t is [0,t]
        x = np.linspace(0, t, n)
        plt.plot(x,self.__wave)  # Draw the wave.
        plt.show()

class Staff():

    def __init__(self, file_name):
        """
        Init an instance of a Staff.

        Parameters
        ----------
            f_name : str
                The name of the file.
            f_type : str
                The type of the file.
        """

        self.__sections = []
        self.__name ,self.__type = file_name.split(".")
        self.__text = ""
        self.__rythm = 60
        self.__loop = None
        self.__supported_type = {"txt"}            # The type of file supported.

        self.read()    # Read file.

    def read(self):
        """
        Init the staff from a file.
        """
        assert self.__type in self.__supported_type, "Sorry, this type of file is not supported."

        if self.__type == "txt":
            self.read_from_txt()

    def read_from_txt(self):
        """
        Load the staff from a txt file.

        Parameters
        ----------
            file_name : str ("xxx.txt")
                The full name of the file.
        """

        file_name = self.__name + "." + self.__type
        with open(file_name, "r") as file:
            self.__text = file.read()

        re_rythm = re.compile("rythm=([0-9]*)",re.S)
        re_loop = re.compile("loop=(.*?\))",re.S)
        re_section = re.compile("(<section.*?>.*?</section>)",re.S)
        re_section_att = re.compile("<section (.*?)>(.*)</section>",re.S)

        self.__rythm = int(re_rythm.findall(self.__text)[0])  # Find the rythm.
        self.__loop = eval(re_loop.findall(self.__text)[0])
        sections = re_section.findall(self.__text)       # Find all sections.

        for section in sections:
            # Create a temp dict to save the information of this section.
            dict_att = {}

            # Find the attributions and the notes of this section.
            match = re_section_att.findall(section)

            # Add every attribute to `dict_att`.
            attributes = match[0][0].split()
            for att in attributes:
                key, value = att.split("=")
                dict_att[key] = value

            # Create a list `notes` and add every note to this list.
            notes_temp = match[0][1].split("\n")
            notes = []
            for i in range(len(notes_temp)):
                note = notes_temp[i].strip(" ")
                note = note.strip("\t")
                if note:
                    notes.append(note)

            # Create a dict to save the information of this section, and add it to `self.__section`.
            self.__sections.append({"attribute":dict_att, "notes":notes})

        # print(self.__sections)

    @property
    def sections(self):
        return self.__sections

    @property
    def rythm(self):
        return self.__rythm

    @property
    def loop(self):
        return self.__loop

class Converter():
    def __init__(self, Fs=8192):
        """
        Init an instance of Converter.

        Parameters
        ----------
            Fs : int [optional]
                The sampling rate.
        """
        self.__Fs = Fs

    def get_frequency(self,major,scale):
        """
        Calculate the Frequency.

        Parameters
        ----------
            major : int
                The major. For example, when it takes 0, it means C major.
            scale : int, range[-1,12]
                The scale. -1 means a rest, and 1 means "do", 12 means "si".

        Returns
        -------
            frequency : float
                The Frequncy calculated by the major and scale.
        """
        frequency = 440*(2**major)
        frequency = frequency*2**((scale-1)/12)
        return frequency

    def get_wave(self,major,scale,rythm=1):
        """
        Generate the wave of a note.

        Parameter
        ---------
            major : int
                The major. For example, when it takes 3, it means C major.
            scale : int, range[-1,12]
                The scale. -1 means a rest, and 1 means "do", 12 means "si".
            rythm : int
                The rythm of the note. When it takes 1.5, int means 1.5 unit-time per beat.

        Returns
        -------
            y : np.array
                The wave generated.

        """
        Pi = np.pi
        x = np.linspace(0, 2*Pi*rythm, int(self.__Fs*rythm), endpoint=False) # time variable

        # When scale==-1, it means a rest.
        if scale == -1:
            y = x*0
        else:
            frequency = self.get_frequency(major, scale)
            y = np.sin(frequency*x)*(1-x/(rythm*2*Pi))

        return y

    def gen_music(self,staff):
        """
        Play a piece of music based on section.

        Parameters
        ----------
            staff : class Staff.

        Returns
        -------
            wave : np.array
                The wave of the staff.
        """
        sections = staff.sections
        time = 60/staff.rythm
        loop_start, loop_end, loop_times, loop_sub = staff.loop

        wave = np.array([])
        section_wave_ls = []
        for section in sections:
            notes = section["notes"]
            wave_list = []
            for line_str in notes:
                line = [eval(note) for note in line_str.split()]
                line_wave = np.array([])
                for note in line:
                    major, scale, rythm = note
                    rythm *= time
                    y = self.get_wave(major, scale, rythm)
                    line_wave = np.concatenate((line_wave,y),axis=0)
                wave_list.append(line_wave)
            length = min([len(line_wave) for line_wave in wave_list])
            section_wave = wave_list[0][:length]
            for i in range(1,len(wave_list)):
                section_wave += wave_list[i][:length]
            # wave = np.concatenate((wave,section_wave),axis=0)
            section_wave_ls.append(section_wave)
            
        temp = [w for w in section_wave_ls[:loop_start-1]]
        for i in range(loop_times):
            for w in section_wave_ls[loop_start-1:loop_end]:
                temp.append(w)

        if loop_sub:
            section_wave_ls = temp[:-1] + [w for w in section_wave_ls[loop_end:]]
        else:
            section_wave_ls = temp + [w for w in section_wave_ls[loop_end:]]
        
        for w in section_wave_ls:
            wave = np.concatenate((wave,w), axis=0)

        return wave


if __name__ == "__main__":
    # s = Staff("国际歌.txt")
    # s.read_from_txt()

    music = Music("Python演奏国际歌")
    music.load_staff("国际歌.txt")
    music.save_music("Python演奏国际歌")
    music.draw_wave()

    # music = Music("test")
    # music.load_staff("test.txt")
    # music.save_music("test")
