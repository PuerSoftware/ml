import os
import csv

__all__ = ['DataFrameRow', 'DataFrame']


class DataFrameRow(list):
	def __init__(self, *args, **kwargs):
		self.df = kwargs['df']
		super().__init__(*args)

	def set(self, col, value):
		col_idx = self.df.cols.get(col, None)
		if col_idx is not None:
			self[col_idx] = value

	def get(self, col):
		col_idx = self.df.cols.get(col, None)
		return self[col_idx] if col_idx is not None else ''

	def has(self, col):
		col_idx = self.df.cols.get(col, None)
		if col_idx:
			return len(self) > col_idx
		return False

	def remove(self, col):
		del self[self.df.cols[col]]

	def to_dict(self):
		return {self.df.header[n]:self[n] for n in range(len(self))}

	def copy(self, df):
		return DataFrameRow([*self], df=df)

class DataFrame:
	_id = 1
	
	######################################################

	@staticmethod
	def open(file_path, delimiter=None, encoding='utf-8'):
		df = DataFrame()
		df.append_file(file_path, delimiter, encoding)
		return df
		

	######################################################
			
	def __init__(self, header=None, rows=None):
		self.id      = DataFrame._id
		self.rows    = []
		self.header  = None
		self.cols    = None
		self.indices = {}  # {col_name: {col_value.lower(): set(rowids)}}
		self.n       = 0

		if header:
			self.set_header(header)

		if rows:
			for row in rows:
				self.append(row)

		DataFrame._id += 1

	def __getitem__(self, key):  # [2:]
		return DataFrame(self.header, self.rows[key])

	def __len__(self):
		return len(self.rows)

	def __iter__(self):
		self.n = 0
		return self

	def __next__(self):
		if self.n < len(self):
			row = self.rows[self.n]
			self.n += 1
			return row
		else:
			raise StopIteration
	def _error(self, s):
		print('Error:', s)

	# def create_index(self, col):
	# 	if self.headers.get(col):
	# 		self.indices[col] = {}
	# 		for n in range(len(self.rows)):
	# 			self.index_row(col, n)
	# 	else:
	# 		self._error(f'Column "{col}" does not exist')

	# def delete_index(self, col):
	# 	if self.headers.get(col):
	# 		if self.indices.get(col):
	# 			del self.indices[col]
	# 		else:
	# 			self._error(f'Index "{col}" does not exist')
	# 	else:
	# 		self._error(f'Column "{col}" does not exist')

	# def index_row(self, col, row_n):
	# 	col_n   = self.cols[col]
	# 	row     = self.rows[row_n]
	# 	value   = row[col_n]
	# 	if not idx_set := self.indices[col].get(value)
	# 		idx_set = set()
	# 		self.indices[col][str(value).lower()] = idx_set
	# 	idx_set.add(row_n)

	# def has_index(self, col):
	# 	return bool(self.indices.get(col))

	# def get_by_value(col, value):
	# 	if self.has_index(col):
	# 		if 

	def get_index(self, col):
		return {
			row.get(col): row
			for row in self
		}

	def _update_header_positions(self):
		self.cols = { self.header[n]: n for n in range(len(self.header)) }

	def _join_headers(self, df):
		header = self.header.copy()
		for h in df.header:
			if h in header:
				header.append('_' + h)
			else:
				header.append(h)
		return header

	def set_header(self, header):
		self.header = header.copy()
		self._update_header_positions()
		return self

	def append(self, row):
		if not isinstance(row, DataFrameRow):
			row = DataFrameRow(row, df=self)
		row.df = self
		self.rows.append(row)
		return self

	def alter(self, cols, copy=False):
		df = DataFrame(cols)
		for row in self.rows:
			new_row = []
			for col in cols:
				new_row.append(row.get(col))
			df.append(new_row)
		if not copy:
			self.set_header(cols)
			self.rows = df.rows
			df = self
		return df

	def add_col(self, col, value='', after=None):
		position = len(self.header)
		if after in self.cols:
			position = self.cols[after] + 1
		self.header.insert(position, col)
		# Update columns positions
		self._update_header_positions()
		for row in self.rows:
			if callable(value):
				row.insert(position, value(row))
			else:
				row.insert(position, value)
		return self

	def add_cols(self, cols, after=None):
		for col in cols:
			self.add_col(col, after=after)
		return self

	def remove_col(self, col):
		col_idx = self.cols[col]
		del self.header[col_idx]
		for row in self.rows:
			del row[col_idx]
		self._update_header_positions()
		return self

	def remove_cols(self, cols):
		for col in cols:
			self.remove_col(col)
		return self

	def set(self, col, n, value):
		self.rows[n].set(col, value)
		return self

	def get(self, col, n):
		return self.rows[n].get(col)

	def map(self, f):  # f(row, n, df)
		for n in range(len(self.rows)):
			f(self.rows[n])
		return self

	def map_col(self, col, f):
		for n in range(len(self.rows)):
			self.rows[n].set(col, f(self.rows[n].get(col)))
		return self

	def map_cols(self, cols, f):
		for n in range(len(self.rows)):
			for col in cols:
				self.rows[n].set(col, f(self.rows[n].get(col)))
		return self

	def cast(self, col, _type=str):
		for row in self:
			row.set(col, _type(row.get(col)))
		return self

	def filter(self, f):
		df = DataFrame(self.header)
		for n in range(len(self.rows)):
			if f(self.rows[n], n):
				df.append(self.rows[n])
		return df

	def sort(self, f, cutoff=None):
		if cutoff is not None:
			items = sorted([(item, f(item)) for item in self.rows], key=lambda x: x[1])
			self.rows = [item for item, value in items if value > cutoff]
		else:
			self.rows.sort(key=f)

	def sort_by(self, col, asc=True):
		self.rows.sort(key=lambda row: row[self.cols[col]], reverse=not asc)

	def find(self, col, value):
		n = 0
		for row in self:
			if row.get(col) == value:
				return row, n
			n += 1
		return None, None

	def match(self, df, f):  # f(lrow, rrow) -> Falsey | new row
		for l in range(len(self.rows)):
			for r in range(len(df.rows)):
				f(self.rows[l], df.rows[r])
		return self

	def ljoin(self, df, f1, f2):
		header = self.header.copy() + [
			h if h not in self.header else f'_{h}' for h in df.header 
		]
		result_df = DataFrame(header)

		self.add_col('__join__1', f1)
		df.add_col('__join__2', f2)
		
		for row in self:
			value1    = row.get('__join__1')
			row2, _   = df.find('__join__2', value1)
			if row2 is not None:
				result_df.append(row[:-1] + row2[:-1])
			else:
				result_df.append(row[:-1] + [''] * (len(df.header) -1))

		self.remove_col('__join__1')
		df.remove_col('__join__2')
		return result_df

	def match_copy(self, df, header, f):  # f(lrow, rrow) -> Falsey | new row
		df1 = DataFrame(header)
		for l in self:
			for r in df:
				row = f(l, r)
				if row is not None:
					df1.append(row)
		return df1

	def transform(self, header, f):
		df = DataFrame(header)
		for row in self.rows:
			df.append(f(row))
		return df

	def append_file(self, file_path, delimiter=None, encoding='utf-8'):
		file_name, file_ext = os.path.splitext(file_path)
		if delimiter is None:
			delimiter = {'.tsv':'\t', '.csv':','}.get(file_ext.lower())

		with open(file_path, 'r', encoding=encoding) as f:
			reader = csv.reader(f, delimiter=delimiter)
			header = next(reader)
			if not self.header:
				self.set_header(header)
			for row in reader:
				self.append(row)
		return self

	def copy(self):
		df = DataFrame(self.header)
		for n in range(len(self.rows)):
			df.append(self.rows[n].copy(df))
		return df

	def save(self, file_path, delimiter=None, encoding='utf-8'):
		file_name, file_ext = os.path.splitext(file_path)
		if delimiter is None:
			delimiter = {'.tsv':'\t', '.csv':','}.get(file_ext.lower())

		with open(file_path, 'w', encoding=encoding, newline='') as f:
			writer = csv.writer(f, delimiter=delimiter)
			writer.writerow(self.header)
			writer.writerows(self.rows)
		return self

	def to_list(self, col, _type=str):
		return [_type(self.rows[n].get(col)) for n in range(len(self.rows))]

	def to_unique_list(self, col):
		values = set()
		for row in self:
			values.add(row.get(col))
		return list(values)

	def to_lists(self, cols):
		lists = []
		for col in cols:
			lists.append(self.to_list(col))
		return lists

	def print(self, max_rows=10):
		margin    = 3
		min_width = 12
		lens   = [(len(h) if len(h) > min_width else min_width) + margin for h in self.header]
		header = ''.join([self.header[n].ljust(lens[n]) for n in range(len(lens))])
		print(header)
		print('-' * len(header))
		count = 0
		for row in self.rows:
			if count < max_rows:
				s = ''.join([str(row[n])[:lens[n]-1].ljust(lens[n]) for n in range(len(lens))])
				print(s)
			else:
				break
			count += 1
		return self


	######################################################






