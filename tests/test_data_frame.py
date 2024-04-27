import os

from puerml  import DataFrame
from pytest  import fixture


class TestDataFrame:
	def _assert_df(self, df):
		for i in range(len(self.header)):
			col = f'h{i}'
			assert df.get(col, i) == self.df.get(col, i), '"Value mismatch in column {col} at index {i}'

	@fixture(autouse=True, scope='class', name='setup_TestDataFrame')
	def setup(cls, request, tmp_path_factory):
		request.cls.location                 = os.path.join(str(tmp_path_factory.mktemp('df_test_dir')), 'test.tsv')
		request.cls.web_location_package     = 'https://raw.githubusercontent.com/PuerSoftware/puerml_test/main/test.tsv'
		request.cls.web_location_single_file = 'https://raw.githubusercontent.com/PuerSoftware/puerml_test/main/test_single.tsv'
		request.cls.file_type      = 'tsv'
		request.cls.max_chunk_size = 1

		request.cls.header         = [f'h{i}' for i in range(10)]
		request.cls.rows           = [
			[f'row{i}-{j}' for j in range(10)]
			for i in range(10) 
		]
		request.cls.df = DataFrame(request.cls.header, request.cls.rows)

	def test_save_local_package(self):
		DataFrame(self.header, self.rows).save(self.location, self.max_chunk_size)
	
	def test_load_local_package(self):
		self._assert_df(DataFrame.load(self.location))
	
	def test_save_local_single_file(self):
		DataFrame(self.header, self.rows).save(self.location, None)
	
	def test_load__local_single_file(self):
		self._assert_df(DataFrame.load(self.location))

	def test_load_web_package(self):
		self._assert_df(DataFrame.load(self.web_location_package))
	
	def test_load_web_single_file(self):
		self._assert_df(DataFrame.load(self.web_location_single_file))