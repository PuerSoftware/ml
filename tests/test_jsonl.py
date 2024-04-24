import json
import pytest

from inspect import isgenerator
from puerml  import Jsonl

@pytest.fixture(scope='session')
def temp_dir(tmp_path_factory):
    return tmp_path_factory.mktemp('json_test_dir')
    
@pytest.fixture(scope='session')
def test_data():
    return [{
			'int'    : i,
			'string' : f'foo\n{i}',
			'list'   : [f'bar\n{j}' for j in range(i+1)],
			'dict'   : {f'baz{k}': k for k in range(i+1)}
		}
		for i in range(10)
	]

def test_Jsonl_save_and_load_local(temp_dir, test_data):
    location = str(temp_dir)
    # save
    Jsonl.save(test_data, location)
    # load
    loaded_data = Jsonl.load(location, generator=False)
    assert json.dumps(loaded_data) == json.dumps(test_data)

def test_Jsonl_save_and_load_local_generator(temp_dir, test_data):
    location = str(temp_dir)
    # save
    Jsonl.save(test_data, location)
    # load
    loaded_data = Jsonl.load(location)
    assert isgenerator(loaded_data)
    assert json.dumps(list(loaded_data)) == json.dumps(test_data)

def test_Jsonl_load_web(test_data):
    location = 'https://raw.githubusercontent.com/PuerSoftware/puerml_test/main/jsonl_test_data'
    # load
    loaded_data = Jsonl.load(location, generator=False)
    assert json.dumps(loaded_data) == json.dumps(test_data)