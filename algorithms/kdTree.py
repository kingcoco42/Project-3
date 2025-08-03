import numpy as np
import heapq


class KDNode:
    def __init__(self, point, player_id, left=None, right=None):
        self.point = point  # point in k-dimensional space
        self.player_id = player_id  # id from csv file
        self.left = left  # left node in kd tree
        self.right = right  # right node in kd tree


class KDTree:
    def __init__(self, dimensions):
        self.root = None
        self.dimensions = dimensions
        self.size = 0

    def build(self, points, player_ids):
        def build_loop(points, depth=0):  # kd tree recursively builds
            if not points:
                return None

            axis = depth % self.dimensions  # cycles through dimensions to determine axis of rotation (discriminator)

            points_sorted = sorted(points, key=lambda x: x[0][axis])
            median = len(points_sorted) // 2  # data is split along median for each dimension

            node = KDNode(  # initialize node in tree for each player
                point=points_sorted[median][0],
                player_id=points_sorted[median][1],
                left=build_loop(points_sorted[:median], depth + 1),
                right=build_loop(points_sorted[median + 1:], depth + 1)
            )
            return node

        self.root = build_loop(list(zip(points, player_ids)))  # call recursive function again
        self.size = len(points)

    def find_nearest_neighbors(self, target, k=5):
        if not self.root:
            return []

        neighbors = []

        def search(node, depth=0):
            if not node:
                return

            axis = depth % self.dimensions
            distance = np.linalg.norm(np.array(target) - np.array(node.point))

            if len(neighbors) < k:
                heapq.heappush(neighbors, (-distance, node.player_id, node.point))
            elif distance < -neighbors[0][0]:
                heapq.heappop(neighbors)
                heapq.heappush(neighbors, (-distance, node.player_id, node.point))

            if target[axis] < node.point[axis]:
                search(node.left, depth + 1)
                if (node.point[axis] - target[axis]) ** 2 < -neighbors[0][0] if neighbors else float('inf'):
                    search(node.right, depth + 1)
            else:
                search(node.right, depth + 1)
                if (target[axis] - node.point[axis]) ** 2 < -neighbors[0][0] if neighbors else float('inf'):
                    search(node.left, depth + 1)

        search(self.root)

        return sorted([(-dist, pid, pt) for dist, pid, pt in neighbors])
