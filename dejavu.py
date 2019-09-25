import decoder as decoder
import fingerprint
import multiprocessing
import os
import traceback
import sys
import pandas as pd
import numpy as np
import itertools 


class Dejavu(object):

	SONG_ID = "song_id"
	SONG_NAME = 'song_name'
	CONFIDENCE = 'confidence'
	MATCH_TIME = 'match_time'
	OFFSET = 'offset'
	OFFSET_SECS = 'offset_seconds'

	def __init__(self):
		super(Dejavu, self).__init__()

		if not os.path.isfile('database/fingerprint_table.csv'):
			self.fingerprint_table = pd.DataFrame({'FIELD_HASH':pd.Series([]),
					   'FIELD_SONG_ID':pd.Series([]),
					   'FIELD_OFFSET':pd.Series([])})
		else:
			self.fingerprint_table = pd.read_csv('database/fingerprint_table.csv',\
														encoding='utf-8')
		if not os.path.isfile('database/songs_table.csv'):
			self.songs_table = pd.DataFrame({'FIELD_SONGNAME':pd.Series([]),
					   'FIELD_FILE_SHA1':pd.Series([]),
					   'FIELD_FINGERPRINTED':pd.Series([])})
		else:
			self.songs_table = pd.read_csv('database/songs_table.csv', encoding='utf-8')
		
		self.limit = None
		self.get_fingerprinted_songs()

	def fingerprint_directory(self, path, extensions, nprocesses=None):
		# Try to use the maximum amount of processes if not given.
		filenames_to_fingerprint = []
		for filename, _ in decoder.find_files(path, extensions):

			# don't refingerprint already fingerprinted files
			if decoder.unique_hash(filename) in self.songhashes_set:
				print ("%s already fingerprinted, continuing..." % filename)
				continue

			filenames_to_fingerprint.append(filename)

		for filename_to_fingerprint in filenames_to_fingerprint:
			self._fingerprint_worker(filename_to_fingerprint)
		print("Done with fingerprinting")
		
		self.fingerprint_table.to_csv('database/fingerprint_table.csv',encoding='utf-8',index=False)
		self.songs_table.to_csv('database/songs_table.csv',encoding='utf-8',index=False)
		print('Saved database successfully')
	
	def find_matches(self, samples, Fs=fingerprint.DEFAULT_FS):
		hashes = fingerprint.fingerprint(samples, Fs=Fs)
		return self.return_matches(hashes)

	def align_matches(self, matches):
		"""
			Finds hash matches that align in time with other matches and finds
			consensus about which hashes are "true" signal from the audio.

			Returns a dictionary with match information.
		"""
		# align by diffs
		diff_counter = {}
		largest = 0
		largest_count = 0
		song_id = -1

		for tup in matches:
			sid, diff = tup
			if diff not in diff_counter:
				diff_counter[diff] = {}
			if sid not in diff_counter[diff]:
				diff_counter[diff][sid] = 0
			diff_counter[diff][sid] += 1

			if diff_counter[diff][sid] > largest_count:
				largest = diff
				largest_count = diff_counter[diff][sid]
				song_id = sid

		# extract idenfication
		song = self.get_song_by_id(song_id)
		
		songname = song[0] if song else None

		# return match info
		nseconds = round(float(largest) / fingerprint.DEFAULT_FS *
						 fingerprint.DEFAULT_WINDOW_SIZE *
						 fingerprint.DEFAULT_OVERLAP_RATIO, 5)
		song = {
			'SONG_ID' : song_id,
			'SONG_NAME' : songname,
			'CONFIDENCE' : largest_count,
			'OFFSET' : int(largest),
			'OFFSET_SECS' : nseconds,
			'FIELD_FILE_SHA1' : song[1],}
		return song
	
	def recognize(self, recognizer, *options, **kwoptions):
		r = recognizer(self)
		return r.recognize(*options, **kwoptions)

	def get_fingerprinted_songs(self):
		# get songs previously indexed
		self.songs = self.get_songs()
		self.songhashes_set = set()  # to know which ones we've computed before
		for index, song in self.songs.iterrows():
			song_hash = song['FIELD_FILE_SHA1']
			self.songhashes_set.add(song_hash)
	
	def get_songs(self):
		"""
		Returns all fully fingerprinted songs in the database.
		"""
		return self.songs_table
		
	def insert_song(self, song_name, file_hash):
		"""
		Inserts a song name into the database, returns the new
		identifier of the song.

		song_name: The name of the song.
		"""
		self.songs_table = self.songs_table.append(pd.DataFrame([[song_name, file_hash, \
										np.nan]],columns=['FIELD_SONGNAME', \
											'FIELD_FILE_SHA1', 'FIELD_FINGERPRINTED']),\
														ignore_index=True)
		return (len(self.songs_table)-1)
		
	def insert_hashes(self, sid, hashes):
		"""
		Insert a multitude of fingerprints.

		   sid: Song identifier the fingerprints belong to
		hashes: A sequence of tuples in the format (hash, offset)
		-   hash: Part of a sha1 hash, in hexadecimal format
		- offset: Offset this hash was created from/at.
		"""
		values = []
		for hash1, offset in hashes:
			values.append((hash1, sid, offset))
		hash_table = pd.DataFrame(values,columns=['FIELD_HASH', 'FIELD_SONG_ID', 'FIELD_OFFSET'])
		self.fingerprint_table = self.fingerprint_table.append(hash_table,ignore_index=True)

	def set_song_fingerprinted(self, sid):
		"""
		Sets a specific song as having all fingerprints in the database.

		sid: Song identifier
		"""
		self.songs_table.loc[sid] = list(self.songs_table.loc[sid])[:-1]+[1]
	
	def get_song_by_id(self, sid):
		"""
		Return a song by its identifier

		sid: Song identifier
		"""
		return list(self.songs_table.loc[sid])
	
	def return_matches(self, hashes):
		"""
		Searches the database for pairs of (hash, offset) values.

		hashes: A sequence of tuples in the format (hash, offset)
		-   hash: Part of a sha1 hash, in hexadecimal format
		- offset: Offset this hash was created from/at.

		Returns a sequence of (sid, offset_difference) tuples.

					  sid: Song identifier
		offset_difference: (offset - database_offset)
		"""
		# Create a dictionary of hash => offset pairs for later lookups
		mapper = {}
		for hash_val, offset in hashes:
			mapper[hash_val] = offset
		matches=[]
		# Get an iteratable of all the hashes we need
		values = list(mapper.keys())
		# Create our IN part of the query
		values = pd.DataFrame({'FIELD_HASH':pd.Series(values)})
		new = self.fingerprint_table.merge(values, how = 'inner', on = ['FIELD_HASH'])
		for index, row in new.iterrows():
			hash1, sid, offset = row
			matches.append((sid, offset - mapper[hash1]))
		return matches

	def _fingerprint_worker(self, filename, limit=None, song_name=None):
		# Pool.imap sends arguments as tuples so we have to unpack
		# them ourself.
		
		songname, extension = os.path.splitext(os.path.basename(filename))
		song_name = song_name or songname
		channels, Fs, file_hash = decoder.read(filename, limit)
		result = set()
		channel_amount = len(channels)

		for channeln, channel in enumerate(channels):
			# TODO: Remove prints or change them into optional logging.
			print("Fingerprinting channel %d/%d for %s" % (channeln + 1,
														   channel_amount,
														   filename))
			hashes = fingerprint.fingerprint(channel, Fs=Fs)
			print("Finished channel %d/%d for %s" % (channeln + 1, \
												channel_amount, filename))
			result |= set(hashes)
		sid = self.insert_song(song_name, file_hash)
		# add song data to songs dataframe
		self.insert_hashes(sid, list(result))
		# add fingerprints of the song to fingerprints dataframe
		self.set_song_fingerprinted(sid)
		# add information that fingerprinted song has been added to fingerprint dataframe
		self.get_fingerprinted_songs()
		print('Song added to database')

def grouper(iterable, n, fillvalue=None):
	args = [iter(iterable)] * n
	return (filter(None, values) for values
			in itertools.zip_longest(fillvalue=fillvalue, *args))

def chunkify(lst, n):
	"""
	Splits a list into roughly n equal parts.
	http://stackoverflow.com/questions/2130016/splitting-a
	-list-of-arbitrary-size-into-only-roughly-n-equal-parts
	"""
	return [lst[i::n] for i in range(n)]
