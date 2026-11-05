import pandas as pd
import plotly.express as px
import streamlit as st
from database.db import init_db, query_df, execute
from database.seed import seed
from modules.financial_model import gross_margin, ebitda, runway_months, vc_return, irr_from_dates
from modules.overlap_detector import detect_overlaps
from modules.efficiency_analyzer import estimate_monthly_savings
from modules.ai_research import generate_research
from utils.excel import build_finance_template
from utils.formatting import money, pct

st.set_page_config(page_title="VentureOS | Investment Intelligence", page_icon="📈", layout="wide")
init_db()
seed()

st.markdown("""
<style>
.block-container {max-width:1450px;padding-top:1.5rem}
[data-testid="stMetric"] {background:#F3F6F7;border:1px solid #E3E8ED;padding:12px;border-radius:9px}
</style>
""", unsafe_allow_html=True)
st.title("VentureOS")
st.caption("Investment Intelligence + AI Operations | Independent portfolio MVP")
st.info("Demo environment: seeded companies, metrics, agents, and assumptions are synthetic. Do not enter confidential information.")

companies = query_df("SELECT * FROM companies ORDER BY name")
metrics = query_df("SELECT fm.*, c.name AS company_name FROM financial_metrics fm JOIN companies c USING(company_id)")
agents = query_df("SELECT * FROM agents ORDER BY name")

tabs = st.tabs(["Overview","Deal Flow","Company Analysis","Financial Modeling","AI Research","AI Operations","Optimization","Excel & Data"])

with tabs[0]:
    st.subheader("Investment and operations overview")
    active = int(companies["pipeline_status"].isin(["Initial Screening","Under Evaluation","Due Diligence","Investment Committee"]).sum()) if not companies.empty else 0
    overlaps = detect_overlaps(agents.fillna("").to_dict("records"),.25) if len(agents)>1 else []
    hours = sum(estimate_monthly_savings(r.frequency_per_month,r.manual_minutes,r.automated_minutes)["hours_saved_monthly"] for r in agents.itertuples()) if not agents.empty else 0
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Startups tracked",len(companies)); c2.metric("Active evaluations",active); c3.metric("AI agents registered",len(agents)); c4.metric("Potential overlaps",len(overlaps))
    left,right=st.columns(2)
    with left:
        st.markdown("**Pipeline by stage**")
        if not companies.empty:
            counts=companies.groupby("pipeline_status").size().reset_index(name="Companies")
            st.plotly_chart(px.funnel(counts,x="Companies",y="pipeline_status"),use_container_width=True)
    with right:
        st.markdown("**Companies by industry**")
        if not companies.empty:
            counts=companies.groupby("industry").size().reset_index(name="Companies")
            st.plotly_chart(px.pie(counts,names="industry",values="Companies",hole=.5),use_container_width=True)
    st.metric("Estimated monthly hours saved across registered workflows",f"{hours:.1f} hours")
    st.caption("Time savings are calculated from illustrative or user-entered workflow assumptions, not independently audited results.")

with tabs[1]:
    st.subheader("Deal flow")
    with st.form("new_company"):
        c1,c2=st.columns(2)
        name=c1.text_input("Company name")
        industry=c2.selectbox("Industry",["Enterprise Software","Fintech","Healthcare","Hardware","Climate Tech","Cybersecurity","Logistics","Education","Other"])
        stage=c1.selectbox("Funding stage",["Pre-seed","Seed","Series A","Series B","Series C+"])
        location=c2.text_input("Headquarters")
        model=c1.selectbox("Business model",["B2B SaaS","B2C","Marketplace","Usage-based","Transaction-based","Hardware + SaaS","Licensing","Other"])
        description=c2.text_area("Company description")
        source=c1.selectbox("Data type",["User-entered","Public source","Illustrative"])
        if st.form_submit_button("Add company",type="primary"):
            if name.strip():
                execute("INSERT INTO companies(name,industry,stage,location,business_model,description,source_type) VALUES(?,?,?,?,?,?,?)",(name.strip(),industry,stage,location,model,description,source))
                st.success("Company added."); st.rerun()
            else: st.error("Enter a company name.")
    if not companies.empty:
        q=st.text_input("Search pipeline")
        view=companies[companies.name.str.contains(q,case=False,na=False)] if q else companies
        st.dataframe(view[["name","industry","stage","location","business_model","pipeline_status","source_type"]],use_container_width=True,hide_index=True)
        selected=st.selectbox("Update pipeline stage",view.name.tolist())
        status=st.selectbox("New stage",["New","Initial Screening","Under Evaluation","Due Diligence","Investment Committee","Passed / Archived"])
        if st.button("Save stage"):
            cid=int(view.loc[view.name==selected,"company_id"].iloc[0])
            execute("UPDATE companies SET pipeline_status=?,updated_at=CURRENT_TIMESTAMP WHERE company_id=?",(status,cid))
            st.rerun()
        st.download_button("Export company list",view.to_csv(index=False).encode(),"ventureos_companies.csv","text/csv")

with tabs[2]:
    st.subheader("Company analysis")
    if companies.empty: st.info("Add a company in Deal Flow.")
    else:
        selected=st.selectbox("Select company",companies.name.tolist(),key="company_analysis")
        co=companies[companies.name==selected].iloc[0]
        c1,c2,c3=st.columns(3)
        c1.metric("Industry",co.industry); c2.metric("Stage",co.stage); c3.metric("Pipeline",co.pipeline_status)
        st.write(co.description or "No description supplied.")
        fm=metrics[metrics.company_id==co.company_id]
        if not fm.empty:
            st.dataframe(fm[["period","revenue","cogs","operating_income","ebitda","cash_balance","monthly_net_burn","customer_count","source_type"]],use_container_width=True,hide_index=True)
        st.caption("Financial and company data are illustrative unless marked otherwise.")

with tabs[3]:
    st.subheader("Financial modeling")
    st.markdown("**Operating metrics**")
    c1,c2,c3=st.columns(3)
    revenue=c1.number_input("Revenue ($)",min_value=0.0,value=1200000.0,step=50000.0)
    cogs=c2.number_input("COGS ($)",min_value=0.0,value=420000.0,step=25000.0)
    operating=c3.number_input("Operating income ($)",value=-216000.0,step=10000.0)
    da=st.number_input("Depreciation & amortization ($)",min_value=0.0,value=36000.0,step=5000.0)
    cash=st.number_input("Cash balance ($)",min_value=0.0,value=780000.0,step=25000.0)
    burn=st.number_input("Monthly net burn ($)",min_value=0.0,value=30000.0,step=2500.0)
    a,b,c=st.columns(3)
    a.metric("Gross margin",pct(gross_margin(revenue,cogs)))
    e=ebitda(operating,da)
    b.metric("EBITDA",money(e))
    runway=runway_months(cash,burn)
    c.metric("Cash runway","Cash-flow positive" if runway==float("inf") else f"{runway:.1f} months")
    st.divider()
    st.markdown("**Venture return model**")
    x1,x2,x3=st.columns(3)
    investment=x1.number_input("Investment amount ($)",min_value=1.0,value=2000000.0,step=100000.0)
    pre=x2.number_input("Pre-money valuation ($)",min_value=0.0,value=8000000.0,step=500000.0)
    exitv=x3.number_input("Exit valuation ($)",min_value=0.0,value=100000000.0,step=1000000.0)
    d1,d2=st.columns(2)
    dilution1=d1.slider("Future round 1 dilution",0.0,.8,.15,.01)
    dilution2=d2.slider("Future round 2 dilution",0.0,.8,.15,.01)
    result=vc_return(investment,pre,exitv,[dilution1,dilution2])
    a,b,c,d=st.columns(4)
    a.metric("Post-money valuation",money(result["post_money_valuation"]))
    b.metric("Initial ownership",pct(result["initial_ownership"]))
    c.metric("Exit ownership",pct(result["exit_ownership"]))
    d.metric("MOIC",f'{result["moic"]:.2f}x')
    st.metric("Exit proceeds",money(result["exit_proceeds"]))
    years=st.number_input("Holding period (years)",min_value=.5,value=5.0,step=.5)
    irr=irr_from_dates(investment,result["exit_proceeds"],years)
    st.metric("Simplified annualized IRR",pct(irr))
    st.caption("Simplified illustrative model. Excludes liquidation preferences, fees, carry, option pools, and fund-level cash flows.")

with tabs[4]:
    st.subheader("AI research assistant")
    st.write("Drafts a structured research outline from information you supply. It does not browse or independently verify claims.")
    company_name=st.text_input("Company to research")
    context=st.text_area("Paste company description, notes, metrics, and source excerpts",height=180)
    if st.button("Generate research draft",type="primary"):
        if company_name.strip():
            result=generate_research(company_name,context)
            st.caption(result.get("mode","Draft"))
            st.json(result)
        else: st.warning("Enter a company name.")
    st.caption("Optional OpenAI API configuration is supported through Streamlit secrets. API use may incur charges; offline mode works without a key.")

with tabs[5]:
    st.subheader("AI operations control center")
    with st.form("new_agent"):
        name=st.text_input("Agent or tool name")
        description=st.text_area("Purpose and function")
        c1,c2=st.columns(2)
        category=c1.selectbox("Category",["Company Research","Market Research","Financial Analysis","Investment Writing","Portfolio Monitoring","Administrative","Other"])
        owner=c2.text_input("Owner",value="Unassigned")
        inputs=st.text_input("Inputs")
        outputs=st.text_input("Outputs")
        frequency=st.number_input("Runs per month",min_value=0.0,value=20.0)
        cost=st.number_input("Monthly tool cost ($)",min_value=0.0,value=0.0)
        manual=st.number_input("Manual minutes per task",min_value=0.0,value=30.0)
        automated=st.number_input("Automated minutes per task",min_value=0.0,value=5.0)
        if st.form_submit_button("Register agent"):
            if name.strip() and description.strip():
                execute("INSERT INTO agents(name,description,category,owner,inputs,outputs,frequency_per_month,monthly_cost,manual_minutes,automated_minutes,source_type) VALUES(?,?,?,?,?,?,?,?,?,?, 'User-entered')",(name,description,category,owner,inputs,outputs,frequency,cost,manual,automated))
                st.success("Agent registered."); st.rerun()
            else: st.error("Name and purpose are required.")
    current=query_df("SELECT * FROM agents ORDER BY name")
    if not current.empty:
        st.dataframe(current[["name","category","owner","frequency_per_month","monthly_cost","status","source_type"]],use_container_width=True,hide_index=True)
        rows=[]
        for r in current.itertuples():
            v=estimate_monthly_savings(r.frequency_per_month,r.manual_minutes,r.automated_minutes,r.monthly_cost,75)
            rows.append({"Agent":r.name,"Hours saved / month":round(v["hours_saved_monthly"],1),"Illustrative labor value":v["estimated_labor_value"],"Tool cost":v["monthly_tool_cost"],"Net monthly benefit":v["estimated_net_monthly_benefit"]})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
        st.caption("Labor value assumes $75/hour. Replace all assumptions with measured usage and costs before relying on estimates.")

with tabs[6]:
    st.subheader("AI workflow optimization")
    current=query_df("SELECT * FROM agents ORDER BY name")
    if len(current)<2: st.info("Register at least two agents to compare.")
    else:
        threshold=st.slider("Minimum text similarity",0.0,1.0,.25,.05)
        results=detect_overlaps(current.fillna("").to_dict("records"),threshold)
        if results:
            df=pd.DataFrame(results)
            st.dataframe(df[["agent_a","agent_b","similarity","recommendation","shared_terms","caveat"]],use_container_width=True,hide_index=True)
            st.download_button("Export overlap review",df.to_csv(index=False).encode(),"ventureos_overlap_review.csv","text/csv")
        else: st.success("No agent pairs crossed this threshold.")
        st.warning("Similarity is a text-based triage signal, not proof of duplicate functionality. Review actual users, outputs, quality, cost, security, and maintenance before consolidating.")

with tabs[7]:
    st.subheader("Excel and data workspace")
    st.write("Download the workbook to build sourced assumptions and financial cases.")
    st.download_button("Download VentureOS financial model template",build_finance_template(),"VentureOS_Financial_Model_Template.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",type="primary")
    st.divider()
    st.markdown("**Export datasets**")
    for table in ["companies","financial_metrics","agents","screenings","investment_memos","agent_overlaps"]:
        df=query_df(f"SELECT * FROM {table}")
        st.download_button(f"Export {table}.csv",df.to_csv(index=False).encode(),f"ventureos_{table}.csv","text/csv",key=f"export_{table}")
