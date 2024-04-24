from puerml  import DataFrame
from pytest  import fixture


class TestDataFrame:
	def _assert_df(self, df):
		for i in range(len(self.header)):
			col = f'h{i}'
			assert df.get(col, i) == self.df.get(col, i), '"Value mismatch in column {col} at index {i}'

	@fixture(autouse=True, scope='class', name='setup_TestDataFrame')
	def setup(cls, request, tmp_path_factory):
		request.cls.location       = str(tmp_path_factory.mktemp('df_test_dir'))
		request.cls.web_location   = 'https://raw.githubusercontent.com/PuerSoftware/puerml_test/main/df_test_data'
		request.cls.file_type      = 'tsv'
		request.cls.max_chunk_size = 1

		request.cls.header         = [f'h{i}' for i in range(10)]
		request.cls.rows           = [
			[f'row{i}-{j}' for j in range(10)]
			for i in range(10) 
		]
		request.cls.df = DataFrame(request.cls.header, request.cls.rows)

	def test_save_local(self):
		DataFrame(self.header, self.rows).save(self.location, self.file_type, self.max_chunk_size)
	
	def test_load_local(self):
		self._assert_df(DataFrame.load(self.location))
	
	def test_load_web(self):
		self._assert_df(DataFrame.load(self.web_location))
		