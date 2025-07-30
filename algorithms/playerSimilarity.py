import pandas as pd
import numpy as np
from kdTree import KDTree
from ann import ANNSearch
from sklearn.preprocessing import StandardScaler


class NBAPlayerSimilarity:

    def __init__(self, data_path='playerstats.csv'):
        self.load_data(data_path)
        self.build_models()

    # transforms values into a 0-1 range from minimum to maximum so that all stats can be compared equally
    def simple_normalize(self, X):
        min_vals = np.min(X, axis=0)
        max_vals = np.max(X, axis=0)
        return (X - min_vals) / (max_vals - min_vals + 1e-8)

    def load_data(self, data_path):
        df = pd.read_csv(data_path)
        df = df.dropna().drop_duplicates(subset=['PLAYER_NAME', 'SEASON'])
        df['player_id'] = df.groupby(['PLAYER_NAME', 'SEASON']).ngroup()

        # choice of how to analyze players (MODIFY LATER)
        self.feature_groups = {
            'scoring': ['PTS', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'TS_PCT', 'USG_PCT'],
            'defense': ['STL', 'BLK', 'DREB', 'DEF_WS', 'DEF_RATING'],
            'traditional': ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV']
        }

        self.player_info = df[['player_id', 'PLAYER_NAME', 'SEASON']]
        self.scaler = StandardScaler()  # z-score (stat - mean / standard deviation)

        self.feature_data = {}
        for group, features in self.feature_groups.items():
            X = df[features].values
            self.feature_data[group] = {
                'scaled': self.simple_normalize(X),
                'raw': dict(zip(df['player_id'], df[features].to_dict('records'))),
                'features': features
            }

    # kd tree and ANN for all players to be analyzed
    def build_models(self):
        self.kd_trees = {}
        self.ann_indices = {}

        for group, data in self.feature_data.items():
            points = data['scaled']
            player_ids = self.player_info['player_id'].values

            self.kd_trees[group] = KDTree(points.shape[1])
            self.kd_trees[group].build(points, player_ids)

            self.ann_indices[group] = ANNSearch(points.shape[1])
            self.ann_indices[group].build_index(points, player_ids)

    def find_similar_players(self, player_name, feature_group='scoring',
                             k=5, season=None, exact=True):  # exact = kd tree, !exact = ANN
        mask = (self.player_info['PLAYER_NAME'] == player_name)
        if season:
            mask &= (self.player_info['SEASON'] == season)  # name and season

        target_info = self.player_info[mask]
        if target_info.empty:
            raise ValueError(f"Player {player_name} not found")

        target_id = target_info['player_id'].values[0]
        features = self.feature_data[feature_group]['features']
        points = self.feature_data[feature_group]['scaled']

        target_idx = np.where(self.player_info['player_id'] == target_id)[0][0]
        target_point = points[target_idx]

        if exact:  # kd tree
            results = self.kd_trees[feature_group].find_nearest_neighbors(target_point, k + 1)
            results = results[1:]
        else:  # ANN
            results = self.ann_indices[feature_group].query(target_point, k + 1)
            results = results[1:]

        similar_players = []
        for dist, pid, pt in results:
            player = self.player_info[self.player_info['player_id'] == pid].iloc[0]
            similar_players.append({
                'player': player['PLAYER_NAME'],
                'season': player['SEASON'],
                'distance': dist,
                'raw_stats': self.feature_data[feature_group]['raw'][pid],
                'norm_stats': dict(zip(features, pt))
            })

        return similar_players
