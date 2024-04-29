import re
import numpy as np
import sympy as sp

from gensim.models         import KeyedVectors
from gensim.downloader     import load
from sklearn.decomposition import PCA
from sklearn.preprocessing import normalize
from numpy.linalg          import norm


class Embeddings:
	def __init__(self, model=None):
		self.model = model
		
	@staticmethod
	def load(path):
		return Embeddings(load(path))

	def query(self, expression, topn=4, probs=False):
		expr = sp.sympify(expression)
		
		# Recursive function to evaluate the expression
		def eval_expr(e):
			if isinstance(e, sp.Symbol):
				# Base case: return the corresponding vector from the embeddings
				return self.model[str(e)]
			elif isinstance(e, sp.Number):
				# Handle numeric literals directly
				return float(e)
			elif isinstance(e, sp.Add):
				# Recursive case for addition
				return sum(eval_expr(arg) for arg in e.args)
			elif isinstance(e, sp.Mul):
				# Recursive case for multiplication
				result = eval_expr(e.args[0])
				for arg in e.args[1:]:
					result = result * eval_expr(arg)
				return result
			elif isinstance(e, sp.Sub):
				# Recursive case for subtraction
				result = eval_expr(e.args[0])
				for arg in e.args[1:]:
					result = result - eval_expr(arg)
				return result
			elif isinstance(e, sp.Div):
				# Recursive case for division
				result = eval_expr(e.args[0])
				for arg in e.args[1:]:
					result = result / eval_expr(arg)
				return result
			else:
				raise ValueError('Unsupported operation')

		# Evaluate the expression
		try:
			result_vector = eval_expr(expr)
			result = self.model.most_similar(positive=[result_vector], topn=topn)
			if not probs:
				result = [r[0] for r in result]
			return result
		except Exception as e:
			print('Error:', str(e))

		return []

	def to_primary(self):
		if self.model is None: raise ValueError('Model not loaded')

		vv = self.model.vectors
		pca = PCA(n_components=vv.shape[1])  # Same amount of components as dimensions
		pca.fit(vv)
		tvv = np.dot(vv, pca.components_.T)  # rotate to fit PC

		emb       = Embeddings()
		emb.model = KeyedVectors(vector_size=tvv.shape[1])
		emb.model.add_vectors(list(self.model.key_to_index.keys()), tvv)

		return emb 

	def filter(self, filter_func, batch_size=1000):
		if self.model is None: raise ValueError('Model not loaded')
		
		emb       = Embeddings()
		emb.model = KeyedVectors(vector_size=self.model.vector_size)
		
		vv = []
		ww = []

		for w in self.model.key_to_index.keys():
			v = self.model[w]
			if filter_func(w, v):
				ww.append(w)
				vv.append(v)

				if len(ww) == batch_size:
					emb.model.add_vectors(ww, np.array(vv))
					ww, vv = [], []

		if len(ww):
			emb.model.add_vectors(ww, np.array(vv))

		return emb

	def rotate_to(self, a, b):
		a_vector = self.model[a]
		b_vector = self.model[b]
		axis     = a_vector - b_vector

		# Normalize the axis
		normalized_axis    = normalize(axis.reshape(1, -1))[0]
		rotation_matrix    = np.eye(self.model.vector_size)
		rotation_matrix[0] = normalized_axis
		rotated_vectors    = self.model.vectors.dot(rotation_matrix.T)

		# Create a new Embeddings object and populate it
		emb       = Embeddings()
		emb.model = KeyedVectors(vector_size=self.model.vector_size)
		emb.model.add_vectors(list(self.model.key_to_index.keys()), rotated_vectors)

		return emb

	def align_axes(self, word_pairs):
		""" Align multiple dimensions based on provided word pairs. """
		vector_size = self.model.vector_size
		basis = np.eye(vector_size)  # Start with an identity matrix as basis
		
		# Process each pair and adjust the basis
		for i, (positive, negative) in enumerate(word_pairs):
			if positive in self.model and negative in self.model:
				# Calculate and normalize the difference vector
				diff_vector = self.model[positive] - self.model[negative]
				diff_vector /= norm(diff_vector)
				
				# Orthogonalize against all previous vectors
				for j in range(i):
					diff_vector -= diff_vector.dot(basis[j]) * basis[j]
				diff_vector /= norm(diff_vector)
				
				# Set this vector as the ith basis vector
				basis[i] = diff_vector
			else:
				raise ValueError(f"One or both words in pair {positive}-{negative} are not in the vocabulary.")
		
		# Rotate all embeddings using the new basis
		rotated_vectors = self.model.vectors.dot(basis.T)
		
		# Create a new Embeddings object and populate it
		emb = Embeddings()
		emb.model = KeyedVectors(vector_size=vector_size)
		emb.model.add_vectors(list(self.model.key_to_index.keys()), rotated_vectors)
		
		return emb

	def display_extremes(self, dimension, n_words=10):
		# Sort words according to the dimension (either positive or negative direction)
		sorted_indices = np.argsort(self.model.vectors[:, dimension])

		print('='*10, f'Dimension {dimension+1}', '='*10)
		positive = []
		for idx in sorted_indices[-n_words:][::-1]:
			positive.append(self.model.index_to_key[idx])
		negative = []
		for idx in sorted_indices[:n_words]:
			negative.append(self.model.index_to_key[idx])

		for pair in zip(positive, negative):
			print(pair[0].ljust(14), pair[1])
        
