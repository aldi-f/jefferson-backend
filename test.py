# %%
from app.clients.warframe.worldstate.client import worldstate_client

# %%
worldstate = await worldstate_client.get_worldstate()
print(worldstate)
# %%
len(worldstate.alerts)
