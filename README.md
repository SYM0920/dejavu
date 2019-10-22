dejavu(No_sql)(With pandas)
==========

Audio fingerprinting and recognition algorithm implemented in Python, see the explanation here:  
[How it works](http://willdrevo.com/fingerprinting-and-audio-recognition-with-python/)

Dejavu can memorize audio by listening to it once and fingerprinting it. Then by playing a song and recording microphone input, Dejavu attempts to match the audio against the fingerprints held in the database, returning the song being played. 

Note that for voice recognition, Dejavu is not the right tool! Dejavu excels at recognition of exact signals with reasonable amounts of noise.


1. Put audio files in files folder after specifying the folder name and list of file extensions in the `fingerprint_directory.py` script.
2. Run `python3 fingerprint_directory.py` which will create hashes for all the files. 
3. Run `python3 merge_csv.py` to merge all the hashed CSVs
4. Run `python3 finder.py` after adding name of the file, to be searched, in the `finder.py` script.
