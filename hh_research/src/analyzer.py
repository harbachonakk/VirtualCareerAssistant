r"""Researcher: collect statistics, predict salaries etc.

------------------------------------------------------------------------
"""

import re
from typing import Dict, List

import matplotlib.pyplot as plt
import nltk
import numpy as np
import pandas as pd
import seaborn as sns
import logging

logger = logging.getLogger(__name__)

class Analyzer:
    def __init__(self, save_csv: bool = False):
        self.save_csv = save_csv
        # try:
        #     nltk.download("stopwords")
        # except:
        #     print(r"[INFO] You have downloaded stopwords!")

    @staticmethod
    def find_top_words_from_keys(keys_list: List) -> pd.Series:
        """Find most used words into description of vacancies.

        Parameters
        ----------
        keys_list : list
            List of sentences from keywords of vacancies.

        Returns
        -------
        pd.Series
            List of sorted keywords.

        """
        # List of keys for all vacancies
        lst_keys = []
        for keys_elem in keys_list:
            for el in keys_elem:
                if el != "":
                    lst_keys.append(re.sub("'", "", el.lower()))

        # Unique keys and their counter
        set_keys = set(lst_keys)
        # Dict: {Key: Count}
        dct_keys = {el: lst_keys.count(el) for el in set_keys}
        # Sorted dict
        srt_keys = dict(
            sorted(dct_keys.items(), key=lambda x: x[1], reverse=True))
        # Return pandas series
        return pd.Series(srt_keys, name="Keys")

    @staticmethod
    def find_top_words_from_description(desc_list: List) -> pd.Series:
        """Find most used words into description of vacancies.

        Parameters
        ----------
        desc_list : list
            List of sentences from vacancy description.

        Returns
        -------
        pd.Series
            List of sorted words from descriptions.

        """
        words_ls = " ".join(
            [re.sub(" +", " ", re.sub(r"\d+", "", el.strip().lower())) for el in desc_list])
        # Find all words
        words_re = re.findall("[a-zA-Z]+", words_ls)
        # Filter words with length < 3
        words_l2 = [el for el in words_re if len(el) > 2]
        # Unique words
        words_st = set(words_l2)
        # Remove 'stop words'
        try:
            _ = nltk.corpus.stopwords.words("english")
        except LookupError:
            nltk.download("stopwords")
        finally:
            stop_words = set(nltk.corpus.stopwords.words("english"))

        # XOR for dictionary
        words_st ^= stop_words
        words_st ^= {"amp", "quot"}
        # Dictionary - {Word: Counter}
        words_cnt = {el: words_l2.count(el) for el in words_st}
        # Pandas series
        return pd.Series(dict(sorted(words_cnt.items(), key=lambda x: x[1], reverse=True)))

    def prepare_df(self, vacancies: Dict) -> pd.DataFrame:
        """Prepare data frame and save results

        Parameters
        ----------
        vacancies: dict
            Dict of parsed vacancies.

        """

        # Create pandas dataframe
        df = pd.DataFrame.from_dict(vacancies)
        # Print some info from data frame
        with pd.option_context("display.max_rows", None, "display.max_columns", None):
            #print(df[df["Salary"]][["Employer", "From", "To", "Experience"]][0:15])
            logging.info('dataframe - {}'.format((df[df["Salary"]][["Employer", "From", "To", "Experience"]][0:15]).to_string()))
            print(df[df["Salary"]][["Employer", "From", "To", "Experience"]][0:15])
        # Save to file
        if self.save_csv:
            #print("\n\n[INFO]: Save dataframe to file...")
            logging.info("\n\n[INFO]: Save dataframe to file...")
            df.to_csv("hh_results.csv", index=False)
        return df

    def analyze_df(self, df: pd.DataFrame):
        """Load data frame and analyze results

        """
        sns.set()
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #print(df[df["Salary"]][0:7])
        logging.info('dataframe - {}'.format((df[df["Salary"]][0:7]).to_string()))
        #print("\nNumber of vacancies: {}".format(df["Ids"].count()))
        
        num_of_vacancies = df["Ids"].count()
        logging.info("\nNumber of vacancies: {}".format(num_of_vacancies))

        logging.info("\nVacancy with max salary: ")
        max_salary = df.iloc[df[["From", "To"]].idxmax()]
        logging.info('dataframe - {}'.format(max_salary.to_string()))

        min_salary = df.iloc[df[["From", "To"]].idxmin()]
        #print(df.iloc[df[["From", "To"]].idxmax()])
        logging.info("\nVacancy with min salary: ")
        #print(df.iloc[df[["From", "To"]].idxmin()])
        logging.info('dataframe - {}'.format(min_salary.to_string()))

        logging.info("\n[INFO]: Describe salary data frame")
        df_stat = df[["From", "To"]].dropna().describe().applymap(np.int32)
        #df_stat = df[["From", "To"]].describe().astype('Int64')
        #print(df_stat.iloc[list(range(4)) + [-1]])
        logging.info('dataframe - {}'.format((df_stat.iloc[list(range(4)) + [-1]]).to_string()))
        print(df_stat.iloc[list(range(4)) + [-1]])
        logging.info('\n[INFO]: Average statistics (filter for "From"-"To" parameters):')
        print('\n[INFO]: Average statistics (filter for "From"-"To" parameters):')
        comb_ft = np.nanmean(
            df[df["Salary"]][["From", "To"]].dropna().to_numpy(), axis=1)
        logging.info("\nDescribe salary series:")
        logging.info("\nMin    : %d" % np.min(comb_ft))
        logging.info("\nMax    : %d" % np.max(comb_ft))
        logging.info("\nMean   : %d" % np.mean(comb_ft))
        logging.info("\nMedian : %d" % np.median(comb_ft))
        max_salary = ("Максимальная зарплата   : %d RUB" % np.max(comb_ft))
        min_salary = ("Минимальная зарплата   : %d RUB" % np.min(comb_ft))
        mean_salary = ("Средняя зарплата   : %d RUB" % np.mean(comb_ft))
        median_salary = ("Медианная зарплата   : %d RUB" % np.median(comb_ft))

        logging.info("\nMost frequently used words [Keywords]:")
        print("\nMost frequently used words [Keywords]:")
        most_keys = self.find_top_words_from_keys(df["Keys"].to_list())
        #print(most_keys[:12])
        most_keys = most_keys[:12]
        logging.info('dataframe - {}'.format(most_keys))
        print(most_keys)

        logging.info("\nMost frequently used words [Description]:")
        print("\nMost frequently used words [Description]:")
        most_words = self.find_top_words_from_description(
            df["Description"].to_list())
        most_words = most_words[:12]
        logging.info('dataframe - {}'.format(most_words))
        print(most_words)

        logging.info("\n[INFO]: Plot results. Close figure box to continue...")
        fz = plt.figure("Salary plots", figsize=(12, 8))
        fz.add_subplot(2, 2, 1)
        plt.title("From / To: Boxplot")
        sns.boxplot(data=df[["From", "To"]].dropna() / 1000, width=0.4)
        plt.ylabel("Salary x 1000 [RUB]")
        fz.add_subplot(2, 2, 2)
        plt.title("From / To: Swarmplot")
        sns.swarmplot(data=df[["From", "To"]].dropna() / 1000, size=6)

        fz.add_subplot(2, 2, 3)
        plt.title("From: Distribution ")
        sns.distplot(df["From"].dropna() / 1000, bins=14, color="C0")
        plt.grid(True)
        plt.xlabel("Salary x 1000 [RUB]")
        plt.xlim([-50, df["From"].max() / 1000])
        plt.yticks([], [])

        fz.add_subplot(2, 2, 4)
        plt.title("To: Distribution")
        sns.distplot(df["To"].dropna() / 1000, bins=14, color="C1")
        plt.grid(True)
        plt.xlim([-50, df["To"].max() / 1000])
        plt.xlabel("Salary x 1000 [RUB]")
        plt.yticks([], [])
        plt.tight_layout()

        return(num_of_vacancies, max_salary, min_salary, mean_salary, median_salary, most_keys, most_words)

"""
if __name__ == "__main__":
    analyzer = Analyzer()
"""
