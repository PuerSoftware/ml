import os
import json

from inspect import isgenerator
from pytest  import fixture
from puerml  import Jsonl


class TestJsonl:
	@fixture(autouse=True, scope='class', name='setup_TestJsonl')
	def setup(cls, request, tmp_path_factory):
		request.cls.location                 = os.path.join(str(tmp_path_factory.mktemp('jsonl_test_dir')), 'test.jsonl') 
		request.cls.web_location_package     = 'https://raw.githubusercontent.com/PuerSoftware/puerml_test/main/test.jsonl'
		request.cls.web_location_single_file = 'https://raw.githubusercontent.com/PuerSoftware/puerml_test/main/test_single.jsonl'
		request.cls.test_data = [{
				'int'    : i,
				'string' : f'foo\n{i}',
				'list'   : [f'bar\n{j}' for j in range(i+1)],
				'dict'   : {f'baz{k}': k for k in range(i+1)}
			}
			for i in range(10)
		]

	def test_save_local_package(self):
		Jsonl.save(self.test_data, self.location)
	
	def test_load_local_package(self):
		loaded_data = Jsonl.load(self.location, generator=False)
		assert json.dumps(loaded_data) == json.dumps(self.test_data), 'Mismatch saved and loaded data'

	def test_load_local_package_generator(self):
		loaded_data = Jsonl.load(self.location)
		assert isgenerator(loaded_data)
		assert json.dumps(list(loaded_data)) == json.dumps(self.test_data), 'Mismatch saved and loaded data'

	def test_save_local_single_file(self):
		Jsonl.save(self.test_data, self.location, max_size=None)
	
	def test_load_local_single_file(self):
		loaded_data = Jsonl.load(self.location, generator=False)
		assert json.dumps(loaded_data) == json.dumps(self.test_data), 'Mismatch saved and loaded data'

	def test_load_web_package(self):
		loaded_data = Jsonl.load(self.web_location_package, generator=False)
		assert json.dumps(loaded_data) == json.dumps(self.test_data), 'Mismatch saved and loaded data'
	
	def test_load_web_single_file(self):
		loaded_data = Jsonl.load(self.web_location_single_file, generator=False)
		assert json.dumps(loaded_data) == json.dumps(self.test_data), 'Mismatch saved and loaded data'