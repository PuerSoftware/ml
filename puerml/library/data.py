import magic

'''
Single file
mypackage.jsonl

Multiple files
mypackage.jsonl/0
mypackage.jsonl/1

Load - Save
Data.load('mypackage.jsonl')
Data.save('mypackage.jsonl', max_size)
'''

############################################################

class DataReader:
	def __init__(self):
		self._data     = None
		self.is_binary = None
		self.is_local  = False

	def _test_content(self, content):
		mime           = magic.Magic(mime=True)
        file_type      = mime.from_buffer(content)
        self.is_binary = not file_type.startswith('text/')

	def _read_remote(self, location, headers):
		response = requests.get(location, headers=headers, stream=True)
		if response.status_code == 200:
			if self.is_binary is None:
				self._test_content(response.content)

			return response
		return None

	def _read_local(self, location):
		try:
			if os.path.exists(location):
				if self.is_binary is None:
					with open(location, 'rb') as f:
						self._test_content(f.read(1024))

				mode = 'rb' if self.is_binary else 'r'
				return open(location, mode)
		except Exception as e:
			print(f'Failed to read file "{location}": {e}')
		return None

	def _read(self, location, headers=None):
		if self.is_local:
			return self._read_local(location)
		return self._read_remote(location, headers)

	def _file_generator(self, location, headers=None):
		if self._data:
			yield self._data
		else:
			n = 0
			while True:
				loc  = os.path.join(location, str(n))
				file = self._read(loc, headers)
				if file:
					# reading package
					yield file
					if self.is_local: file.close()
					n += 1
				elif n == 0:
					# Reading single file
					file = self._read(location, headers)
					if file:
						yield file
						if self.is_local: file.close()
						break
				else:
					break

	def _line_generator(self):
		if self.is_binary:
			raise Exception('Can not iterate lines of binary file')
		for file in self._file_generator():
			iterator = file if self.is_local else file.iter_lines(decode_unicode=True)
			for line in iterator:
				yield line.strip()

	def _chunk_generator_binary(self, max_size):
		for f in self._file_generator():
			if self.is_local:
				while True:
					b = f.read(max_size)
					if not b:
						break
					yield b
			else:
				for b in f.iter_content(chunk_size=max_size):
					yield b

	def _chunk_generator_text(self, max_size)
		b, b_size, n = [], 0, 0
		for l in self._line_generator():
			l_size = len(l.encode('utf-8'))
			if l_size + b_size > max_size and len(b) > 0:
				yield '\n'.join(b)
				b, b_size, n = [], 0, n + 1
			b.append(l)
			b_size += l_size

		if b_size > 0:
			yield '\n'.join(b)

	def _chunk_generator(self, max_size=1024**4):
		if self.is_binary:
			return self._chunk_generator_binary(max_size)
		return self._chunk_generator_text(max_size)

	@staticmethod
	def from_location(location):
		reader = DataReader()
		reader.is_local = not location.startswith('http')
		return reader

	@staticmethod
	def from_data(data):
		reader = DataReader()
		if isinstance(data, bytes):
			reader._data     = io.BytesIO(data)
			reader.is_binary = True
			return reader
		elif isinstance(data, str):
			reader._data     = io.StringIO(data)
			reader.is_binary = False
			return reader
		raise Exception(f'Expected "str" or "bytes", got "{type(data)}"')

############################################################

class DataWriter:
	self.__init__(self, reader):
		self._reader = reader

	def write_single_file(self, location):
		location = f'{location}.{self.file_type}'
			with open(location, 'wb' if self._reader.is_binary else 'w') as f:
				f.write(next(self._file_generator()).read())

	def write_package(self, location, max_size):
		n = 0
		for chunk in self._chunk_generator(max_size):
			loc  = os.path.join(location, str(n))
			mode = 'wb' if self._reader.is_binary else 'w'
			with open(loc, mode) as f:
				f.write(chunk)
			n += 1

############################################################

class Data:
	def __init__(self, reader):
		self.reader = reader
		if data:
			reader = DataReader.from_data(data)

	@staticmethod
	def load(location):
		return Data(DataReader.from_location(location))

	def load_data(data):
		return Data(DataReader.from_data(data))

	def save(self, location, max_size=None):
		writer = DataWriter(self.reader)
		if max_size is None:
			writer.write_single_file(location)
		else:
			writer.write_package(location, max_size)

	def zip(self, location):
		data = io.BytesIO()
		with zipfile.ZipFile(data, 'w') as f:
			for root, _, files in os.walk(location):
				for file in files:
					file_path = os.path.join(root, file)
					f.write(file_path, os.path.relpath(file_path, start=location))
		data.seek(0)
		self.reader._data = data
		return self

	def unzip(self, location):
		buffer = io.BytesIO()
		for f in self.reader._file_generator():
			buffer.write(f.read())

		buffer.seek(0)
		if os.path.exists(location):
			shutil.rmtree(location)

		with zipfile.ZipFile(buffer, 'r') as f:
			f.extractall(location)

	@property
	def lines(self):
		return self._line_generator()

	@property
	def content(self):
		content = ''
		for file_content in self._content_generator():
			content += file_content
		return content

	def batches(self, batch_size=10, preprocess=None):
		if self.is_binary:
			raise Exception('Batch processing is not supported for binary files')
		batch = []
		for line in self._line_generator():
			if len(batch) < batch_size:
				if preprocess:
					line = preprocess(line)
				batch.append(line)
			else:
				yield batch
				batch = []
		if len(batch) > 0:
			yield batch

############################################################