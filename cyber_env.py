import random
from typing import Dict, Any, Tuple

from api.models import Observation

class CyberEnvironment:
    def __init__(self):
        self.task_id = "easy"
        self.network_health = 100.0
        self.step_count = 0
        self.max_steps = 10
        self.current_attack = "none"
        self.history = []

    def reset(self, task_id: str, seed: int = None) -> Observation:
        self.task_id = task_id
        if seed is not None:
            random.seed(seed)
        self.network_health = 100.0
        self.step_count = 0
        self.history = []
        return self._generate_next_state()

    def _generate_next_state(self) -> Observation:
        # Determine next attack based on task_id
        roll = random.random()
        if self.task_id == "easy":
            # 50% ddos, 50% none
            self.current_attack = "ddos" if roll < 0.5 else "none"
        elif self.task_id == "medium":
            # 30% ddos, 30% malware, 40% none
            if roll < 0.3:
                self.current_attack = "ddos"
            elif roll < 0.6:
                self.current_attack = "malware"
            else:
                self.current_attack = "none"
        elif self.task_id == "hard":
            # 30% ddos, 30% malware, 30% zero_day, 10% none
            if roll < 0.3:
                self.current_attack = "ddos"
            elif roll < 0.6:
                self.current_attack = "malware"
            elif roll < 0.9:
                self.current_attack = "zero_day"
            else:
                self.current_attack = "none"
        else:
            self.current_attack = "none"

        # Generate metrics
        if self.current_attack == "ddos":
            reqs = random.randint(1000, 5000)
            load = random.uniform(0.4, 0.6)
            susp = random.randint(0, 2)
        elif self.current_attack == "malware":
            reqs = random.randint(50, 150)
            load = random.uniform(0.8, 0.99)
            susp = random.randint(10, 50)
        elif self.current_attack == "zero_day":
            reqs = random.randint(50, 150)
            load = random.uniform(0.1, 0.4)
            susp = random.randint(100, 500)
        else:
            reqs = random.randint(10, 50)
            load = random.uniform(0.1, 0.3)
            susp = 0

        return Observation(
            incoming_requests=reqs,
            system_load=round(load, 2),
            suspicious_activity=susp,
            network_health=round(self.network_health, 2)
        )

    def step(self, action: str) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        self.step_count += 1
        
        correct_action = "ignore"
        if self.current_attack == "ddos":
            correct_action = "block_ip"
        elif self.current_attack == "malware":
            correct_action = "scan_system"
        elif self.current_attack == "zero_day":
            correct_action = "deploy_patch"

        penalty = 0.0
        reward = 0.0
        success = False

        if action == correct_action:
            # Defended successfully
            success = True
            reward = 1.0 / self.max_steps # 0.1 normalized reward
        else:
            # Failed to defend
            penalty = 15.0
            self.network_health = max(0.0, self.network_health - penalty)
            reward = 0.0

        done = self.step_count >= self.max_steps
        
        info = {
            "attack_type": self.current_attack,
            "action_taken": action,
            "correct_action": correct_action,
            "success": success,
            "health": self.network_health
        }
        self.history.append(info)

        # Ensure that if done is True, we pass the final state back, 
        # or we could generate next state if not done.
        # Often environments evaluate state AFTER action is applied.
        next_obs = None
        if not done:
            next_obs = self._generate_next_state()
        else:
            # Just return current metrics but updated health
            next_obs = Observation(
                incoming_requests=0,
                system_load=0,
                suspicious_activity=0,
                network_health=round(self.network_health, 2)
            )

        return next_obs, reward, done, info

    def get_state(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "network_health": self.network_health,
            "current_attack": self.current_attack,
            "history": self.history
        }

# Global singleton for FastAPI server
env_instance = CyberEnvironment()
