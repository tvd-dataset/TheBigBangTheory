#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2014 Anindya ROY (http://roy-a.github.io/)
# Copyright (c) 2013 Hervé BREDIN (http://herve.niderb.fr/)
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

# Questions (resolved) (AR):
# Q1: Why not keep scene/location description in addition to event info? Note that this may be specific to TBBT. Done.
# Q2: Why not 'event' and 'location', instead of just 'speech'? Done.
# Q3: Continuous graph? Done.

from tvd.series.plugin import SeriesPlugin
import re
import urllib3
from tvd.common.graph import T
import networkx as nx


class TheBigBangTheory(SeriesPlugin):

    

    def outline(self, url, source=None, episode=None):
        """
        Parameters
        ----------
        url : str
            URL where resource is available
        source : str, optional
            Textual description of the source of the resource
        episode : Episode, optional
            Episode for which resource should be downloaded
            Useful in case a same URL contains resources for multiple episodes.

        Returns
        -------
        g : AnnotationGraph
        """

        http = urllib3.PoolManager()
	r = http.request('GET', url)
	r = r.data
	r = re.sub('<script[^<]+</script>', '', r)
 	r = re.sub('<style[^<]+</style>', '', r)
	r = re.sub('<div[^<]+</div>', '', r)
 	r = re.sub('<[^>]+>', '', r)
	r = r.split('\n')

	g = nx.MultiDiGraph(uri=str(episode), source=source)

	t_episode_start = T()
	t_episode_stop = T() 
	t_location_prev = t_episode_start
	t_event_prev = None

	start = 0
	for line in r:
		if re.search('\A[ \t\n\r]*\Z', line): # Empty line.
			continue
		if re.search('\A[ \t]*episode outline[ \t]*\Z', line, re.IGNORECASE): # Start of episode outline section.
			start = 1
			continue
		if start == 1:
			if re.search('\A[ \t]*resources[ \t]*\Z', line, re.IGNORECASE) or re.search('\A\[*[0-9]*\]*timeline[ \t]*\Z', line, re.IGNORECASE) or re.search('\A[ \t]*commentary and trivia[ \t]*\Z', line, re.IGNORECASE) or re.search('\A[ \t]*trivia[ \t]*\Z', line, re.IGNORECASE):
				break
			if re.search('\A[ \t]*[IVXLCM]+[\.:]+', line): # New location description.
			
				# Finish the edge for previous location section.
				if t_event_prev:
					g.add_edge(t_event_prev, t_location_prev)

				location_ = re.sub('\A[ \t]*[IVXLCM]+[\.:]+[ \t]*', '', line)
				t_location_start = T()
				g.add_edge(t_location_prev, t_location_start)
				t_location_stop = T()
				g.add_edge(t_location_start, t_location_stop, location=location_)
				t_location_prev = t_location_stop
				t_event_prev = t_location_start
				
			else:
				event_ = ' '.join(line.split()) 
				t_event_start = T()
				t_event_stop = T()
				g.add_edge(t_event_prev, t_event_start)
				g.add_edge(t_event_start, t_event_stop, event = event_)
				t_event_prev = t_event_stop

        
	g.add_edge(t_location_prev, t_episode_stop)

        return g

    def manual_transcript(self, url, source=None, episode=None):

	#names_map = {'Raj':'Rajesh', 'raj':'rajesh', 'Lesley':'Leslie', 'lesley':'leslie'}
      	http = urllib3.PoolManager()
	r = http.request('GET', url)
	r = r.data
	r = re.sub('<script[^<]+</script>', '', r)
 	r = re.sub('<style[^<]+</style>', '', r)
	r = re.sub('<div[^<]+</div>', '', r)
 	r = re.sub('<[^>]+>', '', r)
	r = r.split('\n')

	g = nx.MultiDiGraph(uri=str(episode), source=source)
	t_episode_start = T()
	t_episode_stop = T()
	t_location_prev = t_episode_start
	t_event_prev = None

	for line in r:
		if re.search('\A[ \t\n\r]*\Z', line): # Empty line.
			continue

		if re.match('\A\s*[Ss]cene\s*[\.:]', line): # Scene/location description. 
			if t_event_prev:
					g.add_edge(t_event_prev, t_location_prev)

			location_ = re.sub('\A[ \t]*[IVXLCM]+[\.:]+[ \t]*', '', line)
			t_location_start = T()
			g.add_edge(t_location_prev, t_location_start)
			t_location_stop = T()
			g.add_edge(t_location_start, t_location_stop, location=location_)
			t_location_prev = t_location_stop
			t_event_prev = t_location_start
			continue

		if re.search('\A[ \t]*Written by', line, re.IGNORECASE) or re.search('\A[ \t]*Teleplay:', line, re.IGNORECASE) or re.search('\A[ \t]*Story:', line, re.IGNORECASE) or re.search('\A[ \t]*Like this:', line, re.IGNORECASE):
			break
		
		speaker_ = re.match('\A\s*[^:\.]+\s*:', line)
		if speaker_ == None:
			continue # Comments e.g. '(They begin to fill out forms.)

		speaker_ = speaker_.group()
		speaker_ = re.sub('\A\s*','', speaker)
		#speaker = re.sub('\s*[\.:]','', speaker).lower()
		speaker_ = re.sub('\s*\([^)]+\)\s*','', speaker_)
		#if speaker in names_map:
		#	speaker = names_map[speaker]
		speech_ = re.sub('\A\s*[^:\.]+\s*:\s*','', line)

                t_event_start = T()
                t_event_stop = T()
                g.add_edge(t_event_prev, t_event_start)
                g.add_edge(t_event_start, t_event_stop, speaker=speaker_, speech=speech_)
                t_event_prev = t_event_stop

        return g





