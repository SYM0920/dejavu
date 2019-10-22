from dejavu import Dejavu
from recognize import FileRecognizer

if __name__ == '__main__':

	# create a Dejavu instance
	djv = Dejavu()

	# Fingerprint all the mp3's in the directory we give it
	# djv.fingerprint_directory("duplicates", [".wav"], nprocesses=4)
	djv.fingerprint_directory("duplicates", [".mp3"], nprocesses=2)