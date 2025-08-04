from playerSimilarity import NBAPlayerSimilarity
import time


def main():
    print("NBA Player Similarity Finder")
    print("============================")

    nba_sim = NBAPlayerSimilarity('playerstats.csv')  # initialize class using dataset

    while True:  # menu
        print("\nOptions:")
        print("1. Find similar players (Exact KNN)")
        print("2. Find similar players (Approximate ANN)")
        print("3. Compare KNN vs ANN methods")
        print("4. List available feature groups")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == '1':
            find_similar_players(nba_sim, exact=True)
        elif choice == '2':
            find_similar_players(nba_sim, exact=False)
        elif choice == '3':
            compare_methods(nba_sim)
        elif choice == '4':
            list_feature_groups(nba_sim)
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def find_similar_players(nba_sim, exact=True):  # larger method to incorporate NBAPlayerSimilarity class into cmd line
    method = "Exact KNN" if exact else "Approximate ANN"
    print(f"\nFind Similar Players ({method})")
    print("-------------------" + "-" * len(method))

    player_name = input("Enter player name: ").strip()
    if not player_name:
        print("Player name cannot be empty!")
        return

    season = None
    season_input = input("Enter season year (e.g., 2022, optional): ").strip()  # get season as singular year
    if season_input:
        try:
            season = int(season_input)
        except ValueError:
            print("Invalid season. Must be a number (e.g., 2022).")
            return

    print("\nAvailable feature groups:")  # print comparison options
    for i, group in enumerate(nba_sim.feature_groups.keys(), 1):
        print(f"{i}. {group}")

    group_choice = input("\nSelect feature group (1-5): ").strip()  # allow choices 1-5
    try:
        group_index = int(group_choice) - 1
        feature_group = list(nba_sim.feature_groups.keys())[group_index]
    except (ValueError, IndexError):
        print("Invalid choice. Using default 'scoring'.")
        feature_group = 'scoring'

    k = input("\nNumber of similar players to find (default 5): ").strip()  # number of nearest neighbors to find
    try:
        if k:
            k = int(k)
        else:
            k = 5
    except ValueError:
        print("Invalid number. Using default 5.")
        k = 5

    start_time = time.time()  # timer
    try:
        similar_players = nba_sim.find_similar_players(
            player_name=player_name,
            feature_group=feature_group,
            k=k,
            season=season,
            exact=exact
        )
        search_time = time.time() - start_time

        # Get target player's stats for reference
        player_and_season = (nba_sim.player_info['PLAYER_NAME'] == player_name)
        if season:
            player_and_season &= (nba_sim.player_info['SEASON_YEAR'] == season)
        target_info = nba_sim.player_info[player_and_season]

        target_id = target_info['player_id'].values[0]
        target_raw = nba_sim.feature_data[feature_group]['raw'][target_id]
        target_norm = nba_sim.feature_data[feature_group]['scaled'][target_id]

        print("\n=== Target Player Stats ===")  # user inputted player displayed first
        print(f"{player_name} ({season if season else 'all seasons'}):")
        for stat in target_raw:
            print(f"   - {stat}: {target_raw[stat]:.2f} ({target_norm[list(target_raw.keys()).index(stat)]:.2f})")

        print(f"\nPlayers similar to {player_name}", end="")
        if season:
            print(f" in {season}", end="")
        print(f" ({feature_group} profile) using {method} ({search_time:.4f}s):\n")  # display method, time

        for i, player in enumerate(similar_players, 1):  # print out nearest neighbors' stats as Raw (normalized)
            print(f"{i}. {player['player']} ({player['season']}) - Similarity: {1 / (1 + player['distance']):.2f}")
            print("   Raw Stats (Normalized Stats):")
            for stat in player['raw_stats']:
                raw_val = player['raw_stats'][stat]
                norm_val = player['norm_stats'].get(stat, 'N/A')
                print(f"   - {stat}: {raw_val:.2f} ({norm_val:.2f})")
            print()

    except ValueError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


def compare_methods(nba_sim):  # contrast KD tree and ANN timing
    print("\nCompare KNN vs ANN Performance")
    print("----------------------------")

    player_name = input("Enter player name: ").strip()
    if not player_name:
        print("Player name cannot be empty!")
        return

    season = None
    season_input = input("Enter season year (e.g., 2022, optional): ").strip()
    if season_input:
        try:
            season = int(season_input)
        except ValueError:
            print("Invalid season. Must be a number (e.g., 2022).")
            return

    # print similarity feature groups -> scoring, defense, etc.
    print("\nAvailable feature groups:")
    for i, group in enumerate(nba_sim.feature_groups.keys(), 1):
        print(f"{i}. {group}")

    group_choice = input("\nSelect feature group (1-5): ").strip()
    try:
        group_index = int(group_choice) - 1
        feature_group = list(nba_sim.feature_groups.keys())[group_index]
    except (ValueError, IndexError):  # default to traditional comparison
        print("Invalid choice. Using default 'traditional'.")
        feature_group = 'traditional'

    k = input("\nNumber of similar players to find (default 5): ").strip()
    try:
        if k:
            k = int(k)
        else:
            k = 5
    except ValueError:
        print("Invalid number. Using default 5.")
        k = 5

    # Get target player's stats for reference
    player_and_season = (nba_sim.player_info['PLAYER_NAME'] == player_name)
    if season:
        player_and_season &= (nba_sim.player_info['SEASON_YEAR'] == season)
    target_info = nba_sim.player_info[player_and_season]

    if target_info.empty:
        print(f"Player {player_name} not found{'' if not season else f' in season {season}'}")
        return

    target_id = target_info['player_id'].values[0]
    target_raw = nba_sim.feature_data[feature_group]['raw'][target_id]
    target_norm = nba_sim.feature_data[feature_group]['scaled'][target_id]

    print("\n=== Target Player Stats ===")  # user inputted player displayed first
    print(f"{player_name} ({season if season else 'all seasons'}):")
    # round stats to two decimal places, output as Raw (Normalized)
    for stat in target_raw:
        print(f"   - {stat}: {target_raw[stat]:.2f} ({target_norm[list(target_raw.keys()).index(stat)]:.2f})")

    # Run both methods
    comparison = {
        'knn': {'time': 0, 'results': []},
        'ann': {'time': 0, 'results': []}
    }

    # time both methods
    for method in ['knn', 'ann']:
        start = time.time()
        results = nba_sim.find_similar_players(
            player_name=player_name,
            feature_group=feature_group,
            k=k,
            season=season,
            exact=(method == 'knn')
        )
        comparison[method]['time'] = time.time() - start
        comparison[method]['results'] = results

    # Create sets of (player_name, season) pairs
    knn_players = set((p['player'], p['season']) for p in comparison['knn']['results'])
    ann_players = set((p['player'], p['season']) for p in comparison['ann']['results'])
    common_players = len(knn_players & ann_players)

    # print out results for both KNN and ANN
    print("\n=== Results Comparison ===")
    for method in ['knn', 'ann']:
        print(f"\n{'Exact KNN' if method == 'knn' else 'Approximate ANN'} - {comparison[method]['time']:.4f}s")
        for i, player in enumerate(comparison[method]['results'], 1):
            print(f"{i}. {player['player']} ({player['season']}) - Similarity: {1 / (1 + player['distance']):.2f}")
            print("   Raw Stats (Normalized Stats):")
            for stat in player['raw_stats']:
                raw_stats = player['raw_stats'][stat]
                normalized_stats = player['norm_stats'].get(stat, 'N/A')
                print(f"   - {stat}: {raw_stats:.2f} ({normalized_stats:.2f})")

    # contrast KNN and ANN using speed and exactness (how close was ANN to exact KNN)
    print(f"\n=== Comparison Metrics ===")
    print(f"Common players in top {k}: {common_players}/{k}")  # how many matches did ANN get to exact KNN
    print(f"Speed ratio: {comparison['knn']['time'] / comparison['ann']['time']:.2f}x faster")  # percentage ANN faster
    print(f"ANN found {100 * common_players / k:.2f}% of KNN results")  # percentage of exact KNN found by ANN


def list_feature_groups(nba_sim):  # similarity metric groups
    print("\nAvailable feature groups and their metrics:")
    for group, features in nba_sim.feature_groups.items():
        print(f"\n{group.capitalize()}:")
        for feature in features:
            print(f"  - {feature}")


if __name__ == '__main__':
    main()
