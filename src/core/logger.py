import logging
import logging.config
import yaml
import os
from pathlib import Path

def setup_logging(
        default_path='log_config.yaml',
        default_level=logging.DEBUG,
        env_key='LOG_CFG'
):
    
    path = os.getenv(env_key, default_path)
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f)

        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


setup_logging()

logger = logging.getLogger('server')
