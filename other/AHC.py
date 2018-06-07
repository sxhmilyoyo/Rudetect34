from fuzzywuzzy import fuzz

class Node:
	"""
	@attributes:
		s: the sum of the distance
		n: the total number of node in the cluster
	"""
	def __init__(self, s=0, n=0):
		self.s = s
		self.n = n

class Cluster:
	"""
	@attributes:
		left: the cluster that has the small number
		right: the cluster that has the large number
	@function:
		the object of the cluster.
	"""
	def __init__(self):
		pass
	def __repr__(self):
		return ("%s, %s") % (self.left, self.right)
	def add(self, clusters, matrix, lefti, righti):
		"""
		@param
			clusters: list, the list of the cluster
			matrix: list, the distance matrix
			lefti: integer, the index of the cluster
			righti: integer, the index of the cluster
		@return
			clusters: list, the list of the cluster
			matrix: list, the distance matrix
		@function
			use the left and right index to merge the two cluster,
			and update the matrix
		"""
		self.left = clusters[lefti]
		self.right = clusters[righti]
		# merge matrix[row][righti] and matrix[righti] into matrix[row][lefti] and matrix[lefti]
		for r in matrix:
			r[lefti] = Node(r[lefti].s + r[righti].s, r[lefti].n + r.pop(righti).n)
		s_list = map(sum, zip([i.s for i in matrix[lefti]], [j.s for j in matrix[righti]]))
		n_list = map(sum, zip([i.n for i in matrix[lefti]], [j.n for j in matrix.pop(righti)]))
		empty = []
		for s, n in zip(s_list, n_list):
			empty.append(Node(s, n))
		matrix[lefti] = empty

		clusters.pop(righti)
		return (clusters, matrix)

class AHC():
	# def __init__(self):
	# 	self.Cluster = Cluster()
	# 	self.Node = Node()

	def get_distance_matrix(self, data):
		"""
		@param
			data: the list of the clusters
		@return
			2D list of the distance betweem each clusters
		@function
			use the coordinates to get the distances between each clusters,
			and build the distance matrix.
		"""
		row, column = len(data), len(data)
		distance_matrix = [[0 for c in range(column)] for r in range(row)]
		for r in range(row):
			print "%dth row" %r
			for c in range(column):
				distance_matrix[r][c] = Node(self.get_distance(data[r], data[c]), 1)
			# break
		return distance_matrix

	def get_distance(self, n1, n2):
		"""
		@param
			n1: list of coordinate of the cluster1
			n2: list of coordinate of the cluster2
		@return
			integer, the distance between two clusters
		@function
			use two clusters coordinates to calculate the distance between them.
		"""
		return fuzz.token_set_ratio(n1, n2)

	def agglomerate(self, labels, matrix):
		"""
		@param
			labels: list, the list of the cluster name
			matrix: list, the list of the distance 
		@return
			clusters: list, the list of the clusters
		@function
			use the while loop as the stop condition to stop merged,
			in while loop, because the matrix is symmetric, only need 
			to get the half of the matrix to get the index of smallest
			average distance between each cluster, then generate the
			cluster and update the matrix.
		"""
		clusters = labels
		i = 1
		while True:
			print "The %dth time iteration."%i
			# print (clusters)
			distances = [(1, 0, matrix[1][0])]
			for i, row in enumerate(matrix[2:]):
				distances += [(i+2, j, c) for j, c in enumerate(row[:i+2])]
			j, i, node = max(distances, key=lambda x: x[2].s / x[2].n)
			# criteria
			similarity = node.s / node.n
			if similarity < 50:
				print "cannot merge any more..."
				print "row is %d and column is %d" %(j, i)
				print "max similarity between clusters is %d" %similarity
				break
			# merge i <- j
			c = Cluster()
			clusters, matrix = c.add(clusters, matrix, i, j)
			clusters[i] = c.left + c.right
			i += 1
		return clusters

	def draw(clusters, data):
		"""
		@param
			clusters: list, the list of the clusters.
			data: list, the distance matrix.
		@return
			none.
		@function
			use the matplotlib to plot the picture of the result.
		"""
		total = []
		for c in clusters:
			temp = []
			for idx in c:
				temp.append(data[idx])
			total.append(temp)

		colors = ['red', 'blue', 'green']
		for i in range(len(total)):
			x = [j[0] for j in total[i]]
			y = [j[1] for j in total[i]]
			plt.scatter(x, y, color=colors[i])
		plt.savefig("result_average.png")

# if __name__ == "__main__":
# 	with open("point_sets.txt") as fp:
# 		content = fp.readlines()

# 	data = [row.split() for row in content]
# 	distance_matrix = get_distance_matrix(data)
	
# 	labels = [[i] for i in range(len(data))]

# 	clusters = agglomerate(labels, distance_matrix)

	# for c in clusters:
	# 	print len(c)
	
	"""	
	# write the result in the file
	lines = []
	for i in range(len(data)):
		if i in clusters[0]:
			# red
			label = "red"
		elif i in clusters[1]:
			# blue
			label = "blue"
		elif i in clusters[2]:
			# green
			label = "green"
		x, y = data[i]
		lines.append(x + "\t" + y + "\t" + label + "\n")
	with open("result_average.txt", "w") as fp:
		for line in lines:
			fp.write(line)

	# draw the plot
	draw(clusters, data)
	"""