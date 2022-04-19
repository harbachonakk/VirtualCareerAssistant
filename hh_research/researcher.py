"""Head Hunter Researcher

Description   :
    HeadHunter (hh.ru) main research script.

    1. Get data from hh.ru by user request (i.e. 'Machine learning')
    2. Collect all vacancies.
    3. Parse JSON and get useful values: salary, experience, name,
    skills, employer name etc.
    4. Calculate some statistics: average salary, median, std, variance.
------------------------------------------------------------------------
"""

import json
import sys
from typing import Dict, Optional
import os
import logging
"""
from src.analyzer import Analyzer
from src.currency_exchange import Exchanger
from src.collector import Collector
from src.parser import Settings_Parser
from src.predictor import Predictor
"""
from hh_research.src.predictor import Predictor
from hh_research.src.parser import Settings_Parser
from hh_research.src.collector import Collector
from hh_research.src.currency_exchange import Exchanger
from hh_research.src.analyzer import Analyzer

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# CACHE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "cache")
CACHE_DIR = "hh_research\src\cache"
SETTINGS_PATH = "hh_research\settings.json"

logger = logging.getLogger(__name__)


class Researcher:
    """Main class for searching vacancies and analyze them."""

    def __init__(self, configs: str = None, settings_dict: Dict = None, no_parse: bool = False):
        self.settings_dict = settings_dict

        # self.settings_pars = Settings_Parser(configs, no_parse=no_parse)
        self.exchanger = Exchanger(params=settings_dict)
        self.collector: Optional[Collector] = None
        self.analyzer: Optional[Analyzer] = None
        self.predictor = Predictor()

    def update(self, **kwargs):
        # self.settings.update_params(**kwargs)
        # if not any(self.settings_dict['rates'].values()) or self.settings_dict['update']:
        logger.info(
            "[INFO]: Trying to get exchange rates from remote server...")
        print("[INFO]: Trying to get exchange rates from remote server...")
        self.settings_dict['rates'] = self.exchanger.update_exchange_rates(
            self.settings_dict['rates'])
        # self.exchanger.save_rates(self.settings.rates)

        logger.info(
            f"[INFO]: Get exchange rates: {self.settings_dict['rates']}")
        print(f"[INFO]: Get exchange rates: {self.settings_dict['rates']}")
        self.collector = Collector(self.settings_dict['rates'])
        # self.analyzer=Analyzer(self.settings.save_result)
        self.analyzer = Analyzer(save_csv=False)

    def __call__(self):
        num_of_vacancies = None
        max_salary = None 
        min_salary = None 
        mean_salary = None 
        median_salary = None 
        most_keys = None
        most_words = None
        logger.info(
            "[INFO]: Collect data from JSON. Create list of vacancies...")
        vacancies = self.collector.collect_vacancies(
            query=self.settings_dict['options'], refresh=self.settings_dict[
                'refresh'], max_workers=self.settings_dict['max_workers']
        )
        if vacancies is not None:
            logger.info("[INFO]: Prepare dataframe...")
            df = self.analyzer.prepare_df(vacancies)
            logger.info("\n[INFO]: Analyze dataframe...")
            num_of_vacancies, max_salary, min_salary, mean_salary, median_salary, most_keys, most_words = self.analyzer.analyze_df(df)
            logger.info("\n[INFO]: Predict None salaries...")
            # total_df = self.predictor.predict(df)
            # self.predictor.plot_results(total_df)
            logger.info("[INFO]: Done! Exit()")
            print("[INFO]: Done! Exit()")
            
        else:
            logger.info("[FAIL] No vacancies found on such request")
            print("[FAIL] No vacancies found on such request")
        return num_of_vacancies, max_salary, min_salary, mean_salary, median_salary, most_keys, most_words

"""
if __name__ == "__main__":
    hh_analyzer = Researcher()
    hh_analyzer.update()
    hh_analyzer()
else:
    print('ok')
"""
