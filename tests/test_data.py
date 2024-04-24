import os
import hashlib

from puerml  import Data
from pytest  import fixture


class TestData:
	@staticmethod
	def _make_txt_content(count):
		return {
			f'text_file_{i}.txt' : 'Hello world!\n' * (i+1)
			for i in range(count)
		}
	
	@staticmethod
	def _make_bin_content(count):
		return {
			f'bin_file_{i}' : b'Hello world!\n' * (i+1)
			for i in range(count)
		}

	@staticmethod
	def _write(file_name, content, mode):
		with open(file_name, mode) as f:
			f.write(content)
	
	@classmethod
	def _write_content(cls, location, content, mode):
		if not os.path.exists(location):
			os.makedirs(location)
		for file_name, c in content.items():
			cls._write(os.path.join(location, file_name), c, mode)

	@staticmethod
	def _read_checksum(file_path):
		with open(file_path, 'rb') as f:
			return hashlib.md5(f.read()).hexdigest()

	@classmethod
	def _get_checksums(cls, location):
		checksums = {}
		for root, _, files in os.walk(location):
			for file in files:
				file_path = os.path.join(root, file)
				checksums[file_path] = cls._read_checksum(file_path)
		return checksums
				
	def _assert_chesums(self, checksums):
		for file_path, checksum in self.checksums.items():
			assert checksums[file_path] == checksum

	@fixture(autouse=True, scope='class', name='setup_TestData')
	def setup(cls, request, tmp_path_factory):
		base_location  = str(tmp_path_factory.mktemp('data_test_dir'))
		location       = os.path.join(base_location, 'raw')
		zip_location   = os.path.join(base_location, 'zip')

		txt_content  = cls._make_txt_content(10)
		bin_content  = cls._make_bin_content(10)

		txt_location  = os.path.join(location, 'txt')
		bin_location  = os.path.join(location, 'bin')

		cls._write_content(txt_location, txt_content, 'w')
		cls._write_content(bin_location, bin_content, 'wb')
		
		checksums = cls._get_checksums(location)

		################################################
		  
		request.cls.location       = location
		request.cls.web_location   = 'https://raw.githubusercontent.com/PuerSoftware/puerml_test/main/data_test_data/zip'
		request.cls.zip_location   = zip_location
		request.cls.checksums      = checksums
		request.cls.max_chunk_size = 100

	def test_zip_local(self):
		data_object = Data(is_binary=True)
		data_object.zip(self.location)
		data_object.save(self.zip_location, self.max_chunk_size)

	def test_unzip_local(self):
		data_object = Data.load(self.zip_location, is_binary=True)
		data_object.unzip(self.location)
		checksums = self._get_checksums(self.location)
		self._assert_chesums(checksums)
	