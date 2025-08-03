import pandas as pd
import numpy as np
from kdTree import KDTree
from ann import ANNSearch
from sklearn.preprocessing import StandardScaler


class NBAPlayerSimilarity:

    def __init__(self, data_path='playerstats.csv'):
        self.load_data(data_path)
        self.build_models()

    def simple_normalize(self, X):
        min_vals = np.min(X, axis=0)
        max_vals = np.max(X, axis=0)
        return (X - min_vals) / (max_vals - min_vals + 1e-8)

    def load_data(self, data_path):
        df = pd.read_csv(data_path)
        df = df.dropna().drop_duplicates(subset=['PLAYER_NAME', 'SEASON'])

        # Convert season to consistent format
        if isinstance(df['SEASON'].iloc[0], str) and '-' in df['SEASON'].iloc[0]:
            df['SEASON_YEAR'] = df['SEASON'].str.split('-').str[0].astype(int)
        else:
            df['SEASON_YEAR'] = df['SEASON'].astype(int)

        df['player_id'] = df.groupby(['PLAYER_NAME', 'SEASON']).ngroup()
        self.player_info = df[['player_id', 'PLAYER_NAME', 'SEASON', 'SEASON_YEAR']]

        self.feature_groups = {
            'scoring': ['PTS', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'TS_PCT', 'USG_PCT'],
            'style': ['FGA', 'USG_PCT', 'FG3A', 'AST_PCT', 'FTA', 'PACE', 'E_TOV_PCT'],
            'defense': ['STL', 'BLK', 'DREB', 'DEF_WS', 'DEF_RATING', 'PF'],
            'traditional': ['PTS', 'REB', 'AST', 'STL', 'BLK'],
            'impact': ['OFF_RATING', 'DEF_RATING', 'PLUS_MINUS']
        }

        self.scaler = StandardScaler()

        self.feature_data = {}
        for group, features in self.feature_groups.items():
            X = df[features].values
            self.feature_data[group] = {
                'scaled': self.simple_normalize(X),
                'raw': dict(zip(df['player_id'], df[features].to_dict('records'))),
                'features': features
            }

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

    def compare_search_methods(self, player_name, feature_group='scoring', k=5, season=None):
        import time

        start = time.time()
        knn_results = self.find_similar_players(player_name, feature_group, k, season, exact=True)
        knn_time = time.time() - start

        start = time.time()
        ann_results = self.find_similar_players(player_name, feature_group, k, season, exact=False)
        ann_time = time.time() - start

        return {
            'knn': {'results': knn_results, 'time': knn_time},
            'ann': {'results': ann_results, 'time': ann_time},
            'common_players': len(set(p['player'] for p in knn_results) &
                              set(p['player'] for p in ann_results))
        }

    def find_similar_players(self, player_name, feature_group='scoring',
                             k=5, season=None, exact=True):
        mask = (self.player_info['PLAYER_NAME'] == player_name)
        if season:
            mask &= (self.player_info['SEASON_YEAR'] == season)

        target_info = self.player_info[mask]
        if target_info.empty:
            raise ValueError(f"Player {player_name} not found{'' if not season else f' in season {season}'}")

        target_id = target_info['player_id'].values[0]
        target_name = target_info['PLAYER_NAME'].values[0]
        features = self.feature_data[feature_group]['features']
        points = self.feature_data[feature_group]['scaled']

        target_idx = np.where(self.player_info['player_id'] == target_id)[0][0]
        target_point = points[target_idx]

        # Get more candidates to ensure we can fill k unique players
        if exact:  # kd tree
            results = self.kd_trees[feature_group].find_nearest_neighbors(target_point, k * 2)  # Get extra candidates
        else:  # ANN
            results = self.ann_indices[feature_group].query(target_point, k * 2)  # Get extra candidates

        similar_players = []
        seen_names = set()

        for dist, pid, pt in results:
            player = self.player_info[self.player_info['player_id'] == pid].iloc[0]

            # Skip if same name as target or already seen this player name
            if player['PLAYER_NAME'] == target_name:
                continue

            seen_names.add(player['PLAYER_NAME'])
            similar_players.append({
                'player': player['PLAYER_NAME'],
                'season': player['SEASON'],
                'distance': dist,
                'raw_stats': self.feature_data[feature_group]['raw'][pid],
                'norm_stats': dict(zip(features, pt))
            })

            if len(similar_players) >= k:
                break

        if len(similar_players) < k:
            remaining = k - len(similar_players)
            extra_results = self.kd_trees[feature_group].find_nearest_neighbors(target_point, k + remaining) if exact \
                else self.ann_indices[feature_group].query(target_point, k + remaining)

            for dist, pid, pt in extra_results:
                if len(similar_players) >= k:
                    break

                player = self.player_info[self.player_info['player_id'] == pid].iloc[0]
                if player['PLAYER_NAME'] != target_name:
                    seen_names.add(player['PLAYER_NAME'])
                    similar_players.append({
                        'player': player['PLAYER_NAME'],
                        'season': player['SEASON'],
                        'distance': dist,
                        'raw_stats': self.feature_data[feature_group]['raw'][pid],
                        'norm_stats': dict(zip(features, pt))
                    })

        return similar_players[:k]