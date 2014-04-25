#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 CNRS
# - Anindya ROY (http://roy-a.github.io/)
# - Hervé BREDIN (http://herve.niderb.fr/)
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
import HTMLParser
from pkg_resources import resource_filename
from tvd import TFloating, TStart, TEnd, AnnotationGraph
from tvd import Plugin
from bs4 import BeautifulSoup
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

        h = HTMLParser.HTMLParser()
        r = self.download_as_utf8(url)

        r = re.sub('<script[^<]+</script>', '', r)
        r = re.sub('<style[^<]+</style>', '', r)
        r = re.sub('<div[^<]+</div>', '', r)
        r = re.sub('<li>', '@EVENT', r) # Alternate way to detect event,
                    # without depending on 'IXV.' etc.
                    # -> Events are always items in a list.
        r = re.sub('<[^>]+>', '', r)
        r = r.split('\n')

        G = AnnotationGraph(episode=episode)

        t_episode_start = TStart()
        t_episode_stop = TEnd()
        t_location_prev = t_episode_start
        t_event_prev = None

        start = 0

        for line in r:
        
            line = h.unescape(line) # Decode HTML code e.g. "don&#8217;t feed the .." to Unicode.
            if re.search('\A[ \t\n\r]*\Z', line):  # Empty line.
                continue

            if re.search(
                '\A[ \t]*episode outline[ \t]*\Z',
                line, re.IGNORECASE
            ):  # Start of episode outline section.
                start = 1
                continue

            if start == 1:
            # Check end of episode outline (or empty content).
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
                        re.IGNORECASE) or
                    re.search(
                        '\A[ \t]*Still to come[ \t]*\Z',
                        line,
                        re.IGNORECASE)
                  ):
                    break

                # Lines to be ignored:
                # 'Titles and opening theme',
                # 'Titles and credits'
                # 'Opening themes and credits'
                # 'Title and Opening Themes'
                # 'Theme song and titles'

                # New location description.
                #if re.search('\A[ \t]*[IVX]+[\.:]+', line): # DO NOT USE.
                if not re.search('@EVENT', line):

                    if (
                        re.search('title', line, re.IGNORECASE) or
                        re.search('credit', line, re.IGNORECASE) or
                        re.search('theme', line, re.IGNORECASE)
                    ):
                        continue # Assume it's 'Titles and opening theme' or something
                         # similar. Ignore.

                    # Finish the edge for previous location section.
                    if t_event_prev:
                        G.add_annotation(t_event_prev, t_location_prev, {})

                    location_ = re.sub(
                        '\A[ \t]*[IVX]+[\.:]+[ \t]*', '', line) # Remove roman numeral.
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
                    event_ = re.sub('@EVENT', '', event_)
                    t_event_start = TFloating()
                    t_event_stop = TFloating()
                    G.add_annotation(t_event_prev, t_event_start, {})
                    G.add_annotation(
                        t_event_start, t_event_stop,
                        {'event': event_}
                    )
                    t_event_prev = t_event_stop

        G.add_annotation(t_event_prev, t_location_prev, {})
        G.add_annotation(t_location_prev, t_episode_stop, {})

        return G

    @staticmethod
    def _get_directions(text):

        REGEXP_DIRECTION = '([^\(^\)]*)\((.+?)\)(.*)'

        directions = []
        text_without_directions = u''

        while text:
            
            m = re.match(REGEXP_DIRECTION, text)
            
            if not m:
                text_without_directions += text
                break
        
            else:
                before, direction, after = m.groups()
                directions.append(direction)
                text_without_directions += before
                text = after
        
        return text_without_directions, directions



    def manual_transcript(self, url=None, episode=None, debug=False, **kwargs):

        SPEAKER_MAPPING = {
            # 'sheldon': 'sheldon',
            # 'sgeldon': 'sheldon',
            # 'leonard': 'leonard',
            # 'penny': 'penny',
            # 'raj': 'raj',
            # 'howard': 'howard',
            # # 'receptionist': 'receptionist',
            # # 'voice from buzzer': 'voice_from_buzzer',
            # # 'voice': 'voice',
            # # 'enormous man': 'enormous_man',
            # # 'man': 'man',
            # 'doug': 'doug',
            # 'lesley': 'leslie_winkle',
            # 'leslie': 'leslie_winkle',
            # 'leslie winkle': 'leslie_winkle',
            # # 'class instructor': 'class_instructor',
            # # 'waitress': 'waitress',
            # #'summer': 'summer',
            # 'gablehouser': 'gablehouser',
            # 'dr gablehouser': 'gablehouser',
            # 'gablehauser': 'gablehouser',
            # 'mrs cooper': 'mrs_cooper',
            # 'kurt': 'kurt',
            # 'christie': 'christie',
            # "howard's mother": 'howards_mother',
            # 'dr koothrappali': 'dr_koothrappali',
            # 'mrs koothrappali': 'mrs_koothrappali',
            # 'lalita': 'lalita',
            # 'toby': 'toby',
            # 'dennis': 'dennis',
            # 'goldfarb': 'goldfarb',
            # 'mike': 'mike',
            # 'missy': 'missy',
            # 'eric': 'eric',
            # 'charlie sheen': 'charlie_sheen',
            # 'kathy': 'kathy',
            # "leonard's mother": 'leonards_mother',
            # # bernadette's father
            # "mr. rostenkowski": "mr_rostenkowski",
            # "mr rostenkowski": "mr_rostenkowski",
        }

        # download webpage and parse it with BeautifulSoup
        soup = BeautifulSoup(self.download_as_utf8(url))

        # extract the following <div> containing the actual transcript
        # <div class='entrytext'> ... </div>
        div = soup.findAll('div', attrs={'class': 'entrytext'})[0]

        # initialize empty annotation graph
        G = AnnotationGraph(episode=episode)

        # episode start and end
        tstart = TStart()
        tend = TEnd()

        # tscene contains end of previous scene
        tscene = tstart
        # tspeech contains end of previous speech turn
        tspeech = None

        speakers = set([])

        # loop on each <p></p> 
        # inside <div class='entrytext'></div> 
        for p in div.findAll('p'):

            # as <p></p> sometimes contain new lines
            # make sure we get only one long text from them
            text = u' '.join(p.getText().split('\n')).strip()

            # if line is empty, skip it
            if not text:
                continue

            # try to match xxxxx: yyyyyy
            REGEXP_DIALOGUE = '\A\s*([^:]+?)\s*:\s*(.*)\Z'
            m = re.match(REGEXP_DIALOGUE, text)
            
            if not m:
                # (They sit ...).
                # (Leonard starts rattling.)
                # u'Credits sequence.'
                # u'Credits sequence'
                # u'Credit sequence.'
                # u'Credit Sequence'
                # u'Credits sequence'
                # u'Time shift, Leonard and Sheldon are now ...'
                # u'Cut to Leonard entering living room in panic, ...'
                # u'Written by...'
                # u'(Time shift)'

                if debug:
                    print "SKIPPING: %s" % repr(text)

                continue             

            # if there is a match, we are in one of the following situations:
            # Scene: blah blah blah
            # Sheldon: blah blah blah
            # Teleplay: blah blah blah
            # ...
            # left: right
            left, right = m.groups()
            left = left.strip().lower()
            right = right.strip()

            # if we are in of the following situations,
            # then we found a new scene
            # Scene: location
            # scene: location
            if left == u'scene':

                # remove unwanted spaces from location
                data = {'location': right.strip()}

                # add the new scene to the graph
                t1 = TFloating()  # start time
                t2 = TFloating()  # end time
                G.add_annotation(t1, t2, data=data)

                # make sure it is connected to the previous scene
                G.add_annotation(tscene, t1)

                # make sure last speech turn of previous scene
                # is correctly connected to end of previous scene
                if tspeech:
                    G.add_annotation(tspeech, tscene)
                
                # update end of previous scene/speech
                tscene = t2
                tspeech = t1

            # if we are in one of the following situations
            # Teleplay: Bill Prady & Steven Molaro
            # Story: Chuck Lorre
            elif left in {'story', 'teleplay'}:
                continue

            # that's what we are really looking for: 
            # speaker_name: speech
            else:

                # remove stage directions from speaker name
                # e.g. "penny (to raj)" becomes ("penny", ["to raj", ])
                speaker, speaker_directions = self._get_directions(left)
                speaker = speaker.strip()

                # remove stage directions from speech
                # "hey sheldon (laughing). where is your spot?"
                # becomes "hey sheldon . where is your spot?", ["laughing",]
                speech, speech_directions = self._get_directions(right)
                speech = speech.strip()

                # gather all stage directions into one long string
                directions = u' '.join(speaker_directions + speech_directions)

                # debug
                if speaker not in SPEAKER_MAPPING:
                    warnings.warn('no mapping for speaker "%s"' % speaker)
                
                # build annotation data
                # (with directions only if they exist)
                data = {
                    'speaker': SPEAKER_MAPPING.get(speaker, speaker),
                    'speech': speech,
                }
                if directions:
                    data['directions'] = directions

                # add the new speech turn to the graph
                t1 = TFloating()
                t2 = TFloating()
                G.add_annotation(t1, t2, data=data)

                # make sure it is connected to the previous speech turn
                G.add_annotation(tspeech, t1)

                # update end of previous speech turn
                tspeech = t2


        # make sure last speech turn is correctly connected to end of last scene
        G.add_annotation(tspeech, tscene)

        # make sure last scene is correctly connected to episode end
        G.add_annotation(tscene, tend)

        return G

    # def manual_transcript(self, url=None, episode=None, **kwargs):

    #     h = HTMLParser.HTMLParser()

    #     r = self.download_as_utf8(url)

    #     # remove <script>...</script>
    #     r = re.sub('<script[^<]+</script>', '', r)

    #     # remove <style>...</style>
    #     r = re.sub('<style[^<]+</style>', '', r)

    #     # remove <div>..</div>
    #     r = re.sub('<div[^<]+</div>', '', r)

    #     # remove 
    #     r = re.sub('<[^>]+>', '', r)
    #     r = r.split('\n')

    #     G = AnnotationGraph(episode=episode)
    #     t_episode_start = TStart()
    #     t_episode_stop = TEnd()
    #     t_location_prev = t_episode_start
    #     t_event_prev = None

    #     for line in r:

    #         #line = h.unescape(line) # Decode HTML code e.g. 
    #                 # "don&#8217;t feed the .." to Unicode.
    #         # Empty line
    #         if re.search('\A[ \t\n\r]*\Z', line):
    #             continue

    #         # Scene/location description.
    #         if re.match('\A\s*[Ss]cene\s*[\.:]', line):

    #             if t_event_prev:
    #                 G.add_annotation(t_event_prev, t_location_prev, {})

    #             location_ = re.sub('\A\s*[Ss]cene\s*[\.:]', '', line)
    #             t_location_start = TFloating()
    #             G.add_annotation(t_location_prev, t_location_start, {})
    #             t_location_stop = TFloating()
    #             G.add_annotation(
    #                 t_location_start, t_location_stop,
    #                 {'location': location_}
    #             )
    #             t_location_prev = t_location_stop
    #             t_event_prev = t_location_start
    #             continue

    #         if (
    #             re.search('\A[ \t]*Written by', line, re.IGNORECASE) or
    #             re.search('\A[ \t]*Teleplay:', line, re.IGNORECASE) or
    #             re.search('\A[ \t]*Story:', line, re.IGNORECASE) or
    #             re.search('\A[ \t]*Like this:', line, re.IGNORECASE)
    #         ):
    #             break

    #         speaker_ = re.match('\A\s*[^:\.]+\s*:', line)
    #         # Comments e.g. '(They begin to fill out forms.)
    #         if speaker_ is None:
    #             continue

    #         speaker_ = speaker_.group()
    #         speaker_ = re.sub('\A\s*', '', speaker_)
    #         #speaker = re.sub('\s*[\.:]','', speaker).lower()
    #         speaker_ = re.sub('\s*\([^)]+\)\s*', '', speaker_)
    #         #if speaker in names_map:
    #         #   speaker = names_map[speaker]
    #         speech_ = re.sub('\A\s*[^:\.]+\s*:\s*', '', line)

    #         t_event_start = TFloating()
    #         t_event_stop = TFloating()
    #         G.add_annotation(t_event_prev, t_event_start, {})
    #         G.add_annotation(
    #             t_event_start, t_event_stop,
    #             {'speaker': speaker_, 'speech': speech_}
    #         )
    #         t_event_prev = t_event_stop

    #     G.add_annotation(t_event_prev, t_location_prev, {})
    #     G.add_annotation(t_location_prev, t_episode_stop, {})
    #     return G

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
