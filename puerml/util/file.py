import os
import shutil

__all__ = ['File']

class File:
	@staticmethod
	def rm(path):
		if os.path.exists(path):
			if os.path.isdir(path):
				shutil.rmtree(path)
			else:
				os.remove(path)
