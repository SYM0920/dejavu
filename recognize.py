# encoding: utf-8
import fingerprint as fingerprint
import decoder as decoder
import numpy as np
import pyaudio
import time


class BaseRecognizer(object):

	def __init__(self, dejavu):
		self.dejavu = dejavu
		self.Fs = fingerprint.DEFAULT_FS

	def _recognize(self, data):
		matches = []
		print("Finding Matches.")
		for d in data:
			matches.extend(self.dejavu.find_matches(d, Fs=self.Fs))
		if len(matches)>0:
			print("Found {} Matches.".format(len(matches)))
		return self.dejavu.align_matches(matches)

	def recognize(self):
		pass  # base class does nothing


class FileRecognizer(BaseRecognizer):
	def __init__(self, dejavu):
		super(FileRecognizer, self).__init__(dejavu)

	def recognize_file(self, filename):
		frames, self.Fs, file_hash = decoder.read(filename)
		t = time.time()
		match = self._recognize(frames)
		t = time.time() - t
		return t

	def recognize(self, filename):
		return self.recognize_file(filename)