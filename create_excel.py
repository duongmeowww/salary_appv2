from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

# Tạo workbook
wb = Workbook()
ws = wb.active
ws.title = 'Bang luong'

# Thêm tiêu đề với Tiếng Việt
headers = ['Mã nhân viên', 'Họ tên', 'Tháng', 'Năm', 'Lương cơ bản', 'Phụ cấp', 'Khấu trừ', 'Lương thực nhận']
ws.append(headers)

# Thêm dữ liệu
data = [
    ['NV001', 'Nguyễn Văn A', 1, 2025, 10000000, 500000, 1000000, 9500000],
    ['NV002', 'Trần Thị B', 1, 2025, 12000000, 600000, 1200000, 11400000]
]

for row in data:
    ws.append(row)

# Định dạng header
header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
header_font = Font(bold=True, color='FFFFFF')

for cell in ws[1]:
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal='center', vertical='center')

# Điều chỉnh độ rộng cột
for col in ws.columns:
    max_length = 0
    for cell in col:
        if cell.value:
            max_length = max(max_length, len(str(cell.value)))
    ws.column_dimensions[cell.column_letter].width = max_length + 2

# Lưu file
wb.save('bang_luong.xlsx')
print('File bang_luong.xlsx da duoc tao thanh cong!')
