import os
import json

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
			return data  # Return the data unchanged if it's not a dict, list, or string.

	@classmethod
	def _escape(cls, data):
		return cls._traverse(data, lambda s: s.replace('\n', '\\n'))
	
	@classmethod
	def _unescape(cls, data):
		return cls._traverse(data, lambda s: s.replace('\\n', '\n'))

	@classmethod
	def save(cls, data, name, file_dir, max_file_size=52428800):
		'Writes data to jsonl files ensuring each file does not exceed the specified max_file_size'
		if not isinstance(data, list):
			raise Exception('Data must be a list')
		chunk_num    = 0
		current_size = 0
		file         = None

		def open_new_file():
			nonlocal file, current_size, chunk_num
			if file:
				file.close()
			file_path    = os.path.join(file_dir, f'{name}_{chunk_num}.jsonl')
			file         = open(file_path, 'w')
			current_size = 0
			chunk_num += 1

		open_new_file()

		for item in data:
			jsonl_line = json.dumps(cls._escape(item)) + '\n'
			line_size  = len(jsonl_line.encode('utf-8'))
			if max_file_size and current_size + line_size > max_file_size:
				open_new_file()
			file.write(jsonl_line)
			current_size += line_size

		if file:
			file.close()

	@classmethod
	def load_all(cls, name, file_dir):
		'Load all records at once'
		all = []
		files = sorted([os.path.join(file_dir, f) for f in os.listdir(file_dir) if f.startswith(name) and f.endswith('.jsonl')])
		for file_path in files:
			with open(file_path, 'r') as file:
				for line in file:
					all.append(cls._unescape(json.loads(line.strip())))

		return all

	@classmethod
	def load(cls, name, file_dir, batch_size=None):
		'Generator to read jsonl files in batches'
		if batch_size is None:
			return Jsonl.load_all(name, file_dir)
		files = sorted([os.path.join(file_dir, f) for f in os.listdir(file_dir) if f.startswith(name) and f.endswith('.jsonl')])
		for file_path in files:
			with open(file_path, 'r') as file:
				batch = []
				for line in file:
					batch.append(cls._unescape(json.loads(line.strip())))
					if len(batch) == batch_size:
						yield batch
						batch = []
				if batch:
					yield batch
