import argparse
import asyncio
import logging
import sys
import json
from pathlib import Path
from typing import Optional

import nodriver

from potoken_generator.extractor import PotokenExtractor, TokenInfo
from potoken_generator.server import PotokenServer

logger = logging.getLogger('potoken')


def save_token_info_to_json(token_info: Optional[TokenInfo], filename='token_info.json'):
    """
    Saves token information to a JSON file.

    Args:
        token_info (Optional[TokenInfo]): Token info object.
        filename (str): Name of the output JSON file. Defaults to 'token_info.json'.
    """

    if token_info is None:
        logger.warning('failed to extract token')
        sys.exit(1)

    visitor_data = token_info.visitor_data
    po_token = token_info.potoken

    # Create a dictionary with the extracted information
    data_dict = {
        'visitor_data': visitor_data,
        'po_token': po_token
    }

    try:
        # Open the file in write mode and load any existing content
        with open(filename, 'w') as f:
            json.dump(data_dict, f)
            logger.info(f'Token info saved to {filename}')
    except Exception as e:
        logger.error(f'Failed to save token info: {e}')


def print_token_and_exit(token_info: Optional[TokenInfo]):
    if token_info is None:
        logger.warning('failed to extract token')
        sys.exit(1)
    
    visitor_data = token_info.visitor_data
    po_token = token_info.potoken

    print('visitor_data: ' + visitor_data)
    print('po_token: ' + po_token)

    save_token_info_to_json(token_info)

    if len(po_token) < 160:
        logger.warning("there is a high chance that the potoken generated won't work. Please try again on another internet connection")
        sys.exit(1)
    sys.exit(0)


async def run(loop: asyncio.AbstractEventLoop, oneshot: bool,
              update_interval: int, bind_address: str, port: int,
              browser_path: Optional[Path] = None) -> None:
    potoken_extractor = PotokenExtractor(loop, update_interval=update_interval, browser_path=browser_path)
    token = await potoken_extractor.run_once()
    if oneshot:
        print_token_and_exit(token)

    extractor_task = loop.create_task(potoken_extractor.run())
    potoken_server = PotokenServer(potoken_extractor, port=port, bind_address=bind_address)
    server_task = loop.create_task(asyncio.to_thread(potoken_server.run))

    try:
        await asyncio.gather(extractor_task, server_task)
    except Exception:
        # exceptions raised by the tasks are intentionally propogated
        # to ensure process exit code is 1 on error
        raise
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info('Stopping...')
    finally:
        potoken_server.stop()


def set_logging(log_level: int = logging.DEBUG) -> None:
    log_format = '%(asctime)s.%(msecs)03d [%(name)s] [%(levelname)s] %(message)s'
    datefmt = '%Y/%m/%d %H:%M:%S'
    logging.basicConfig(level=log_level, format=log_format, datefmt=datefmt)
    logging.getLogger('asyncio').setLevel(logging.INFO)
    logging.getLogger('nodriver').setLevel(logging.WARNING)
    logging.getLogger('uc').setLevel(logging.WARNING)
    logging.getLogger('websockets').setLevel(logging.WARNING)


def args_parse() -> argparse.Namespace:
    description = '''
Retrieve potoken using Chromium runned by nodriver, serve it on a json endpoint

    Token is generated on startup, and then every UPDATE_INTERVAL seconds.
    With web-server running on default port, the token is available on the
    http://127.0.0.1:8080/token endpoint. It is possible to request immediate
    token regeneration by accessing http://127.0.0.1:8080/update
    '''
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-o', '--oneshot', action='store_true', default=True,
                        help='Do not start server. Generate token once, print it and exit')
    parser.add_argument('--update-interval', '-u', type=int, default=300,
                        help='How ofthen new token is generated, in seconds (default: %(default)s)')
    parser.add_argument('--port', '-p', type=int, default=8080,
                        help='Port webserver is listening on (default: %(default)s)')
    parser.add_argument('--bind', '-b', default='127.0.0.1',
                        help='Address webserver binds to (default: %(default)s)')
    parser.add_argument('--chrome-path', '-c', type=Path, default=None,
                        help='Path to the Chromiun executable')
    return parser.parse_args()


def main() -> None:
    args = args_parse()
    set_logging(logging.WARNING if args.oneshot else logging.INFO)
    loop = nodriver.loop()
    main_task = run(loop, oneshot=args.oneshot,
                    update_interval=args.update_interval,
                    bind_address=args.bind,
                    port=args.port,
                    browser_path=args.chrome_path
                    )
    loop.run_until_complete(main_task)
