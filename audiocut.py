import glob
import os
import sys
import csv

import ffmpeg
import sox

# set a path variable and check for existence
path = input("Enter the name of the directory with audio:")
if os.path.isdir(path):

    # find all wav files in directory
    audiofiles = glob.glob(path + "/*.wav")

    # cut right channel in original wav-files and output in files
    # make right channel from original audio is better way to make script faster, then cut right from many files in the end
    tfm = sox.Transformer()
    remix_dictionary = {1: [1]}
    for audiofile in audiofiles:
        tfm.build(audiofile, f"{audiofile[:-4]}_right.wav")
        tfm.remix()

    # replace ";" to "," in csv to make a dict in future
    # does work if in directory only one csv-file
    csvfile = os.path.commonpath(glob.glob(path + "/*.csv"))
    newcsvfile = path + "/output.csv"
    with open(csvfile, "r") as csvtext:
        textcsvreplace = "".join([row for row in csvtext]).replace(";", ",")
        with open(newcsvfile, "w") as newcsvtext:
            newcsvtext.writelines(textcsvreplace)
            newcsvtext.close

    # make a dict from csv file
    with open(newcsvfile) as newcsv:
        csvread = csv.DictReader(newcsv)
        rows = list(csvread)

        # find audio with right channel
        rightchannel_audio = glob.glob(path + "/*_right.wav")

        # use loop for read csv rows
        for row in range(0, len(rows)):
            nextrow = row+1 if row+1 < len(rows) else row
            starttime = rows[row]['starttime']
            endtime = rows[nextrow]['starttime']
            channel = rows[row]['channel']

            # find file by startime and channel
            filetofind = starttime[:11] + "0000_" + channel
            for files in rightchannel_audio:
                if filetofind in files:
                    audiofile = files

            # count seconds from timestamps
            minutesfromdate = int(starttime[11:-2]) # minutes from timestamp in csv
            secondsfromdate = int(starttime[13:]) # seconds from timestamp in csv
            startseconds = (minutesfromdate * 60) +  secondsfromdate # seconds from start in audiofile

            # named output audiofile
            outputaudio = path + "/" + starttime + "_" + channel + "_" + rows[row]['fio'] + ".wav"

            # check if difference between start and start of next audio more then 5 minutes
            difference = int(endtime[9:]) - int(starttime[9:])
            difference = difference * -1 # make negative number to positive if starttime bigger than endtime
            if difference < 500:
                endtimeminutes = int(endtime[11:-2])
                endtimeseconds = int(endtime[13:])
                duration = ((endtimeminutes * 60) + endtimeseconds) - startseconds

                stream = ffmpeg.input(audiofile, ss=startseconds, t=duration)
                stream = ffmpeg.output(stream, outputaudio)
                ffmpeg.run(stream)
            else:
                stream = ffmpeg.input(audiofile, ss=startseconds, t=300)
                stream = ffmpeg.output(stream, outputaudio)
                ffmpeg.run(stream)

        newcsv.close
    # delete temp files
    for files in rightchannel_audio:
        os.remove(files)
    os.remove(newcsvfile)
else:
    print("Directory doesn't exist")
