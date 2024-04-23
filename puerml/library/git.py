import os
import requests

from .decorators import handle_http_error
from .jsonl      import Jsonl

__all__ = ['Git']


class Git:
	def __init__(self, 
		user,
		repo,
		branch   = 'main',
		host     = 'github.com',
		raw_host = 'raw.githubusercontent.com',
		token    = None,
		encoding = 'utf-8'
	):
		for k, v in locals().items():
			setattr(self, k, v)
	
	def _split_path(self, path):
		dir_name            = os.path.dirname(path)
		file_name           = os.path.basename(path)
		file_name, file_ext = os.path.splitext(file_name) 
		return dir_name, file_name, file_ext

	def _make_raw_url(self, file_path):
		return os.path.join('https://', self.raw_host, self.user, self.repo, self.branch, file_path)

	@handle_http_error
	def _get_response(self, file_path, stream):
		dir_name, file_name, ext_name = self._split_path(file_path)
		url     = self._make_raw_url(file_path)
		headers = {}
		if self.token:
			headers['Authorization'] = f'token {self.token}'
			
		with requests.get(url, headers=headers, stream=stream) as response:
			if response.status_code == 200:
				yield response
			elif response.status_code == 404:
				chunk = 0
				while True:
					file_path = os.path.join(dir_name, f'{file_name}_{chunk}{ext_name}')
					url       = self._make_raw_url(file_path)
					with requests.get(url, headers=headers, stream=stream) as response:
						if response.status_code == 404:
							break
						yield response
					chunk += 1
			else:
				response.raise_for_status()
	
	def load(self, file_path, process_line=None):
		for response in self._get_response(file_path, True):
			for line in response.iter_lines():
				if line and line.strip():
					line = line.decode(response.encoding or self.encoding)
					yield process_line(line) if process_line else line

	def load_all(self, file_path, process_line=None, lines=False) -> list[str] | str:
		if lines:
			return list(self.load(file_path, process_line))
		else:
			s = ''
			for response in self._get_response(file_path, False):
				s += response.content.decode(response.encoding or self.encoding)
			return s

	def load_jsonl(self, file_path, lines=True):
		if lines:
			return self.load(file_path, Jsonl.decode)
		else:
			return self.load_all(file_path)
