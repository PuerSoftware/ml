import re
import sys
import toml


class Version:
	path = 'pyproject.toml'
	
	@classmethod
	def _read(cls):
		return toml.load(cls.path)

	@classmethod
	def _write(cls, data):
		with open(cls.path, 'w') as f:
			toml.dump(data, f)

	@staticmethod
	def normalize(version):
		return '.'.join([str(v) for v in version])

	@staticmethod
	def parse(version):
		v = [int(s) for s in re.split(r'[^0-9]', version) if s][:3]
		while len(v) < 3:
			v.append(0)
		return v

	@classmethod
	def increment(cls):
		version      = cls.get()
		version_bars = cls.parse(version)
		version_bars[2] += 1

		cls.set(cls.normalize(version_bars))

	@classmethod
	def set(cls, version):
		data = cls._read()
		data['tool']['poetry']['version'] = version
		cls._write(data)


	@classmethod
	def get(cls):
		return cls._read()['tool']['poetry']['version']



def main():
	if len(sys.argv) == 2:
		version = Version.normalize(Version.parse(sys.argv[1]))
		Version.set(version)
	else:
		Version.increment()

if __name__ == '__main__':
	main()
