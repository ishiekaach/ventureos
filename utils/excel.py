from io import BytesIO
import pandas as pd
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

def build_finance_template():
    companies = pd.DataFrame([{"Company":"Example Startup","Industry":"Enterprise Software","Stage":"Seed","Source Type":"Illustrative"}])
    financials = pd.DataFrame([{"Company":"Example Startup","Period":"FY2025","Revenue":1200000,"COGS":420000,"Operating Income":-216000,"D&A":36000,"Cash Balance":780000,"Monthly Net Burn":30000,"Customers":20,"Source Type":"Illustrative"}])
    comps = pd.DataFrame([{"Company":"Public Comp A","Enterprise Value":300000000,"Revenue":50000000,"EBITDA":8000000,"Source URL":"","As Of Date":"","Source Type":"Illustrative"}])
    vc = pd.DataFrame([{"Investment Amount":2000000,"Pre-money Valuation":8000000,"Exit Valuation":100000000,"Dilution Round 1":0.15,"Dilution Round 2":0.15,"Investment Date":"2026-01-01","Exit Date":"2031-01-01"}])
    output=BytesIO()
    with pd.ExcelWriter(output,engine="openpyxl") as writer:
        companies.to_excel(writer,sheet_name="Companies",index=False)
        financials.to_excel(writer,sheet_name="Financials",index=False)
        comps.to_excel(writer,sheet_name="Comps",index=False)
        vc.to_excel(writer,sheet_name="VC Returns",index=False)
        ws=writer.book["Financials"]
        for col,label in enumerate(["Gross Profit","Gross Margin","EBITDA","EBITDA Margin","Runway (months)"],start=10):
            ws.cell(row=1,column=col,value=label)
        ws["J2"]="=C2-D2"; ws["K2"]="=IFERROR(J2/C2,0)"; ws["L2"]="=E2+F2"; ws["M2"]="=IFERROR(L2/C2,0)"; ws["N2"]="=IFERROR(G2/H2,0)"
        for ws in writer.book.worksheets:
            ws.freeze_panes="A2"; ws.auto_filter.ref=ws.dimensions
            for cell in ws[1]:
                cell.font=Font(bold=True,color="FFFFFF")
                cell.fill=PatternFill("solid",fgColor="14243A")
            for col in ws.columns:
                ws.column_dimensions[get_column_letter(col[0].column)].width=min(max(len(str(c.value or "")) for c in col)+2,32)
    output.seek(0)
    return output.getvalue()
