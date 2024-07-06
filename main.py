from asyncio import gather, run, set_event_loop_policy
from datetime import datetime, timedelta
from logging import INFO, basicConfig, error, info, warning
from platform import system
from sys import argv

from aiohttp import ClientSession


async def request(
    day: int,
    currencies: set[str],
    session: ClientSession
) -> dict:
    '''
    Retrieves exchange rates from PrivatBank API for a specific day.

    :param day: int
    :param currencies: set[str]
    :param session: ClientSession

    :return: dict
    '''

    URL = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
    DATE = (datetime.now() - timedelta(day)).strftime('%d.%m.%Y')
    RATES = 'sale', 'purchase'

    try:
        async with session.get(URL + DATE, ssl=False) as response:
            if response.status != 200:
                raise Exception(f'Bad status: {response.status}')
            elif response.headers['Content-Type'] != 'application/json':
                raise Exception('The format is not JSON.')

            items = (await response.json())['exchangeRate']
            items = filter(lambda item: item['currency'] in currencies, items)

            items = {item['currency']: {rate: item.get(f'{rate}Rate')
                                        for rate in RATES}
                     for item in items}

            return {DATE: items}

    except Exception as e:
        raise Exception(e)


async def main(days: int, currencies: list[str]) -> list[dict]:
    '''
    Make a few requests in parallel and use only one session for that.

    :param days: int
    :param currencies: list[str]

    :return: list[dict]
    '''

    if days < 1 or days > 10:
        raise Exception('Number of days must be from one to ten.')

    currencies = {currency.upper() for currency in currencies} | {'EUR', 'USD'}

    async with ClientSession() as session:
        return await gather(*[request(day, currencies, session)
                              for day in range(days)])

if __name__ == '__main__':
    basicConfig(level=INFO)

    try:
        if system() == 'Windows':
            from asyncio import WindowsSelectorEventLoopPolicy

            set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    except Exception:
        error('App preparation for your operating system has failed.')
    else:
        try:
            info(run(main(int(argv[1]), argv[2:] if len(argv) > 2 else [])))
        except IndexError:
            error('The required CLI argument (days number) is missing.')
        except ValueError:
            error('Number of days must be a decimal.')
        except Exception as e:
            warning(e)
