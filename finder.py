from dejavu import Dejavu
from recognize import FileRecognizer

if __name__ == '__main__':

	# create a Dejavu instance
	djv = Dejavu()
	
	# Or use a recognizer without the shortcut, in anyway you would like
	recognizer = FileRecognizer(djv)
	time_taken = recognizer.recognize_file("duplicates/04. Lil Nas X - Old Town Road (Remix)_15_70.mp3")
	print('time_taken', time_taken)

