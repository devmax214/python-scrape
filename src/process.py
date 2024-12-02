import os
import sys
from datetime import datetime
from pathlib import Path
from multiprocessing import Pool
from scripts.common.model import *
from scripts.common.constants import *
from scripts.common.functions import *

main_dir = str(Path(os.path.dirname(__file__)))
scrapy_dir = main_dir+"/scripts/scraping"

def run_scrapy(params):
  index, count, url, retailer_type = params
  try:
    command = None
    if int(retailer_type) == RETAIL_TYPES['amazon']:
      command = f'cd {scrapy_dir} && scrapy crawl amazon -a index={index} -a count={count} -a url="{url}"'
    else:  
      command = f'cd {scrapy_dir} && scrapy crawl other -a index={index} -a count={count} -a retailer_type="{retailer_type}" -a url="{url}"'
    os.system(command)
    print("runing scrapy", index, url)
  except Exception as e:
    print("except", e)

def main(retailer_type, prefix_url):
  print("start process", retailer_type, prefix_url)
  if retailer_type == "-1":
    os.system(f'cd {scrapy_dir} && scrapy crawl cashback')
    return
  
  cursor = get_db_conn().cursor()
  cursor.execute("SELECT DISTINCT ProductURL FROM `TargetRaw`.`UserInput` WHERE ProductURL LIKE '{}%' AND IsDeleted = 0 order by ID;".format(prefix_url))
  urls = [url[0] for url in cursor.fetchall()]
  
  id_name = get_spider_name(retailer_type)
  count = len(urls)
  insert_scrapper_log(cursor, id_name, 0, count, '', 0, 'Getting ' + id_name + ' Prices', datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
  print("start scrapper log", count)
  
  tasks = [(i, count, url, retailer_type) for i, url in enumerate(urls)]
  with Pool(processes=5) as pool:
      pool.map(run_scrapy, tasks)
      
  # exiting the 'with'-block has stopped the pool
  print("Now the pool is closed and no longer available")

if __name__ == "__main__":
    retailer_type = sys.argv[1]
    prefix_url = sys.argv[2]
    main(retailer_type, prefix_url)