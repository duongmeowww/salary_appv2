import pytest

from app.utils import parse_salary_excel
from tests.conftest import build_excel


def test_parse_valid_file():
    stream = build_excel([
        ['NV001', 'Nguyễn Văn A', 1, 2024, 10000000, 1000000, 500000, 10500000],
        ['NV002', 'Trần Thị B', 1, 2024, 12000000, 0, 0, 12000000],
    ])
    records = parse_salary_excel(stream)
    assert len(records) == 2
    assert records[0]['username'] == 'NV001'
    assert records[0]['net_salary'] == 10500000.0


def test_parse_skips_empty_rows():
    stream = build_excel([
        ['NV001', 'Nguyễn Văn A', 1, 2024, 1, 0, 0, 1],
        [None, None, None, None, None, None, None, None],
    ])
    assert len(parse_salary_excel(stream)) == 1


def test_parse_missing_column():
    stream = build_excel([], columns=['Mã nhân viên', 'Họ tên'])
    with pytest.raises(ValueError, match='thiếu cột bắt buộc'):
        parse_salary_excel(stream)


def test_parse_invalid_number_reports_row():
    stream = build_excel([['NV001', 'A', 1, 2024, 'abc', 0, 0, 0]])
    with pytest.raises(ValueError, match='Dòng 2'):
        parse_salary_excel(stream)


def test_parse_invalid_month():
    stream = build_excel([['NV001', 'A', 13, 2024, 1, 0, 0, 1]])
    with pytest.raises(ValueError, match='Tháng'):
        parse_salary_excel(stream)
