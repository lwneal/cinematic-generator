# This script converts an input .mp4 file to a .mp4 file with a fixed audio track
# We use ffmpeg to do the conversion
import os
import sys
import subprocess


def main(input_filename, output_filename):
    # First, decode the audio to a temporary .wav file
    temp_wav_filename = 'temp.wav'
    subprocess.call(['ffmpeg', '-i', input_filename, '-vn', '-acodec', 'pcm_s16le', '-ac', '2', '-ar', '44100', '-f', 'wav', temp_wav_filename])

    # Now reencode the audio and the original video into the output file
    subprocess.call(['ffmpeg', '-i', input_filename, '-i', temp_wav_filename, '-c:a', 'aac', '-strict', 'experimental', output_filename])


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: {} <input_filename> <output_filename>'.format(sys.argv[0]))
        print('Example: {} input.mp4 output.mp4'.format(sys.argv[0]))
        print('This script converts an input .mp4 file to a .mp4 file with a fixed audio track')
        sys.exit(1)
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    main(input_filename, output_filename)
