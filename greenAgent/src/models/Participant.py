from pydantic import BaseModel
from src.models.enum.Role import Role
from src.game.AgentState import AgentState
from src.game.GameData import GameData
from src.models.Bid import Bid
from src.models.Message import Message

from typing import List

class Participant(BaseModel):
    id:str
    url:str
    role: Role
    game_data: GameData
    simulated: bool
    simulated_state: AgentState
    
    def __init__(self, id:str, url:str, role:Role, simulated:bool, game_data: GameData):
        super().__init__(
            id = id,
            role = role,
            simulated = simulated,
            game_data = game_data
        )
        
        if simulated == True:
            self.simulated_state = AgentState(game_data)
        else:
            self.url = url
            
    #Helpers
    def get_simulated_agent_state_prompt(self):
        return f"""
            You are a simulated participant in a game of werewolf. Here is your memories of the game this far
            
            Your role: {self.role}
            Who you suspect and why: {self.simulated_state.suspects}
        """
            
            
    # Prompts
    def get_vote_prompt(self, user_role:str, messages:List[Message], participants:List[Participant]):
        messages_w_ids = [f"{message.sender_id} - {message.content}" for message in messages]
        participant_ids = [p.id for p in participants]
        
        if self.simulated:
            simulated_message = self.get_simulated_agent_state_prompt()
        else:
            simulated_message = ""
        
        return f"""
                {simulated_message}
                
                It's time to vote for a player to eliminate:
                
                remember your role is: {user_role}
                
                Here is all of the conversations from this round:
                {"\n".join(messages_w_ids)}
                
                Pick a single player to eliminate and provide an explination as to why.
                Here are a list of players to chose from:
                {"\n".join(participant_ids)}
                
                Be sure to provide you response in JSON format as follows:
                {{
                    "player_id": "the player ID you want to eliminate",
                    "reason": "your explanation for why you are eliminating this player"
                }}
            """
        
    def get_werewolf_prompt(self, round_num:int, participants:List[str]):
        if self.simulated:
            simulated_message = self.get_simulated_agent_state_prompt()
        else:
            simulated_message = ""
            
        participants_list = "\n".join([f"- {p}" for p in participants])
        return f"""
            {simulated_message}
            
            ROUND {round_num}:

            YOU ARE THE WEREWOLF

            Pick one participant to eliminate. Here is a list of the participants:
            {participants_list}

            Be sure to also explain why you are choosing to eliminate this player.

            Respond with a JSON object in the following format:
            {{
                "player_id": "the player ID you want to eliminate",
                "reason": "your explanation for why you are eliminating this player"
            }}
        """

    def get_seer_reveal_prompt(self, player_id:str, is_werewolf:bool):
        if self.simulated:
            simulated_message = self.get_simulated_agent_state_prompt()
        else:
            simulated_message = ""
            
        return f"""
            {simulated_message}
            Here are the results of your investigation:

            You investigated player: {player_id}
            They {"are" if is_werewolf else "are not"} the werewolf

        """
        
    def get_bid_prompt(self, user_role:str, bids:List[Bid]) -> str:
        if self.simulated:
            simulated_message = self.get_simulated_agent_state_prompt()
        else:
            simulated_message = ""
            
        return f"""
            {simulated_message}
             
            It is time to place your bid for speaking order in the upcoming debate round.
            You are playing as a {user_role}.

            Place a bid between 0 and 100 points to determine your speaking order.

            Remember, your bid will determine when you get to speak, with higher bids allowing you to speak earlier.
            Consider your strategy carefully based on the current state of the game and the messages exchanged so far.

            Here are the current bids from all participants:
            {"\n".join([f"- Participant {bid.participant_id}: {bid.amount} points" for bid in bids])}

            Be sure to response in JSON format as follows:
            {{
                "bid_amount": <your_bid_amount>
                "reason": "your explanation for your bid"
            }}
        """