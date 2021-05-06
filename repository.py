import tinvest
import model
import datetime
import asyncio

from typing import Any, Optional


class PortfolioRepository:

    def __init__(self, token: str):
        self._tclient = tinvest.AsyncClient(token)
        self._tapi = tinvest.OpenApi(self._tclient)

    async def get_portfolio(self) -> Optional[model.Portfolio]:
        # получение данных о бумагах в портфеле
        response = self._tapi.portfolio.portfolio_get()
        tin_portfolio: Optional[tinvest.Portfolio] = await _get_one_payload(response)

        if tin_portfolio is None:
            return None

        result = model.Portfolio()

        operations_requests = []
        from_date = datetime.datetime(year=2016, month=1, day=1)
        to_date = datetime.datetime.now()

        start_at = datetime.datetime.now()
        # получение данных об операциях со всеми бумагами в портфеле с момента основания Тинькофф.Инвестиции
        for position in tin_portfolio.positions:
            # год запуска Тинькофф.Инвестиции
            operations_raw = self._tapi.operations.operations_get(
                from_date,
                to_date,
                position.figi,
            )
            operations_requests.append(_get_one_payload(operations_raw))

        prepared_at = datetime.datetime.now()

        preparing_time = prepared_at - start_at
        print(f'Preparing time async: {preparing_time.total_seconds()}')

        operations_responses = await asyncio.gather(*operations_requests)

        for i, position in enumerate(tin_portfolio.positions):
            operations = operations_responses[i]

            result.positions[position.figi] = model.PortfolioPosition(
                common_info=position,
                operations=operations.operations if operations else [],
            )

        end_at = datetime.datetime.now()
        receiving_time = end_at - prepared_at
        time_delta = end_at - start_at
        print(f'Receiving time async: {receiving_time.total_seconds()}')
        print(f'Total time async: {time_delta.total_seconds()}')
        await self._tclient.close()
        return result


async def _get_one_payload(async_response) -> Optional[Any]:
    result = None
    extra_iter = 0
    async for raw_resp in async_response.gen:
        if extra_iter != 0:
            continue
        if raw_resp.status == 200:
            try:
                resp = await raw_resp.parse_json()
                result = resp.payload
            except Exception as exc:
                print(f'WARNING: parse json error: {exc}')
        else:
            print(f'WARNING: Http status is {raw_resp.status}')
        extra_iter += 1

    if extra_iter != 1:
        print(f'WARNING: Number of extra iteration: {extra_iter-1}')

    return result
