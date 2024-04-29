import netrc
import requests
import base64
import os

class Repo:
	def __init__(self, repo, owner, token=None, host='api.github.com', branch='master'):
		self.repo   = repo
		self.owner  = owner
		self.host   = host
		self.branch = branch
		self.token  = token if token else self._get_token_from_netrc()

		if not self.token:
			raise ValueError('A GitHub token must be provided or set in .netrc')

	#################################################################

	def _url(self, extra=''):
		return os.path.join(f'https://{self.host}/repos/{self.owner}/{self.repo}', extra)

	def _headers(self):
		return {
			'Authorization' : f'token {self.token}',
			'Content-Type'  : 'application/json'
		}

	def _request(self, method='get', path='', data=None):
		url = self._url(path)
		kwargs = {'headers': self._headers()}
		if data:
			kwargs['json'] = data
		response = getattr(requests, method)(url, **kwargs)
		return response

	def _get    (self, path)       : return self._request('get', path)
	def _put    (self, path, data) : return self._request('put', path, data)
	def _delete (self, path)       : return self._request('delete', path, data)

	def _get_token_from_netrc(self):
		try:
			auth_info = netrc.netrc().authenticators(self.host)
			if auth_info:
				print('Retrieved token from .netrc')
				return auth_info[2]  # Return the token
		except FileNotFoundError:
			print('.netrc file not found')
		except netrc.NetrcParseError as e:
			print(f'Error parsing .netrc file: {e}')
		return None

	#################################################################

	def commit(self, path, content, message=None, branch=None):
		branch  = branch or self.branch
		message = message or 'Automated commit'
		content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
		data = {
			'message' : message,
			'content' : content,
			'branch'  : branch
		}
		# Attempt to get the SHA of the existing file to update it
		response = self.get(path)
		if response.status_code == 200:
			data['sha'] = response.json().get('sha', '')

		return self.put(path, data).json()

	def delete(self, path, message):
		response = self.get(path)
		if response.status_code == 200:
			sha = response.json().get('sha', '')
			if sha:
				data = {
					'message' : message,
					'sha'     : sha,
					'branch'  : self.branch
				}
				return self._delete().json()
			else:
				print('File SHA not found, cannot delete.')
		else:
			print('File not found or access denied.')
		return None