def recession_week(config):
    for p in config["BASE_DAILY_DEMAND"]:
        config["BASE_DAILY_DEMAND"][p] *= 0.6

def viral_spike(config):
    for p in config["BASE_DAILY_DEMAND"]:
        config["BASE_DAILY_DEMAND"][p] *= 2.5
    for p in config["PRODUCTION_RANGE"]:
        low, high = config["PRODUCTION_RANGE"][p]
        config["PRODUCTION_RANGE"][p] = (low // 2, high // 2)

def marketing_death_spiral(config):
    for ch in config["CHANNEL_BEHAVIOR"]:
        config["CHANNEL_BEHAVIOR"][ch]["cvr"] = (
            config["CHANNEL_BEHAVIOR"][ch]["cvr"][0] * 0.6,
            config["CHANNEL_BEHAVIOR"][ch]["cvr"][1] * 0.6,
        )
        config["CHANNEL_BEHAVIOR"][ch]["cpc"] = (
            config["CHANNEL_BEHAVIOR"][ch]["cpc"][0] * 1.4,
            config["CHANNEL_BEHAVIOR"][ch]["cpc"][1] * 1.4,
        )
