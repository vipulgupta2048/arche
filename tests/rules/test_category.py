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


@pytest.mark.parametrize(
    "source, target, categories, expected_messages",
    [
        (
            {
                "sex": ["male", "female", "male", np.nan],
                "country": ["uk", "uk", "uk", "us"],
                "age": [25, 25, 25, 25],
                "race": ["white", "black", "indian", "indian"],
            },
            {
                "sex": ["male", "female", "male"],
                "country": ["uk", "uk", "uk"],
                "age": [25, 25, 25],
                "race": ["white", "black", "indian"],
            },
            ["sex", "country", "age", "race"],
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
                        pd.Series(
                            [8.33, 16.67, 25.00],
                            index=["female", "male", np.nan],
                            name="Coverage difference between s's and t's sex",
                        ),
                    ),
                    (
                        "'country' PASSED",
                        None,
                        None,
                        pd.Series(
                            [25.0, 25.0],
                            index=["uk", "us"],
                            name="Coverage difference between s's and t's country",
                        ),
                    ),
                    (
                        "'race' PASSED",
                        None,
                        None,
                        pd.Series(
                            [8.33, 8.33, 16.67],
                            index=["black", "white", "indian"],
                            name="Coverage difference between s's and t's race",
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
