# this script process raw copy-n-paste episode transcripts from wikia
# and generate (hopefully) clean text files in the following format

# ../TheBigBangTheory.Season01.Episode01.txt
# SCENE description of the scene
# CHARACTER1 dialogue line from CHARACTER 1
# CHARACTER2 dialogue line from CHARACTER 2

import re
from tvd import TheBigBangTheory
episodes = TheBigBangTheory('whatever').episodes

QUOTES = "''(.*?)''"
PARENTHESES = '\(.*?\)'
BRACKETS = '(\[|\])'
SCENE = "'''Scene'''"
NOTHING = ''

for episode in episodes[:17]:

    print episode

    inputFile = '%s.txt' % str(episode)
    outputFile = '../%s.txt' % str(episode)

    with open(inputFile, 'r') as f:
        file_content = ''.join([line for line in f.readlines() if line[0] == '|'])
    entries = [e[1:].split('\n|')[:2]
               for e in file_content.split('|-\n')
               if e and e[0] == '|']

    with open(outputFile, 'w') as f:

        for left, right in entries:

            # new scene
            if left == SCENE:
                m = re.match(QUOTES, right)
                if m:
                    scene = m.groups()[0]
                else:
                    scene = right
                scene = re.sub(BRACKETS, NOTHING, scene)
                f.write('SCENE {scene:s}\n'.format(scene=scene))

            elif left != NOTHING:
                speaker = re.sub(BRACKETS, NOTHING, left)
                speaker = re.sub(PARENTHESES, NOTHING, speaker)

                # sheldon --> SHELDON
                # voice from buzzer --> VOICE_FROM_BUZZER
                speaker = '_'.join(speaker.split()).upper()
                dialogue = re.sub(QUOTES, NOTHING, right).strip()

                if dialogue != NOTHING:
                    f.write('{speaker:s} {dialogue:s}\n'.format(
                        speaker=speaker, dialogue=dialogue))
