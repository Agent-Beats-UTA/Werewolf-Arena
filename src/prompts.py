def get_game_rules_prompt(self):
    return """
        This is the game of werewolf. The main objective is for villagers to detect the werewolves and for the werewolves to avoid detection
        through deception and persuasion.

        ROLES:
        - Werewolves (2): Work together to eliminate villagers. One werewolf is the primary killer who chooses the night target.
          If the primary werewolf is eliminated, the secondary werewolf becomes the primary.
        - Seer (1): Can investigate one player each night to learn if they are a werewolf.
        - Doctor (1): Can protect one player each night from being eliminated by the werewolves (cannot protect themselves).
        - Villagers (3): Must identify and vote out the werewolves through discussion and deduction.

        GAME RULES:
        Each round starts with a NIGHT phase:
        1. The doctor chooses one player to protect from elimination.
        2. The werewolves secretly choose one player to eliminate.
        3. The seer investigates one player to learn if they are a werewolf.

        Next, the game enters the DAY phase:
        1. Bidding: Each participant bids for speaking order in the discussion.
        2. Discussion: Players speak in order of highest bid, sharing suspicions and defending themselves.
        3. Voting: Each participant votes for one person to eliminate. The player with the most votes is removed.

        WIN CONDITIONS:
        - Villagers win if both werewolves are eliminated.
        - Werewolves win if they equal or outnumber the remaining villagers.

        If no winning condition is met after voting, the next round begins at the NIGHT phase.

    """