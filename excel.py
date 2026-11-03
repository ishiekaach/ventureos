from io import BytesIO
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

def build_finance_template():
    companies = pd.DataFrame([{"Company": "Example Startup", "Industry": "Enterprise Software", "Stage": "Seed", "Currency": "USD", "Source Type": "User-entered"}])
    financials = pd.DataFrame([{"Company": "Example Startup", "Period": "FY2025", "Revenue": 1200000, "COGS": 420000, "Operating Income": -216000, "D&A": 36000, "Cash Balance": 780000, "Monthly Net Burn": 30000, "Customers": 20, "Source Type": "Illustrative"}, {"Company": "Example Startup", "Period": "FY2026E", "Revenue": 1980000, "COGS": 693000, "Operating Income": -158400, "D&A": 79200, "Cash Balance": 480000, "Monthly Net Burn": 21600, "Customers": 35, "Source Type": "Illustrative"}])
    comps = pd.DataFrame([{"Company": "Public Comp A", "Enterprise Value": 300000000, "Revenue": 50000000, "EBITDA": 8000000, "Source URL": "", "As Of Date": "", "Source Type": "User-entered"}])
    vc = pd.DataFrame([{"Investment Amount": 2000000, "Pre-money Valuation": 8000000, "Exit Valuation": 100000000, "Dilution Round 1": 0.15, "Dilution Round 2": 0.15, "Investment Date": "2026-01-01", "Exit Date": "2031-01-01"}])
    instructions = pd.DataFrame([{"Instructions": "Replace example rows with your own assumptions. Clearly identify actual, estimated, and illustrative data. Do not treat sample values as investment advice."}])
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        instructions.to_excel(writer, sheet_name="Read Me", index=False)
        companies.to_excel(writer, sheet_name="Companies", index=False)
        financials.to_excel(writer, sheet_name="Financials", index=False)
        comps.to_excel(writer, sheet_name="Comps", index=False)
        vc.to_excel(writer, sheet_name="VC Returns", index=False)
        # Formula-driven analysis columns; Excel recalculates these when opened.
        ws = writer.book["Financials"]
        derived = ["Gross Profit", "Gross Margin", "EBITDA", "EBITDA Margin", "Revenue Growth", "Runway (months)"]
        start_col = ws.max_column + 1
        for offset, label in enumerate(derived):
            ws.cell(row=1, column=start_col + offset, value=label)
        for row in range(2, ws.max_row + 1):
            ws.cell(row=row, column=start_col, value=f'=IF(OR(C{row}="",D{row}=""),"",C{row}-D{row})')
            ws.cell(row=row, column=start_col+1, value=f'=IFERROR({get_column_letter(start_col)}{row}/C{row},"")')
            ws.cell(row=row, column=start_col+2, value=f'=IF(E{row}="","",E{row}+F{row})')
            ws.cell(row=row, column=start_col+3, value=f'=IFERROR({get_column_letter(start_col+2)}{row}/C{row},"")')
            ws.cell(row=row, column=start_col+4, value='=""' if row == 2 else f'=IF(A{row}<>A{row-1},"",IFERROR(C{row}/C{row-1}-1,""))')
            ws.cell(row=row, column=start_col+5, value=f'=IF(OR(G{row}="",H{row}=""),"",IF(H{row}<=0,"Cash-flow positive",G{row}/H{row}))')
        ws = writer.book["Comps"]
        ws.cell(row=1, column=8, value="EV / Revenue")
        ws.cell(row=1, column=9, value="EV / EBITDA")
        for row in range(2, ws.max_row + 1):
            ws.cell(row=row, column=8, value=f'=IFERROR(B{row}/C{row},"")')
            ws.cell(row=row, column=9, value=f'=IFERROR(B{row}/D{row},"")')
        ws = writer.book["VC Returns"]
        extra = ["Post-money Valuation", "Initial Ownership", "Exit Ownership", "Exit Proceeds", "MOIC", "Holding Period (Years)", "IRR"]
        for offset, label in enumerate(extra, start=8):
            ws.cell(row=1, column=offset, value=label)
        ws.cell(row=2, column=8, value="=A2+B2")
        ws.cell(row=2, column=9, value="=IFERROR(A2/H2,0)")
        ws.cell(row=2, column=10, value="=I2*(1-D2)*(1-E2)")
        ws.cell(row=2, column=11, value="=C2*J2")
        ws.cell(row=2, column=12, value="=IFERROR(K2/A2,0)")
        ws.cell(row=2, column=13, value="=IFERROR(YEAR(G2)-YEAR(F2),0)")
        ws.cell(row=2, column=14, value="=IFERROR(L2^(1/M2)-1,0)")
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor="14243A")
                cell.alignment = Alignment(vertical="center")
            for col in ws.columns:
                max_len = min(max(len(str(c.value or "")) for c in col) + 2, 34)
                ws.column_dimensions[get_column_letter(col[0].column)].width = max(14, max_len)
    output.seek(0)
    return output.getvalue()
