from fastapi import FastAPI
from market_clock.regions import get_regions, RegionEnum, EXCHANGE_DICTIONARY

app = FastAPI()


@app.get("/")
async def index():
    regions = get_regions()
    regions.update()
    return regions


@app.get("/region/{region_name}")
async def get_region_name(region_name: RegionEnum):
    regions = get_regions()
    exchange = EXCHANGE_DICTIONARY[region_name.value]
    exchange.update()
    return exchange
