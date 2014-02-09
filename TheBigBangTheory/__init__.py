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

# Comments (AR):
# Q1: Why not keep scene/location description in addition to event info? Note that this may be specific to TBBT.
# Q2: Why not 'event' and 'location', instead of just 'speech'?
# Q3: Continuous graph?

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

	text = [] # Text for episode outline.
	start = 0
	for line in r:
		if re.search('\A[ \t\n\r]*\Z', line):
			continue
		if re.search('\A[ \t]*episode outline[ \t]*\Z', line, re.IGNORECASE):
			start = 1
			continue
		if start == 1:
			if re.search('\A[ \t]*resources[ \t]*\Z', line, re.IGNORECASE) or re.search('\A\[*[0-9]*\]*timeline[ \t]*\Z', line, re.IGNORECASE) or re.search('\A[ \t]*commentary and trivia[ \t]*\Z', line, re.IGNORECASE) or re.search('\A[ \t]*trivia[ \t]*\Z', line, re.IGNORECASE):
				break
			if not re.search('\A[ \t]*[IVXLCM]+[\.:]+', line): # Remove location description.
				text.append(' '.join(line.split())) # Keep just events. Q. Why not keep location info?

        g = nx.MultiDiGraph(uri=str(episode), source=source)
	nEvents = len(text)
        for eNo in xrange(nEvents):
                t1 = T()
                t2 = T()
		event = text[eNo]
                g.add_edge(t1, t2, scene="Scene_"+str(eNo), speech=event) # Why not 'event' instead of 'speech'?

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

	for line in r:
		if re.search('\A[ \t\n\r]*\Z', line): # Empty line.
			continue

		if re.match('\A\s*[Ss]cene\s*[\.:]', line): # Scene description. 
			continue

		if re.search('\A[ \t]*Written by', line, re.IGNORECASE) or re.search('\A[ \t]*Teleplay:', line, re.IGNORECASE) or re.search('\A[ \t]*Story:', line, re.IGNORECASE) or re.search('\A[ \t]*Like this:', line, re.IGNORECASE):
			break
		
		speaker = re.match('\A\s*[^:\.]+\s*:', line)
		if speaker == None:
			continue # Comments e.g. '(They begin to fill out forms.)

		speaker = speaker.group()
		speaker = re.sub('\A\s*','', speaker)
		#speaker = re.sub('\s*[\.:]','', speaker).lower()
		speaker = re.sub('\s*\([^)]+\)\s*','', speaker)
		#if speaker in names_map:
		#	speaker = names_map[speaker]
		speech_ = re.sub('\A\s*[^:\.]+\s*:\s*','', line)

                t1 = T()
                t2 = T()
                g.add_edge(t1, t2, spk=speaker, speech=speech_)

        return g





