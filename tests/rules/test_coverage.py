import arche.rules.coverage as cov
from arche.rules.result import Level
from conftest import create_result, Job
import pandas as pd
import pytest


@pytest.mark.parametrize(
    "df, expected_messages",
    [
        (
            pd.DataFrame([{"_key": 0}]),
            {
                Level.INFO: [
                    (
                        "PASSED",
                        None,
                        None,
                        pd.Series([1], index=["_key"], name="Fields Coverage"),
                    )
                ]
            },
        ),
        (
            pd.DataFrame([("Jordan", None)], columns=["Name", "Field"]),
            {
                Level.ERROR: [
                    (
                        "1 empty field(s)",
                        None,
                        None,
                        pd.Series(
                            [1, 0], index=["Name", "Field"], name="Fields Coverage"
                        ),
                    )
                ]
            },
        ),
        (
            pd.DataFrame([(0, "")], columns=["Name", "Field"]),
            {
                Level.INFO: [
                    (
                        "PASSED",
                        None,
                        None,
                        pd.Series(
                            [1, 1], index=["Field", "Name"], name="Fields Coverage"
                        ),
                    )
                ]
            },
        ),
    ],
)
def test_check_fields_coverage(df, expected_messages):
    result = cov.check_fields_coverage(df)
    assert result == create_result("Fields Coverage", expected_messages)


@pytest.mark.parametrize(
    "source_stats, target_stats, expected_messages",
    [
        (
            {"counts": {"f1": 100, "f2": 150}, "totals": {"input_values": 100}},
            {"counts": {"f2": 100, "f3": 150}, "totals": {"input_values": 100}},
            {
                Level.ERROR: [("The difference is greater than 10% for 3 field(s)",)],
                Level.INFO: [
                    (
                        "",
                        None,
                        None,
                        pd.Series(
                            [50.0, 100.0, 150.0],
                            index=["f2", "f1", "f3"],
                            name="Coverage difference between 0 and 1",
                        ),
                    )
                ],
            },
        ),
        (
            {"counts": {"f1": 100, "f2": 150}, "totals": {"input_values": 100}},
            {"counts": {"f1": 106, "f2": 289}, "totals": {"input_values": 200}},
            {
                Level.ERROR: [("The difference is greater than 10% for 1 field(s)",)],
                Level.WARNING: [
                    ("The difference is between 5% and 10% for 1 field(s)",)
                ],
                Level.INFO: [
                    (
                        "",
                        None,
                        None,
                        pd.Series(
                            [5.5, 47.0],
                            index=["f2", "f1"],
                            name="Coverage difference between 0 and 1",
                        ),
                    )
                ],
            },
        ),
        (
            {"counts": {"f1": 100, "f2": 150}, "totals": {"input_values": 100}},
            {"counts": {"f1": 94, "f2": 141}, "totals": {"input_values": 100}},
            {
                Level.WARNING: [
                    ("The difference is between 5% and 10% for 2 field(s)",)
                ],
                Level.INFO: [
                    (
                        "",
                        None,
                        None,
                        pd.Series(
                            [6.0, 9.0],
                            index=["f1", "f2"],
                            name="Coverage difference between 0 and 1",
                        ),
                    )
                ],
            },
        ),
        (
            {"counts": {"state": 100}, "totals": {"input_values": 100}},
            {"counts": {"state": 100}, "totals": {"input_values": 100}},
            {},
        ),
    ],
)
def test_get_difference(source_stats, target_stats, expected_messages):
    result = cov.get_difference(
        Job(stats=source_stats, key="0"), Job(stats=target_stats, key="1")
    )
    assert result == create_result("Coverage Difference", expected_messages)


@pytest.mark.parametrize(
    "source_cols, target_cols, expected_messages",
    [
        (["range", "name"], ["name"], {Level.INFO: [("New - range",)]}),
        (["name"], ["name", "sex"], {Level.ERROR: [("Missing - sex",)]}),
    ],
)
def test_compare_scraped_fields(source_cols, target_cols, expected_messages):
    result = cov.compare_scraped_fields(
        pd.DataFrame([], columns=source_cols), pd.DataFrame([], columns=target_cols)
    )
    assert result == create_result("Scraped Fields", expected_messages)
