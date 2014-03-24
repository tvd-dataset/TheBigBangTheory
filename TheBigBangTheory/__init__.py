#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2014 Anindya ROY (http://roy-a.github.io/)
# Copyright (c) 2013-2014 Hervé BREDIN (http://herve.niderb.fr/)
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


import re
import urllib3
from pkg_resources import resource_filename
from tvd import TFloating, TStart, TEnd, AnnotationGraph
from tvd import Plugin
import warnings

class TheBigBangTheory(Plugin):

    def speaker(self, url=None, episode=None, **kwargs):
        path = resource_filename(self.__class__.__name__, url)
        return AnnotationGraph.load(path)

    def outline(self, url=None, episode=None, **kwargs):
        """
        Parameters
        ----------
        url : str
            URL where resource is available
        episode : Episode, optional
            Episode for which resource should be downloaded
            Useful in case a same URL contains resources for multiple episodes.

        Returns
        -------
        G : AnnotationGraph
        """

        http = urllib3.PoolManager()
        r = http.request('GET', url)
        r = r.data
        r = re.sub('<script[^<]+</script>', '', r)
        r = re.sub('<style[^<]+</style>', '', r)
        r = re.sub('<div[^<]+</div>', '', r)
        r = re.sub('<[^>]+>', '', r)
        r = r.split('\n')

        G = AnnotationGraph(episode=episode)

        t_episode_start = TStart()
        t_episode_stop = TEnd()
        t_location_prev = t_episode_start
        t_event_prev = None

        start = 0

        for line in r:

            if re.search('\A[ \t\n\r]*\Z', line):  # Empty line.
                continue

            if re.search(
                '\A[ \t]*episode outline[ \t]*\Z',
                line, re.IGNORECASE
            ):  # Start of episode outline section.
                start = 1
                continue

            if start == 1:

                if (
                    re.search(
                        '\A[ \t]*resources[ \t]*\Z',
                        line,
                        re.IGNORECASE) or
                    re.search(
                        '\A\[*[0-9]*\]*timeline[ \t]*\Z',
                        line,
                        re.IGNORECASE) or
                    re.search(
                        '\A[ \t]*commentary and trivia[ \t]*\Z',
                        line,
                        re.IGNORECASE) or
                    re.search(
                        '\A[ \t]*trivia[ \t]*\Z',
                        line,
                        re.IGNORECASE)
                ):
                    break

                # New location description.
                if re.search('\A[ \t]*[IVXLCM]+[\.:]+', line):

                    # Finish the edge for previous location section.
                    if t_event_prev:
                        G.add_annotation(t_event_prev, t_location_prev, {})

                    location_ = re.sub(
                        '\A[ \t]*[IVXLCM]+[\.:]+[ \t]*', '', line)
                    t_location_start = TFloating()
                    G.add_annotation(t_location_prev, t_location_start, {})
                    t_location_stop = TFloating()
                    G.add_annotation(
                        t_location_start, t_location_stop,
                        {'location': location_}
                    )
                    t_location_prev = t_location_stop
                    t_event_prev = t_location_start

                else:

                    event_ = ' '.join(line.split())
                    t_event_start = TFloating()
                    t_event_stop = TFloating()
                    G.add_annotation(t_event_prev, t_event_start, {})
                    G.add_annotation(
                        t_event_start, t_event_stop,
                        {'event': event_}
                    )
                    t_event_prev = t_event_stop

        G.add_annotation(t_location_prev, t_episode_stop, {})

        return G

    def manual_transcript(self, url=None, episode=None, **kwargs):

        http = urllib3.PoolManager()
        r = http.request('GET', url)
        r = r.data
        r = re.sub('<script[^<]+</script>', '', r)
        r = re.sub('<style[^<]+</style>', '', r)
        r = re.sub('<div[^<]+</div>', '', r)
        r = re.sub('<[^>]+>', '', r)
        r = r.split('\n')

        G = AnnotationGraph(episode=episode)
        t_episode_start = TStart()
        t_episode_stop = TEnd()
        t_location_prev = t_episode_start
        t_event_prev = None

        for line in r:

            # Empty line
            if re.search('\A[ \t\n\r]*\Z', line):
                continue

            # Scene/location description.
            if re.match('\A\s*[Ss]cene\s*[\.:]', line):

                if t_event_prev:
                    G.add_annotation(t_event_prev, t_location_prev, {})

                location_ = re.sub('\A\s*[Ss]cene\s*[\.:]', '', line)
                t_location_start = TFloating()
                G.add_annotation(t_location_prev, t_location_start, {})
                t_location_stop = TFloating()
                G.add_annotation(
                    t_location_start, t_location_stop,
                    {'location': location_}
                )
                t_location_prev = t_location_stop
                t_event_prev = t_location_start
                continue

            if (
                re.search('\A[ \t]*Written by', line, re.IGNORECASE) or
                re.search('\A[ \t]*Teleplay:', line, re.IGNORECASE) or
                re.search('\A[ \t]*Story:', line, re.IGNORECASE) or
                re.search('\A[ \t]*Like this:', line, re.IGNORECASE)
            ):
                break

            speaker_ = re.match('\A\s*[^:\.]+\s*:', line)
            # Comments e.G. '(They begin to fill out forms.)
            if speaker_ is None:
                continue

            speaker_ = speaker_.group()
            speaker_ = re.sub('\A\s*', '', speaker_)
            #speaker = re.sub('\s*[\.:]','', speaker).lower()
            speaker_ = re.sub('\s*\([^)]+\)\s*', '', speaker_)
            #if speaker in names_map:
            #   speaker = names_map[speaker]
            speech_ = re.sub('\A\s*[^:\.]+\s*:\s*', '', line)

            t_event_start = TFloating()
            t_event_stop = TFloating()
            G.add_annotation(t_event_prev, t_event_start, {})
            G.add_annotation(
                t_event_start, t_event_stop,
                {'speaker': speaker_, 'speech': speech_}
            )
            t_event_prev = t_event_stop

        return G

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
