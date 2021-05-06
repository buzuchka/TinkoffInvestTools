import os
import tinvest
import model
import asyncio
from repository import PortfolioRepository


def get_token():
    token_file_name = 'token.txt'
    if not os.path.exists(token_file_name):
        print('There is no file ' + token_file_name)
        return

    token_file = open(token_file_name, "r")
    token = token_file.readline()
    token_file.close
    return token


async def test_get_portfolio():
    token = get_token()
    if not token:
        print('Token is empty')
        return

    rep = PortfolioRepository(token)
    await rep.get_portfolio()


async def main():
    token = get_token()
    if not token:
        print('Token is empty')
        return

    aclient = tinvest.AsyncClient(token)
    atapi = tinvest.OpenApi(aclient)
    response = atapi.portfolio.portfolio_get()
    print(f'response = {response}')
    print(f'response = {response.__dir__()}')
    async for r in response.gen:
        print(f'r: {r.status}')
        portfolio_resp: tinvest.PortfolioResponse = await r.parse_json()
        portfolio: tinvest.Portfolio = portfolio_resp.payload
        print(f'portfolio: {portfolio}')

    await aclient.close()

asyncio.run(test_get_portfolio())
