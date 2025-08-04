import pandas as pd
import numpy as np
from kdTree import KDTree
from ann import ANNSearch
import time


class NBAPlayerSimilarity:

    def __init__(self, data_path='playerstats.csv'):
        self.load_data(data_path)
        self.build_models()

    # all stats normalized to 0-1 range (so all stats considered equally)
    # points will naturally have > value, range than steals so this balances it
    def normalize(self, x):
        min_values = np.min(x, axis=0)
        max_values = np.max(x, axis=0)
        return (x - min_values) / (max_values - min_values + 1e-8)  # 1e-8 prevents division by zero

    def load_data(self, data_path):  # read data from csv file and define comparison groups
        # create dataframe, minor cleaning
        df = pd.read_csv(data_path)
        df = df.dropna().drop_duplicates(subset=['PLAYER_NAME', 'SEASON'])

        # allow season to be searched using only one year (2022 instead of 2021-22)
        if isinstance(df['SEASON'].iloc[0], str) and '-' in df['SEASON'].iloc[0]:
            df['SEASON_YEAR'] = df['SEASON'].str.split('-').str[0].astype(int)
        else:
            df['SEASON_YEAR'] = df['SEASON'].astype(int)

        # organize players into dataframe, differentiating individual seasons
        df['player_id'] = df.groupby(['PLAYER_NAME', 'SEASON']).ngroup()
        self.player_info = df[['player_id', 'PLAYER_NAME', 'SEASON', 'SEASON_YEAR']]

        self.feature_groups = {  # type of similarities to find
            'scoring': ['PTS', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'TS_PCT', 'USG_PCT'],  # scoring/shooting/offensive focus
            'style': ['FGA', 'USG_PCT', 'FG3A', 'AST_PCT', 'FTA', 'PACE', 'E_TOV_PCT'],  # passing vs shooting, speed
            'defense': ['STL', 'BLK', 'DREB', 'DEF_WS', 'DEF_RATING', 'PF'],  # defensive stats and impact
            'traditional': ['PTS', 'REB', 'AST', 'STL', 'BLK'],  # 5 main statistical categories
            'impact': ['OFF_RATING', 'DEF_RATING', 'PLUS_MINUS']  # how well team plays with player on vs off
        }

        self.feature_data = {}
        for group, features in self.feature_groups.items():  # normalized stats (for calculations) and raw (for display)
            X = df[features].values
            self.feature_data[group] = {
                'scaled': self.normalize(X),
                'raw': dict(zip(df['player_id'], df[features].to_dict('records'))),
                'features': features
            }

    def build_models(self):  # assemble both a kd tree and approximate nearest neighbors list
        self.kd_trees = {}
        self.ann_indices = {}

        for group, data in self.feature_data.items():
            points = data['scaled']  # use normalized points for distance calculations
            player_ids = self.player_info['player_id'].values
            self.kd_trees[group] = KDTree(points.shape[1])
            self.kd_trees[group].build(points, player_ids)
            self.ann_indices[group] = ANNSearch(points.shape[1])
            self.ann_indices[group].build_index(points, player_ids)

    def compare_search_methods(self, player_name, feature_group='scoring', k=5, season=None):  # compare KNN, ANN
        # time both methods
        start_knn = time.time()
        knn_results = self.find_similar_players(player_name, feature_group, k, season, exact=True)
        knn_time = time.time() - start_knn
        start_ann = time.time()
        ann_results = self.find_similar_players(player_name, feature_group, k, season, exact=False)
        ann_time = time.time() - start_ann

        return {  # compile times and similar players between KNN, ANN
            'knn': {'results': knn_results, 'time': knn_time},
            'ann': {'results': ann_results, 'time': ann_time},
            'common_players': len(set(p['player'] for p in knn_results) & set(p['player'] for p in ann_results))
        }

    def find_similar_players(self, player_name, feature_group='scoring',
                             k=5, season=None, exact=True):  # allow KNN or ANN search
        player_and_season = (self.player_info['PLAYER_NAME'] == player_name)
        if season:
            player_and_season &= (self.player_info['SEASON_YEAR'] == season)

        target_info = self.player_info[player_and_season]
        if target_info.empty:  # player not in NBA or in given season
            raise ValueError(f"Player {player_name} not found{'' if not season else f' in season {season}'}")

        # get info for inputted player
        target_id = target_info['player_id'].values[0]
        target_name = target_info['PLAYER_NAME'].values[0]
        features = self.feature_data[feature_group]['features']
        points = self.feature_data[feature_group]['scaled']
        target_index = np.where(self.player_info['player_id'] == target_id)[0][0]
        target_point = points[target_index]

        if exact:  # kd tree
            results = self.kd_trees[feature_group].find_nearest_neighbors(target_point, k * 2)
            # k*2 -> go through extra players in case of target player repeating often
            # players will usually be similar to themselves so the true k-nearest will usually include the target
        else:  # ANN
            results = self.ann_indices[feature_group].query(target_point, k * 2)  # same buffer for ANN

        similar_players = []
        for distance, player_id, target_point in results:
            current_player = self.player_info[self.player_info['player_id'] == player_id].iloc[0]
            # Skip if target player comes up (i.e. don't add the player as a nearest neighbor of himself)
            if current_player['PLAYER_NAME'] == target_name:
                continue

            similar_players.append({
                'player': current_player['PLAYER_NAME'],
                'season': current_player['SEASON'],
                'distance': distance,
                'raw_stats': self.feature_data[feature_group]['raw'][player_id],
                'norm_stats': dict(zip(features, target_point))
            })

            if len(similar_players) >= k:
                break

        # ensure that k nearest neighbors are actually outputted in the event that original loop yields < k neighbors
        if len(similar_players) < k:
            remaining = k - len(similar_players)
            # go only as many times as we are missing players to fill knn
            extra_results = self.kd_trees[feature_group].find_nearest_neighbors(target_point, k + remaining) if exact \
                else self.ann_indices[feature_group].query(target_point, k + remaining)

            for distance, player_id, target_point in extra_results:
                if len(similar_players) >= k:
                    break
                current_player = self.player_info[self.player_info['player_id'] == player_id].iloc[0]
                if current_player['PLAYER_NAME'] != target_name:
                    similar_players.append({
                        'player': current_player['PLAYER_NAME'],
                        'season': current_player['SEASON'],
                        'distance': distance,
                        'raw_stats': self.feature_data[feature_group]['raw'][player_id],
                        'norm_stats': dict(zip(features, target_point))
                    })

        # in the event that > k players are compiled, only return the top k
        return similar_players[:k]
