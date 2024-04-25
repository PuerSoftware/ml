import os
import shutil
import io
import json
import zipfile
import requests

__all__ = ['Data']


class Data:
	def __init__(self, data=None, file_type=None, is_binary=False):
		self.data       = io.BytesIO(data) if is_binary else io.StringIO(data)
		self.is_binary  = is_binary
		self.file_type  = file_type if data else None
		self.headers    = None
		self.location   = None
		self.from_web   = None
		self.description = ''

	def _read_manifest(self):
		file_loc = os.path.join(self.location, 'manifest.json')
		if self.from_web:
			response = requests.get(file_loc, headers=self.headers)
			return json.loads(response.text)
		else:
			with open(file_loc) as f:
				return json.load(f)

	def _write_manifest(self, location, manifest):
		file_loc = os.path.join(location, 'manifest.json')
		with open(file_loc, 'w') as f:
			return json.dump(manifest, f)

	def _read_web(self, file_loc):
		response = requests.get(file_loc, headers=self.headers, stream=True)
		if response.status_code == 200:
			return response
		return None

	def _read_disk(self, file_loc):
		try:
			if os.path.exists(file_loc):
				mode = 'rb' if self.is_binary else 'r'
				return open(file_loc, mode)
		except Exception as e:
			print(f'Failed to open file {file_loc}: {e}')
		return None

	def _file_generator(self):
		if self.data:
			yield self.data
		else:
			if os.path.exists(f'{location}.{self.file_type}'):
				with open(location, 'rb' if self.is_binary else 'r') as f:
					yield f
			else:
				n = 0
				while True:
					file_name  = f'{n}.{self.file_type}' if self.file_type else str(n)
					file_loc = os.path.join(self.location, file_name)
					read = self._read_web if self.from_web else self._read_disk
					file = read(file_loc)
					if file:
						yield file
						if not self.from_web:
							file.close()
						n += 1
					else:
						break

	def _content_generator(self):  # TODO: modify to produce chunks efficiently
		for file in self._file_generator():
			if self.from_web:
				yield file.content if self.is_binary else file.text
			else:
				yield file.read()

	def _chunk_generator(self, max_size=1024*1024):
		for file in self._file_generator():
			if self.from_web:
				for chunk in file.iter_content(chunk_size=max_size):
					yield chunk if self.is_binary else chunk.decode('utf-8')
			else:
				while True:
					chunk = file.read(max_size)
					if not chunk:
						break
					yield chunk

	def _line_generator(self):
		for file in self._file_generator():
			iterator = file.iter_lines(decode_unicode=True) if self.from_web else file
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
			d.file_type   = manifest['type'].lower() if manifest['type'] else None
		else:
			d.description = ''
			d.is_binary   = is_binary
			d.file_type   = file_type

		return d

	def save(self, location, max_size=None, description=''):
		if max_size is None:
			location = f'{location}.{self.file_type}'
			with open(location, 'wb' if self.is_binary else 'w') as f:
				f.write(self.data.read())
			return

		if os.path.exists(location):
			shutil.rmtree(location)
		os.makedirs(location)

		def _write(l, t, n, m, c):
			fn = f'{n}.{t}' if t else str(n)
			l = os.path.join(l, fn)
			with open(l, m) as f:
				f.write(c)

		if self.is_binary:
			n = 0
			for chunk in self._chunk_generator(max_size):
				_write(location, self.file_type, n, 'wb', chunk)
				n += 1
		else:
			n = 0
			buffer, buffer_size = [], 0
			for line in self._line_generator():
				line_size        = len(line.encode('utf-8'))
				next_buffer_size = line_size + buffer_size
				if next_buffer_size > max_size and len(buffer) > 0:
					_write(location, self.file_type, n, 'w', '\n'.join(buffer))
					buffer, buffer_size = [], 0
					n += 1
				buffer.append(line)
				buffer_size = next_buffer_size
			if buffer_size > 0:
				_write(location, self.file_type, n, 'w', '\n'.join(buffer))
				n += 1

		self._write_manifest(location, {
			'description' : description or self.description,
			'count'       : n,
			'type'        : self.file_type,
			'is_binary'   : self.is_binary
		})

	def zip(self, location):
		self.data = io.BytesIO()
		with zipfile.ZipFile(self.data, 'w') as f:
			for root, _, files in os.walk(location):
				for file in files:
					file_path = os.path.join(root, file)
					f.write(file_path, os.path.relpath(file_path, start=location))
		self.data.seek(0)
		return self

	def unzip(self, location):
		buffer = io.BytesIO()
		for f in self._file_generator():
			buffer.write(f.read())

		buffer.seek(0)
		if os.path.exists(location):
			shutil.rmtree(location)
		with zipfile.ZipFile(buffer, 'r') as f:
			f.extractall(location)

	@property
	def lines(self):
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
