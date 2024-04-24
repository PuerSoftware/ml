import os
import json

from .data import Data

__all__ = ['Jsonl']


class Jsonl:
	@classmethod
	def _traverse(cls, data, f):
		if isinstance(data, dict):
			return {key: cls._traverse(value, f) for key, value in data.items()}
		elif isinstance(data, list):
			return [cls._traverse(item, f) for item in data]
		elif isinstance(data, str):
			return f(data)
		else:
			return data

	@classmethod
	def _escape(cls, data):
		return cls._traverse(data, lambda s: s.replace('\n', '\\n'))
	
	@classmethod
	def _unescape(cls, data):
		return cls._traverse(data, lambda s: s.replace('\\n', '\n'))

	@classmethod
	def save(cls, data, location, max_size=99*1024):
		data = '\n'.join([cls.encode(item) for item in data])
		Data(data, 'jsonl').save(location, max_size)

	@classmethod
	def load(cls, location, generator=True, http_headers=None):
		data_object = Data.load(location, headers=http_headers)
		if generator:
			return (cls.decode(line) for line in data_object.lines)
		else:
			return [cls.decode(line) for line in data_object.lines]

	@classmethod
	def encode(cls, item):
		return json.dumps(cls._escape(item))

	@classmethod
	def decode(cls, line):
		return cls._unescape(json.loads(line.strip()))