from functools           import wraps
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

def handle_http_error(f):
	@wraps(f)
	def _decorator(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except HTTPError as http_err:
			print(f'HTTP error occurred: {http_err}')
		except ConnectionError as conn_err:
			print(f'Connection error occurred: {conn_err}')
		except Timeout as timeout_err:
			print(f'Timeout error occurred: {timeout_err}')
		except RequestException as req_err:
			print(f'An error occurred: {req_err}')
		except Exception as e:
			print(f'An unexpected error occurred: {e}')	
	return _decorator
	