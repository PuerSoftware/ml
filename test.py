from puerml import Jsonl, Git, DataFrame

FILE_NAME = 'test'
FILE_DIR  = 'test_data'

def test_Jsonl():
	data = [{'text': 'Some text\nNew line', 'cat': 0, 'arr': ['String\nNew line'], 'map': {'text': 'Some\nNew line'}}]
	Jsonl.save(data, FILE_NAME, FILE_DIR)
	data = Jsonl.load_all(FILE_NAME, FILE_DIR)
	print(data)
	print(data[0]['text'])

def test_Git():
	token  = ''
	user   = ''
	repo   = ''
	branch = ''
	file_path = ''

	git = Git(user, repo, branch, token=token)
	# counter = 0
	# for obj in git.load_jsonl(file_path, True):
	# 	if counter > 10:
	# 		break
	# 	print(obj)
	# 	counter += 1
	return git.load_all(file_path)
	
def test_DataFrame():
	data = test_Git()
	print(data)
	df   = DataFrame.from_string(data)
	print(df.header)

if __name__ == '__main__':
	test_Jsonl()
	test_Git()
	test_DataFrame()

