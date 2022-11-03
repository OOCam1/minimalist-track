from email.mime import audio
import numpy as np
import pydub
from pydub.playback import play
from random import randint as ra
from pydub import AudioSegment 

#Things to change
###

set_beat = 0.20
set_bar = 16
overlap = 20
snippet_max = 15
increment = 2

###
OVERLAP_END = overlap + (snippet_max)*increment


bar_seconds = set_bar*set_beat
TOTAL_SECONDS = (OVERLAP_END + (snippet_max//2)*increment)*bar_seconds
print(TOTAL_SECONDS)

#This code enables us to play notes
def key(frequency, duration = 1, sampling_rate = 44100 , amplitude = 1000):

    times = np.linspace(0,duration,int(sampling_rate*duration))
    note = amplitude * np.sin(2*np.pi*frequency*times)
    return note.astype(np.int16)

def generate_note(herz, seconds):

    channel1 = key(herz, seconds, 44100, 1000)
    audio_segment = pydub.AudioSegment(channel1.tobytes(), frame_rate=44100,sample_width=2, channels=1)
    return audio_segment



NOTES =  [130.81, 146.83, 164.81, 196.00, 220.00, 261.63, 293.66, 329.63, 392.00, 440.00, 523.25,587.33, 659.26,783.99,880]

#This is the code used to randomly decide which note to play next
def find_new_note(starting_note):
    note_index = starting_note
    index_gap = ra(1,3)
    if note_index - index_gap < 0:
        parity = 1
    elif note_index + index_gap > len(NOTES) - 1:
        parity = 0
    else:
        parity = ra(0,1)
    if parity == 0:
        note_index -= index_gap
    else:
        note_index += index_gap
    return note_index

#This code generates a fragment of music that will be repeated

def generate_snippet():

    beat_choice = ra(1,2)
    if beat_choice ==1:
        beat = set_beat*2/3
        bar = set_bar*3/2
    else:
        beat = set_beat
        bar = set_bar

    chord_choice = True
    
    
    gap = ra(1,32)
 
    if gap <=16:
        snippet = AudioSegment.silent(duration = gap*1000*beat)
        remaining = bar - gap
        start_gap_check = True
        note_index = ra(0, len(NOTES)-1)
        chord_note_index = note_index
        while chord_note_index == note_index:
            chord_note_index = ra(0, len(NOTES)-1)
        chord_snippet = snippet
    else:
        
        note_index = ra(0,len(NOTES)-1)
        frequency = NOTES[note_index]
        length = ra(1,bar)

        remaining = bar - length
        snippet = generate_note(frequency, length*beat)
        start_gap_check = False
        if chord_choice:
            chord_note_index = note_index
            while chord_note_index == note_index:
                chord_note_index = ra(0, len(NOTES)-1)
            frequency = NOTES[note_index]
            chord_snippet = generate_note(frequency, length*beat)


    while remaining > 0:
        if not start_gap_check:
            gap = ra(1,8)

            if gap <=6:
                if gap > remaining:
                    gap = remaining
                snippet += AudioSegment.silent(duration = gap*1000*beat)
                remaining -= gap

        if remaining > 0:
            start_gap_check = False
            note_index = find_new_note(note_index)
            length = ra(1, remaining)
            snippet += generate_note(NOTES[note_index], length*beat)
            remaining -= length
            if chord_choice:
                chord_note_index = find_new_note(chord_note_index)
                chord_snippet += generate_note(NOTES[chord_note_index], length*beat)
    
    if chord_choice:
        snippet = snippet.overlay(chord_snippet)
 

    return snippet



#This code combines all the snippets into one track


first_track = generate_snippet().overlay(generate_snippet())
track = first_track*OVERLAP_END 
remaining_silence = TOTAL_SECONDS - track.duration_seconds 
track += AudioSegment.silent(duration = remaining_silence*1000)
print(track.duration_seconds)

for pair in range(1,(snippet_max//2)+1):
    for x in range(2):
        silence_length = (pair*2+x-1)*increment

        snippet = AudioSegment.silent(duration = bar_seconds*1000*silence_length)
        melody = generate_snippet()
        snippet += melody*(OVERLAP_END-silence_length)
        snippet += melody*(increment*pair)   

        track = track.overlay(snippet)
        length = track.duration_seconds




#This saves the track to a file, and then plays it out loud

with open("counter.txt", "r") as file:
    counter = str(int(file.readline())+1)

with open("counter.txt", 'w') as file:
    file.write(counter)

track.export(out_f = 'track' + counter + '.mp3', format = "mp3")

play(track)