import math
import os
import pickle

import numpy as np
import torch
import torch.nn.functional as F
from torch.distributions import Categorical

from lookup_act import LookupAction
import advanced_padder
from discrete_policy import DiscreteFF

# You can get the OBS size from the rlgym-ppo console print-outs when you start your bot
OBS_SIZE = 237

# If you haven't set these, they are [256, 256, 256] by default
POLICY_LAYER_SIZES = [768, 512, 256]

class Agent:
	def __init__(self):
		self.action_parser = LookupAction()
		self.num_actions = len(self.action_parser._lookup_table)
		cur_dir = os.path.dirname(os.path.realpath(__file__))
		
		device = torch.device("cpu")
		self.policy = DiscreteFF(OBS_SIZE, self.num_actions, POLICY_LAYER_SIZES, device)
		self.policy.load_state_dict(torch.load(os.path.join(cur_dir, "PPO_POLICY.pt"), map_location=device))
		torch.set_num_threads(1)

	def act(self, state):
		with torch.no_grad():
			action_idx, probs = self.policy.get_action(state, True)
		
		action = np.array(self.action_parser.parse_actions([action_idx], None))
		if len(action.shape) == 2:
			if action.shape[0] == 1:
				action = action[0]
		
		if len(action.shape) != 1:
			raise Exception("Invalid action:", action)
		
		return action