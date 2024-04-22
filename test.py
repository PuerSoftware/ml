from puerml import Jsonl

FILE_NAME = 'test'
FILE_DIR  = 'test_data'

def test_Jsonl():
	data = [{'text': 'Some text\nNew line', 'cat': 0, 'arr': ['String\nNew line'], 'map': {'text': 'Some\nNew line'}}]
	Jsonl.save(data, FILE_NAME, FILE_DIR)
	data = Jsonl.load_all(FILE_NAME, FILE_DIR)
	print(data)
	print(data[0]['text'])

if __name__ == '__main__':
	test_Jsonl()
