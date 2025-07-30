from playerSimilarity import NBAPlayerSimilarity


def main():
    print("NBA Player Similarity Finder")
    print("============================")

    nba_sim = NBAPlayerSimilarity('playerstats.csv')

    while True:
        print("\nOptions:")
        print("1. Find similar players")
        print("2. List available feature groups")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == '1':
            find_similar_players(nba_sim)
        elif choice == '2':
            list_feature_groups(nba_sim)
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def find_similar_players(nba_sim):
    print("\nFind Similar Players")
    print("-------------------")

    player_name = input("Enter player name: ").strip()
    if not player_name:
        print("Player name cannot be empty!")
        return

    year = None
    year_input = input("Enter year (optional, press Enter to skip): ").strip()
    if year_input:
        try:
            year = int(year_input)
        except ValueError:
            print("Invalid year. Must be a number.")
            return

    print("\nAvailable feature groups:")
    for i, group in enumerate(nba_sim.feature_groups.keys(), 1):
        print(f"{i}. {group}")

    group_choice = input("\nSelect feature group (1-4): ").strip()
    try:
        group_idx = int(group_choice) - 1
        feature_group = list(nba_sim.feature_groups.keys())[group_idx]
    except (ValueError, IndexError):
        print("Invalid choice. Using default 'scoring'.")
        feature_group = 'scoring'

    k = input("\nNumber of similar players to find (default 5): ").strip()
    try:
        k = int(k) if k else 5
    except ValueError:
        print("Invalid number. Using default 5.")
        k = 5

    search_method = input("\nUse exact search? (y/n, default n): ").strip().lower()
    exact = search_method == 'y'

    try:
        similar_players = nba_sim.find_similar_players(
            player_name=player_name,
            feature_group=feature_group,
            k=k,
            season=year,
            exact=exact
        )

        print(f"\nPlayers similar to {player_name}", end="")
        if year:
            print(f" in {year}", end="")
        print(f" ({feature_group} profile):\n")

        for i, player in enumerate(similar_players, 1):
            print(f"{i}. {player['player']} ({player['season']}) - Similarity: {1 / (1 + player['distance']):.2f}")
            for stat, value in player['raw_stats'].items():
                print(f"   {stat}: {value:.2f}")
            print()

        print(f"Search method: {'Exact KD-Tree' if exact else 'Approximate ANN'}")

    except ValueError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


def list_feature_groups(nba_sim):
    print("\nAvailable feature groups and their metrics:")
    for group, features in nba_sim.feature_groups.items():
        print(f"\n{group.capitalize()}:")
        for feature in features:
            print(f"  - {feature}")


if __name__ == '__main__':
    main()