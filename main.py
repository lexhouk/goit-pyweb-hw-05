from asyncio import run, set_event_loop_policy
from datetime import datetime
from logging import INFO, basicConfig, error, info, warning
from platform import system
from sys import argv

from aiohttp import ClientConnectionError, ClientSession


def alert(suffix: str) -> str:
    PREFIX = 'Something went wrong because a request to API was returned %.'

    warning(PREFIX % suffix)


async def main(days: int) -> None:
    if days < 1 or days > 10:
        raise Exception('Number of days must be from one to ten.')

    url = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
    url += datetime.now().strftime('%d.%m.%Y')

    async with ClientSession() as session:
        try:
            async with session.get(url, ssl=False) as response:
                if response.status == 200:
                    if response.headers['Content-Type'] == 'application/json':
                        info(await response.json())
                    else:
                        alert('not in JSON format')
                else:
                    alert(f'with status {response.status}')
        except ClientConnectionError as e:
            error(e)

if __name__ == '__main__':
    try:
        if system() == 'Windows':
            from asyncio import WindowsSelectorEventLoopPolicy

            set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    except Exception:
        error('App preparation for your operating system has failed.')
    finally:
        basicConfig(level=INFO)

        try:
            run(main(int(argv[1])))
        except IndexError:
            error('The required CLI argument (days number) is missing.')
        except ValueError:
            error('Number of days must be a decimal.')
        except Exception as e:
            error(e)
