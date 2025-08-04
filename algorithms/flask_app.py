from flask import Flask, request, jsonify
from flask_cors import CORS
from playerSimilarity import NBAPlayerSimilarity


app = Flask(__name__)
CORS(app)  # allows react to communicate back

# init nba simn
try:
    nba_sim = NBAPlayerSimilarity('playerstats.csv')
    #print("nba sim initialized")
except Exception as e:
    #print("error")
    nba_sim = None


@app.route('/api/feature-groups', methods=['GET']) # reading 
def get_feature_groups():
    if not nba_sim:
        return jsonify({'error': 'nba sim not initialized'}), 500 # return 500 error for hhtp stuff idk
    
    return jsonify({ # if all good list the profiles and their criteria
        'feature_groups': list(nba_sim.feature_groups.keys()),
        'profiles': {
            group: features for group, features in nba_sim.feature_groups.items()
        }
    })

@app.route('/api/similar', methods=['POST']) # sending 
def find_similar_players():
    if not nba_sim:
        return jsonify({'error': 'nba sim not initialized'}), 500

    try:
        data = request.get_json()

        # get data from jason, as easy as stealing candy from a baby
        player_name = data.get('player_name', '').strip()
        feature_group = data.get('feature_group', 'scoring').lower()
        k = data.get('k', 5)
        season = data.get('season')
        exact = data.get('exact', False)
        


        # make sure that k is positive
        if not isinstance(k, int) or k <= 0:
            return jsonify({'error': 'k must be a positive integer'}), 400 # user error 
        
        # convert string to int to pass into function
        if season and isinstance(season, str) and season.isdigit():
            season = int(season)
        

        # do the search
        similar_players = nba_sim.find_similar_players(
            player_name=player_name,
            feature_group=feature_group,
            k=k,
            season=season,
            exact=exact
        )

        # response from backend
        response_data = []
        
        # target player as first row
        target_player = {
            'player': player_name,
            'season': season if season else 'All seasons',
            'metrics': [],
            'is_target': True
        }
        
        # target playe stats 
        if similar_players:
            features = nba_sim.feature_groups[feature_group]
            # Find target player's actual stats
            mask = (nba_sim.player_info['PLAYER_NAME'] == player_name)
            if season:
                if isinstance(season, int):
                    mask &= nba_sim.player_info['SEASON'].astype(str).str.startswith(str(season))
                else:
                    mask &= (nba_sim.player_info['SEASON'] == season)
            target_info = nba_sim.player_info[mask]
            if not target_info.empty:
                target_id = target_info['player_id'].values[0]
                target_stats = nba_sim.feature_data[feature_group]['raw'][target_id]
                target_player['metrics'] = [round(target_stats[feat], 1) for feat in features]

        response_data.append(target_player)
        
        # append similar players
        for player in similar_players:
            similarity_score = round(1 / (1 + player['distance']), 3)
            features = nba_sim.feature_groups[feature_group]
            metrics = [round(player['raw_stats'][feat], 1) for feat in features]
            
            response_data.append({
                'player': player['player'],
                'season': player['season'],
                'similarity': similarity_score,
                'distance': round(player['distance'], 3),
                'metrics': metrics,
                'is_target': False
            })
        
        return jsonify({
            'success': True,
            'data': response_data,
            'metadata': {
                'feature_group': feature_group,
                'features': nba_sim.feature_groups[feature_group],
                'search_method': 'Exact KD-Tree' if exact else 'Approximate ANN',
                'total_results': len(similar_players)
            }
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        print(f"Error in find_similar_players: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/players', methods=['GET']) # auto fill
def get_players():

    if not nba_sim:
        return jsonify({'error': 'nba sim not initialized'}), 500
    
    try:
        players = nba_sim.player_info['PLAYER_NAME'].unique().tolist()
        players.sort()
        
        return jsonify({
            'players': players,
            'total': len(players)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/<player_name>', methods=['GET'])
def get_player_seasons(player_name):
    """Get available seasons for a specific player"""
    if not nba_sim:
        return jsonify({'error': 'nba sim not initialized'}), 500
    
    try:
        player_data = nba_sim.player_info[
            nba_sim.player_info['PLAYER_NAME'] == player_name
        ]
        
        if player_data.empty:
            return jsonify({'error': 'Player not found'}), 404
        
        seasons = sorted(player_data['SEASON'].unique().tolist())
        
        return jsonify({
            'player': player_name,
            'seasons': seasons,
            'total_seasons': len(seasons)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=8080)
