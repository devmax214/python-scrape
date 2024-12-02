from scripts.common.constants import *
import os
from pathlib import Path
from scripts.notifier.start_notifier import start_notifier

# main_dir = str(Path(os.path.dirname(__file__)))
# scrapy_dir = main_dir+"/scripts/scraping"

# if __name__ == "__main__":
#     bash_command="python process.py -1 https://www.rakuten.com/"
#     os.system(bash_command)

start_notifier()