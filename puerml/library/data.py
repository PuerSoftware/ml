import os
import io
import json
import requests


class Data:
	def __init__(self, data=None, is_binary=False):
		self.data      = io.BytesIO(data) if is_binary else io.StringIO(data)
		self.is_binary = None
		self.headers   = None
		self.location  = None
		self.from_web  = None
		self.file_type = None

	def _read_manifest(self):
		file_loc = os.path.join(self.location, 'manifest.json')
		if self.from_web:
			response = requests.get(file_loc, headers=self.headers)
			return json.loads(response.text)
		else:
			with open(file_loc) as f:
				return json.load(f)

	def _write_manifest(self, manifest):
		file_loc = os.path.join(self.location, 'manifest.json')
		with open(file_loc, 'w') as f:
			return json.dump(f, manifest)

	def _read_web(self, file_loc):
		response = requests.get(file_loc, headers=self.headers, stream=True)
		if response.status_code == 200:
			return response
		return None

	def _read_disk(self, file_loc):
		mode = 'rb' if self.is_binary else 'r'
		if os.path.exists(file_loc):
			with open(file_loc, mode) as f:
				return f
		return None

	def _file_generator(self):
		if self.data:
			yield self.data
		else:
			n = 0
			while True:
				file_loc = os.path.join(self.location, f'{n}.{self.file_type}')
				read     = self._read_web if from_web else self._read_disk
				if file := read(file_loc):
					yield file
					n += 1
				else:
					break

	def _content_generator(self):  # TODO: modify to produce chunks efficiently
		for file in self._file_generator():
			if self.from_web:
				yield file.content if self.is_binary else file.text
			else:
				yield file.read()

	def _line_generator(self):
		for file in self._file_generator():
			iterator = file.iter_lines(decode_unicode=True) if self.from_web else item
			for line in iterator:
				yield line.strip()

	################################################################################

	@staticmethod
	def load(location, file_type=None, headers=None, is_binary=False):
		d = Data()
		d.data     = None
		d.location = location
		d.headers  = headers
		d.from_web = location.startswith('http')

		if file_type is None:
			manifest = d._read_manifest()
			d.description = manifest['description']
			d.is_binary   = manifest['is_binary']
			d.file_type   = manifest['type'].lower()
		else:
			d.description = ''
			d.is_binary   = is_binary
			d.file_type   = file_type

		return d

	@staticmethod
	def load_file(location):  # TODO: implement for single files
		...

	def save(self, location, max_size=None, description=''):
		if not os.path.exists(location):
			os.makedirs(location)

		n = 0
		for content in self._content_generator():
			if content:
				chunk_size = max_size or len(content)
				start      = 0
				while start < len(content):
					end       = start + chunk_size
					chunk     = content[start:end]
					file_path = os.path.join(location, f'{n}.{self.file_type}')
					mode      = 'wb' if self.is_binary else 'w'
					with open(file_path, mode) as f:
						f.write(chunk)
						start = end
						n += 1

		self._write_manifest({
			'description' : description or self.description,
			'count'       : n,
			'type'        : self.file_type,
			'is_binary'   : self.is_binary
		})

	def items(self): # TODO: add line preprocessing
		return self._line_generator()

	def content(self):
		content = ''
		for file_content in self._content_generator(): # TODO: add binary handling
			content += file_content
		return content

	def batches(self, batch_size=10): # TODO: add line preprocessing
		batch = []
		for line in self._line_generator():
			if len(batch) < batch_size:
				batch.append(line)
			else:
				yield batch
				batch = []
		if len(batch) > 0:
			yield batch

	def chunks(self, chunk_size=1024):
		...




















