#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2015 CNRS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# AUTHORS
# Hervé BREDIN -- http://herve.niderb.fr/

import pytest
from tvd import TheBigBangTheory
from pyannote.core import Segment
import numpy as np


@pytest.fixture
def dataset():
    dataset = TheBigBangTheory('.')
    return dataset

def test_speaker(dataset):

    episode = dataset.episodes[0]
    speaker = dataset.get_resource_from_plugin('speaker', episode)

    assert list(speaker.itertracks(label=True))[:10] == [
        (Segment(0.0000, 1.2151), '0', 'silence'),
        (Segment(1.2151, 1.2151 + 11.3662), '0', 'speech_sheldon'),
        (Segment(12.5813, 12.5813 + 0.3340), '0', 'silence'),
        (Segment(12.9153, 12.9153 + 0.4284), '0', 'speech_leonard'),
        (Segment(13.3437, 13.3437 + 0.6346), '0', 'silence'),
        (Segment(13.9783, 13.9783 + 0.6305), '0', 'speech_leonard'),
        (Segment(14.6088, 14.6088 + 0.1360), '0', 'silence'),
        (Segment(14.7448, 14.7448 + 2.1888), '0', 'speech_sheldon'),
        (Segment(16.9336, 16.9336 + 0.4533), '0', 'silence'),
        (Segment(17.3868, 17.3868 + 3.1363), '0', 'sound_laugh')
    ]

def test_outline(dataset):
    episode = dataset.episodes[0]
    outline = dataset.get_resource_from_plugin('outline', episode)

    assert list(outline.ordered_edges_iter(data=True))[:10] == [
        (0, 16, {"location": "Hallway outside High-IQ Sperm Bank"}),
        (0, 20, {"event": 'Sheldon tells his "good idea for a T-shirt".'}),
        (16, 150, {"location": "High-IQ Sperm Bank"}),
        (20, 150, {"event": 'Sheldon and Leonard consider donating sperm, but back out.'}),
        (150, 152,  {"jingle": ""}),
        (152, 183,  {"location": "Stairs"}),
        (152, 183,  {"event": 'Sheldon and Leonard head back to the apartment, discussing the height of stair steps.'}),
        (183, 252,  {"location": "Hallway outside apartments"}),
        (183, 252,  {"event": 'They discover they have a new neighbor'}),
        (252, 287,  {"location": "Living room"})
    ]

def test_transcript(dataset):
    episode = dataset.episodes[0]
    transcript = dataset.get_resource_from_plugin('transcript', episode)

    assert list(transcript.ordered_edges_iter(data=True))[:10] == [
    ('A', 'C', {}),
    ('A', 'B', {'scene': 'A corridor at a sperm bank.'}),
    ('C',
     'D',
     {'speaker': 'SHELDON',
      'speech': 'So if a photon is directed through a plane with two slits in '
                'it and either slit is observed, it will not go through both '
                "slits. If it's unobserved it will, however, if it's observed "
                "after it's left the plane but before it hits its target, it "
                'will not have gone through both slits.'}),
    ('D', 'E', {}),
    ('E', 'F', {'speaker': 'LEONARD', 'speech': "Agreed, what's your point?"}),
    ('F', 'G', {}),
    ('G',
     'H',
     {'speaker': 'SHELDON',
      'speech': "There's no point, I just think it's a good idea for a "
                'tee-shirt.'}),
    ('H', 'I', {}),
    ('I', 'J', {'speaker': 'LEONARD', 'speech': 'Excuse me?'}),
    ('J', 'K', {})]

def test_transcript_aligned(dataset):
    episode = dataset.episodes[0]
    transcript = dataset.get_resource_from_plugin('transcript_aligned', episode)

    assert list(transcript.ordered_edges_iter(data=True))[:10] == [
        (-np.inf, 1.41, {}),
        (1.41, 1.63, {'confidence': 0.99, 'speech': 'So'}),
        (1.63, 1.67, {'confidence': 0.1, 'speech': 'if'}),
        (1.67, 1.74, {'confidence': 0.1, 'speech': 'a'}),
        (1.74, 1.83, {}),
        (1.83, 2.25, {'confidence': 0.99, 'speech': 'photon'}),
        (2.25, 2.37, {'confidence': 0.99, 'speech': 'is'}),
        (2.37, 2.74, {'confidence': 0.99, 'speech': 'directed'}),
        (2.74, 2.77, {}),
        (2.77, 2.89, {'confidence': 0.99, 'speech': 'through'})
    ]
