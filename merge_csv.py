from dejavu import Dejavu

if __name__ == '__main__':

	# create a Dejavu instance
	djv = Dejavu()

	# Fingerprint all the mp3's in the directory we give it
	djv.merge_tables()