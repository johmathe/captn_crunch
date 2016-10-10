import feedparser
import urllib
import os
import tempfile
import ffmpy
import scipy.io.wavfile
import numpy as np
from scipy.signal import butter, lfilter

PODCAST = 'http://www.npr.org/rss/podcast.php?id=510310'

__author__ = 'johan.mathe@gmail.com'


def download_rss_feed(rss_feed_url, link_paths):
    feed = feedparser.parse(PODCAST)
    entry_count = len(feed['entries'])
    print('downloading %d links...' % entry_count)
    for i, link in enumerate(feed['entries']):
        href = link['links'][0]['href']
        print('retrieving %s...' % href)
        urllib.urlretrieve(href, os.path.join(link_paths, '%04d.mp3' % i))


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = fs / 2
    low = float(lowcut) / nyq
    high = float(highcut) / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    filtered = lfilter(b, a, data)
    return filtered


def sound_to_wav(sound_path, wav_path):
    ff = ffmpy.FFmpeg(
        global_options='-y',
        inputs={sound_path: None},
        outputs={wav_path: None})
    ff.run()


def downsample_file(input_sound_file,
                    output_wav_file,
                    lowcut=200,
                    highcut=1200):
    _, tmp_file = tempfile.mkstemp(prefix='/tmp/', suffix='.wav')
    sound_to_wav(input_sound_file, tmp_file)
    fs, sound = scipy.io.wavfile.read(tmp_file)
    mono = sound[:, 0]
    filtered = butter_bandpass_filter(mono, lowcut, highcut, fs, order=3)
    scipy.io.wavfile.write(
        output_wav_file, rate=44100, data=filtered.astype(np.int16))
    os.remove(tmp_file)

downsample_file('0002.mp3', 'downsampled.wav')
