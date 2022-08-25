from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

software_names = [SoftwareName.FIREFOX.value]
operating_systems = [OperatingSystem.MAC.value, OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=20)
user_agent = user_agent_rotator.get_random_user_agent()

for agent in range(10):
    print(user_agent_rotator.get_random_user_agent())
