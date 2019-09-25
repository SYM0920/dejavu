import warnings
import json
from dejavu import Dejavu
warnings.filterwarnings("ignore")
from recognize import FileRecognizer, MicrophoneRecognizer

if __name__ == '__main__':

	# create a Dejavu instance
	djv = Dejavu()

	# Fingerprint all the mp3's in the directory we give it
	djv.fingerprint_directory("mp3", [".mp3"], nprocesses=4)

	# # Recognize audio from a file
	# song = djv.recognize(FileRecognizer, "mp3/Sean-Fournier--Falling-For-You.mp3")
	# print ("From file we recognized: %s\n" % song)

	# Or recognize audio from your microphone for `secs` seconds
	# secs = 5
	# song = djv.recognize(MicrophoneRecognizer, seconds=secs)
	# if song is None:
	# 	print "Nothing recognized -- did you play the song out loud so your mic could hear it? :)"
	# else:
	# 	print "From mic with %d seconds we recognized: %s\n" % (secs, song)

	# Or use a recognizer without the shortcut, in anyway you would like
	recognizer = FileRecognizer(djv)
	song = recognizer.recognize_file("./match_from/03_Find_U_Again_(feat_Camila_Cabello)-[AudioTrimmer.com].mp3")
	print ("No shortcut, we recognized: %s\n" % song)
