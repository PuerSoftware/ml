import pytest

from inspect import isgenerator
from puerml  import DataFrame

@pytest.fixture(scope='session')
def temp_df_dir(tmp_path_factory):
	return tmp_path_factory.mktemp('df_test_dir')


@pytest.fixture(scope='session')
def test_df_data():
	header = [f'h{i}' for i in range(10)]
	rows   = [[f'row{i}-{j}' for j in range(10)]
		for i in range(10) 
	]
	return header, rows


def test_DataFrame_save_and_load_local(temp_df_dir, test_df_data):
	location = str(temp_df_dir)
	header, rows = test_df_data
	# save
	df1 = DataFrame(header, rows).save(location, 'tsv', 1)
	# load
	df2 = DataFrame.load(location)
	assert df1.get('h5', 5) == df2.get('h5', 5)

def test_DataFrame_load_web(test_df_data):
	location     = 'https://raw.githubusercontent.com/PuerSoftware/puerml_test/main/df_test_data'
	header, rows = test_df_data
	df1          = DataFrame(header, rows)
	# load
	df2 = DataFrame.load(location)
	assert df1.get('h5', 5) == df2.get('h5', 5)
