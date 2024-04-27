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
	
	def _unzip(self, location):
		Data.load(location).unzip(self.location)
		checksums = self._get_checksums(self.location)
		self._assert_chesums(checksums)

	@fixture(autouse=True, scope='class', name='setup_TestData')
	def setup(cls, request, tmp_path_factory):
		location     = str(tmp_path_factory.mktemp('data_test_dir'))
		txt_location = os.path.join(location, 'txt')
		bin_location = os.path.join(location, 'bin')
		txt_content  = cls._make_txt_content(10)
		bin_content  = cls._make_bin_content(10)

		cls._write_content(txt_location, txt_content, 'w')
		cls._write_content(bin_location, bin_content, 'wb')
		
		checksums = cls._get_checksums(location)

		################################################
		  
		request.cls.location                 = location
		request.cls.web_location_package     = 'https://raw.githubusercontent.com/PuerSoftware/puerml_test/main/test.zip'
		request.cls.web_location_single_file = 'https://raw.githubusercontent.com/PuerSoftware/puerml_test/main/test_single.zip'
		request.cls.checksums                = checksums
		request.cls.max_chunk_size           = 100

	def test_zip_local_package(self): 
		Data.zip(self.location).save(self.location, self.max_chunk_size)

	def test_unzip_local_load(self):
		self._unzip(self.location + '.zip')

	def test_zip_local_single_file(self): 
		Data.zip(self.location).save(self.location)
	
	def test_unzip_local_load_single_file(self):
		self._unzip(self.location + '.zip')

	def test_unzip_web_load_package(self):
		self._unzip(self.web_location_package)

	def test_unzip_web_load_single_file(self):
		self._unzip(self.web_location_single_file)
