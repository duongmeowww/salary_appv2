import io

from openpyxl import load_workbook

REQUIRED_COLUMNS = (
    'Mã nhân viên',
    'Họ tên',
    'Tháng',
    'Năm',
    'Lương cơ bản',
    'Phụ cấp',
    'Khấu trừ',
    'Lương thực nhận',
)


def _to_float(value, column, row_number):
    if value is None or value == '':
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f'Dòng {row_number}: cột "{column}" phải là số, nhận được "{value}".')


def _to_int(value, column, row_number, minimum, maximum):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f'Dòng {row_number}: cột "{column}" phải là số nguyên, nhận được "{value}".')
    if not minimum <= number <= maximum:
        raise ValueError(f'Dòng {row_number}: cột "{column}" phải nằm trong khoảng {minimum}-{maximum}.')
    return number


def parse_salary_excel(source):
    """Đọc bảng lương từ file Excel (đường dẫn hoặc file-like object).

    Dùng openpyxl ở chế độ read-only nên chỉ giữ từng dòng trong bộ nhớ khi duyệt.
    """
    if hasattr(source, 'read') and not hasattr(source, 'seekable'):
        # SpooledTemporaryFile (upload của Werkzeug trên Python < 3.11) không có seekable()
        source = io.BytesIO(source.read())

    workbook = load_workbook(source, read_only=True, data_only=True)
    try:
        sheet = workbook.active
        rows = sheet.iter_rows(values_only=True)
        try:
            header = next(rows)
        except StopIteration:
            raise ValueError('File Excel rỗng.')

        indexes = {}
        for position, name in enumerate(header):
            if isinstance(name, str):
                indexes.setdefault(name.strip(), position)

        missing = [column for column in REQUIRED_COLUMNS if column not in indexes]
        if missing:
            raise ValueError(f"File Excel thiếu cột bắt buộc: {', '.join(missing)}")

        records = []
        for row_number, row in enumerate(rows, start=2):
            def cell(column):
                position = indexes[column]
                return row[position] if position < len(row) else None

            username = cell('Mã nhân viên')
            if username is None or str(username).strip() == '':
                continue

            records.append({
                'username': str(username).strip(),
                'full_name': str(cell('Họ tên') or '').strip(),
                'month': _to_int(cell('Tháng'), 'Tháng', row_number, 1, 12),
                'year': _to_int(cell('Năm'), 'Năm', row_number, 1900, 2999),
                'basic_salary': _to_float(cell('Lương cơ bản'), 'Lương cơ bản', row_number),
                'allowance': _to_float(cell('Phụ cấp'), 'Phụ cấp', row_number),
                'deduction': _to_float(cell('Khấu trừ'), 'Khấu trừ', row_number),
                'net_salary': _to_float(cell('Lương thực nhận'), 'Lương thực nhận', row_number),
            })
        return records
    finally:
        workbook.close()
