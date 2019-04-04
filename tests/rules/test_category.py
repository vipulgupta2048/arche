from typing import Dict, List

import arche.rules.category as c
from arche.rules.result import Level
from conftest import create_result
import numpy as np
import pandas as pd
import pytest


@pytest.mark.parametrize(
    "data, cat_names, expected_messages",
    [
        (
            {"sex": ["male", "female", "male"], "country": ["uk", "uk", "uk"]},
            ["sex", "country"],
            {
                Level.INFO: [
                    (
                        "2 categories in 'sex'",
                        None,
                        None,
                        pd.Series({"female": 1, "male": 2}, name="sex"),
                    ),
                    (
                        "1 categories in 'country'",
                        None,
                        None,
                        pd.Series({"uk": 3}, name="country"),
                    ),
                ]
            },
        )
    ],
)
def test_get_coverage_per_category(data, cat_names, expected_messages):
    assert c.get_coverage_per_category(pd.DataFrame(data), cat_names) == create_result(
        "Coverage For Scraped Categories", expected_messages
    )


def create_df(data: Dict, index: List[str], name: str) -> pd.DataFrame:
    df = pd.DataFrame(data, index=index)
    df.name = "Coverage difference in sex"
    return df


@pytest.mark.parametrize(
    "source, target, categories, expected_messages",
    [
        (
            {
                "sex": ["male", "female", "male", np.nan],
                "country": ["uk", "uk", "uk", "us"],
                "age": [25, 25, 25, 25],
            },
            {
                "sex": ["male", "female", "male"],
                "country": ["uk", "uk", "uk"],
                "age": [25, 25, 25],
            },
            ["sex", "country", "age"],
            {
                Level.WARNING: [
                    ("The difference is greater than 20% for 1 value(s) of sex",),
                    ("The difference is greater than 20% for 2 value(s) of country",),
                ],
                Level.INFO: [
                    (
                        "'sex' PASSED",
                        None,
                        None,
                        create_df(
                            {"s": [25.0, 25.0, 50.0], "t": [0.0, 33.33, 66.67]},
                            index=[np.nan, "female", "male"],
                            name="Coverage difference in sex",
                        ),
                    ),
                    (
                        "'country' PASSED",
                        None,
                        None,
                        create_df(
                            {"s": [25.0, 75.0], "t": [0.0, 100.0]},
                            index=["us", "uk"],
                            name="Coverage difference in country",
                        ),
                    ),
                    (
                        "'age' PASSED",
                        None,
                        None,
                        create_df(
                            {"s": [100.0], "t": [100.0]},
                            index=[25],
                            name="Coverage difference in age",
                        ),
                    ),
                ],
            },
        )
    ],
)
def test_get_difference(source, target, categories, expected_messages):
    assert c.get_difference(
        "s", "t", pd.DataFrame(source), pd.DataFrame(target), categories
    ) == create_result("Category Coverage Difference", expected_messages)
