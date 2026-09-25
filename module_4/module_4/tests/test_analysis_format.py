"""Check every answer and every percentage, including zero and rounding."""
import re
import pytest
from bs4 import BeautifulSoup

pytestmark = pytest.mark.analysis


@pytest.mark.parametrize("value,expected", [(0, "0.00%"), (100, "100.00%"),
    (39.2851, "39.29%"), (100 / 3, "33.33%"), (2 / 3 * 100, "66.67%")])
def test_all_percentage_values_have_exactly_two_decimals(client, dependencies, value, expected):
    for key in ("q2", "q5", "q11"):
        dependencies["query"].return_value[key] = value
    page = BeautifulSoup(client.get("/analysis").data, "html.parser")
    percentages = page.select('[data-testid="percentage"]')
    assert len(percentages) == 3
    assert [item.text for item in percentages] == [expected] * 3
    assert all(re.fullmatch(r"\d+\.\d{2}%", item.text) for item in percentages)
    assert len(re.findall(r"\d+(?:\.\d+)?%", page.get_text())) == 3
    for answer in page.select('[data-testid="analysis-answer"]'):
        assert answer.get_text(strip=True).startswith("Answer:")


def test_missing_averages_and_degree_groups_render(client):
    page = BeautifulSoup(client.get("/analysis").data, "html.parser")
    assert "N/A" in page.select_one('[data-question="3"]').text
    assert "No reported GPA" in page.select_one('[data-question="10"]').text
