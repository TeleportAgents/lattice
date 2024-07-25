from typing import Tuple

import pandas as pd

from src.lattice.retrieve.example_data_1 import ENTITY, RELATIONSHIP


def get_db_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    entity = pd.DataFrame.from_dict(data=ENTITY)
    relationship = pd.DataFrame.from_dict(data=RELATIONSHIP)
    return entity, relationship


def main():
    entity, relationship = get_db_data()
    pass


if __name__ == "__main__":
    main()
