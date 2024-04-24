import json

from inspect import isgenerator
from pytest  import fixture
from puerml  import Jsonl


class TestJsonl:
	@fixture(autouse=True, scope='class', name='setup_TestJsonl')
	def setup(cls, request, tmp_path_factory):
		request.cls.location     = str(tmp_path_factory.mktemp('json_test_dir'))
		request.cls.web_location = 'https://raw.githubusercontent.com/PuerSoftware/puerml_test/main/jsonl_test_data'
		request.cls.test_data = [{
				'int'    : i,
				'string' : f'foo\n{i}',
				'list'   : [f'bar\n{j}' for j in range(i+1)],
				'dict'   : {f'baz{k}': k for k in range(i+1)}
			}
			for i in range(10)
		]

	def test_save_local(self):
		Jsonl.save(self.test_data, self.location)

	def test_load_local(self):
		loaded_data = Jsonl.load(self.location, generator=False)
		assert json.dumps(loaded_data) == json.dumps(self.test_data), 'Mismatch saved and loaded data'

	def test_load_local_generator(self):
		loaded_data = Jsonl.load(self.location)
		assert isgenerator(loaded_data)
		assert json.dumps(list(loaded_data)) == json.dumps(self.test_data), 'Mismatch saved and loaded data'

	def test_load_web(self):
		loaded_data = Jsonl.load(self.web_location, generator=False)
		assert json.dumps(loaded_data) == json.dumps(self.test_data), 'Mismatch saved and loaded data'
	