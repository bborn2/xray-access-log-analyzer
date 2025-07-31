import gspread
from google.oauth2.service_account import Credentials


def update_google_sheet(date, count):

    creds = Credentials.from_service_account_file("service_account.json", scopes=[
        "https://www.googleapis.com/auth/spreadsheets"
    ])
    client = gspread.authorize(creds)

    spreadsheet_id = "1YYouPIdoqMbcHXjI-ZgPGkLS9-cju29UulVYwrjL3V0"  # 这是你表格的ID
    spreadsheet = client.open_by_key(spreadsheet_id)

    sheet = spreadsheet.sheet1  # 默认第一个工作表

    key = date  # 用第一列作为唯一标识

    # 读取所有行
    all_values = sheet.get_all_values()

    # 查找是否已存在
    found = False
    for idx, row in enumerate(all_values):
        if len(row) > 0 and row[0] == key:

            sheet.update(
                values=[[date, count]],
                range_name=f"A{idx+1}",
                value_input_option="USER_ENTERED"
            )

            found = True
            break

    # 如果未找到，则追加
    if not found:
        sheet.append_row([date, count], value_input_option="USER_ENTERED")

if __name__ == "__main__":

    update_google_sheet("2025/8/1", 233)