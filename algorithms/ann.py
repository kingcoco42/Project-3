import numpy as np
from collections import defaultdict


class ANNSearch:

    def __init__(self, dimensions, num_tables=10, hash_size=8):
        self.dimensions = dimensions
        self.num_tables = num_tables
        self.hash_size = hash_size
        self.hash_tables = [defaultdict(list) for _ in range(num_tables)]
        self.random_planes = []

        # gets random planes (dimensions/stats)
        for _ in range(num_tables):
            planes = [np.random.randn(dimensions) for _ in range(hash_size)]
            self.random_planes.append(planes)

    # generates binary hash key based on where players fall in the randomly generated planes
    def _hash(self, point, planes):
        return tuple(int(np.dot(point, plane) > 0) for plane in planes)

    # hashes player list
    def build_index(self, points, player_ids):
        self.points = points
        self.player_ids = player_ids

        for idx, point in enumerate(points):
            for table_idx in range(self.num_tables):
                hash_key = self._hash(point, self.random_planes[table_idx])
                self.hash_tables[table_idx][hash_key].append(idx)

    # generates list of approximate nearest neighbors
    def query(self, target, k=5):
        candidates = set()

        for table_idx in range(self.num_tables):
            hash_key = self._hash(target, self.random_planes[table_idx])
            candidates.update(self.hash_tables[table_idx].get(hash_key, []))

        candidate_distances = []
        for idx in candidates:
            dist = np.linalg.norm(target - self.points[idx])
            candidate_distances.append((dist, self.player_ids[idx], self.points[idx]))

        return sorted(candidate_distances)[:k]
