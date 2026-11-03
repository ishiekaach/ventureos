from __future__ import annotations
import io
import math
import pandas as pd
import plotly.express as px
import streamlit as st
from database.db import init_db, query_df, execute, log_action
from database.seed import seed
from modules.financial_model import (gross_margin, ebitda, ebitda_margin, revenue_growth,
    runway_months, vc_return, irr_from_dates, calculate_comps_multiples)
from modules.overlap_detector import detect_overlaps
from modules.efficiency_analyzer import estimate_monthly_savings
from modules.ai_research import generate_research
from utils.formatting import money, pct
from utils.excel import build_finance_template

st.set_page_config(page_title="VentureOS | Investment Intelligence", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
init_db(); seed()

st.markdown("""
<style>
:root { --navy:#14243A; --sage:#83A99A; }
.block-container {padding-top:1.5rem; padding-bottom:2.5rem; max-width:1500px;}
[data-testid="stSidebar"] {background:#14243A;}
[data-testid="stSidebar"] * {color:#F3F6F8 !important;}
[data-testid="stMetric"] {background:#F4F6F8; border:1px solid #E3E8ED; padding:14px 16px; border-radius:10px;}
[data-testid="stMetricValue"] {color:#14243A;}
div.stButton > button[kind="primary"] {background:#426C60; border-color:#426C60;}
.small-muted {color:#667085;font-size:0.82rem;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("# VentureOS")
    st.caption("INVESTMENT INTELLIGENCE + AI OPERATIONS")
    st.divider()
    page = st.radio("WORKSPACE", ["Overview", "Deal Flow", "Company Analysis", "Financial Modeling", "AI Research", "AI Operations", "Optimization", "Excel & Data"], label_visibility="visible")
    st.divider()
    st.caption("DEMO ENVIRONMENT")
    st.caption("Synthetic data is labeled throughout. No live fund or private-company data is connected.")
    st.caption("Version 0.1.0 · Portfolio MVP")

companies = query_df("SELECT * FROM companies ORDER BY name")
metrics = query_df("SELECT fm.*, c.name AS company_name, c.industry FROM financial_metrics fm JOIN companies c USING(company_id)")
agents = query_df("SELECT * FROM agents ORDER BY name")


def header(title, subtitle):
    st.title(title)
    st.caption(subtitle)


def metric_card(label, value, help_text=None):
    st.metric(label, value, help=help_text)


def overview():
    header("Investment & Operations Overview", "A unified view of the startup pipeline and AI workflow infrastructure.")
    pipeline = companies["pipeline_status"].value_counts() if not companies.empty else pd.Series(dtype=int)
    active = int(companies["pipeline_status"].isin(["Initial Screening", "Under Evaluation", "Due Diligence", "Investment Committee"]).sum()) if not companies.empty else 0
    overlaps = detect_overlaps(agents.fillna("").to_dict("records"), 0.25) if not agents.empty else []
    hours = 0.0
    if not agents.empty:
        for r in agents.to_dict("records"):
            hours += estimate_monthly_savings(r["frequency_per_month"], r["manual_minutes"], r["automated_minutes"])["hours_saved_monthly"]
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Startups tracked", f"{len(companies):,}")
    c2.metric("Active evaluations", f"{active:,}")
    c3.metric("AI agents registered", f"{len(agents):,}")
    c4.metric("Potential overlaps", f"{len(overlaps):,}")
    st.markdown(" ")
    left,right = st.columns([1.15,1])
    with left:
        st.subheader("Startup pipeline")
        if not pipeline.empty:
            p = pipeline.rename_axis("Stage").reset_index(name="Companies")
            fig = px.funnel(p, x="Companies", y="Stage", color_discrete_sequence=["#83A99A"])
            fig.update_layout(height=330, margin=dict(l=10,r=10,t=15,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Add companies in Deal Flow to populate the pipeline.")
    with right:
        st.subheader("Startup mix by industry")
        if not companies.empty:
            counts = companies.groupby("industry").size().reset_index(name="Companies")
            fig = px.pie(counts, names="industry", values="Companies", hole=.58, color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(height=330, margin=dict(l=10,r=10,t=15,b=10), legend_title_text="")
            st.plotly_chart(fig, use_container_width=True)
    st.subheader("AI operations snapshot")
    a,b,c = st.columns(3)
    a.metric("Estimated monthly hours saved", f"{hours:,.1f}h", help="Based on illustrative frequency and time assumptions entered for each agent.")
    b.metric("Agent categories", f"{agents['category'].nunique() if not agents.empty else 0}")
    c.metric("Active agents", f"{int((agents['status']=='Active').sum()) if not agents.empty else 0}")
    st.caption("All seeded companies, financial figures, agents, and efficiency assumptions are synthetic demonstration data.")


def deal_flow():
    header("Deal Flow", "Source, organize, and screen early-stage companies. Screening is decision support, not an automated investment decision.")
    with st.expander("＋ Add a startup", expanded=False):
        with st.form("add_company"):
            c1,c2 = st.columns(2)
            name = c1.text_input("Company name *")
            industry = c2.selectbox("Industry", ["Enterprise Software","Fintech","Healthcare","Hardware","Climate Tech","Cybersecurity","Logistics","Education","Agriculture","Advanced Materials","Other"])
            stage = c1.selectbox("Funding stage", ["Pre-seed","Seed","Series A","Series B","Series C+"])
            location = c2.text_input("Headquarters")
            business_model = c1.selectbox("Business model", ["B2B SaaS","B2C","Marketplace","Usage-based","Transaction-based","Hardware + SaaS","Licensing","Other"])
            website = c2.text_input("Website")
            founded_year = c1.number_input("Founded year", min_value=1900, max_value=2100, value=2025)
            employees = c2.number_input("Employee count", min_value=0, max_value=1_000_000, value=5)
            description = st.text_area("Company description")
            source_type = st.selectbox("Data type", ["User-entered","Public source","Illustrative"])
            submitted = st.form_submit_button("Add company", type="primary")
            if submitted:
                if not name.strip(): st.error("Company name is required.")
                else:
                    try:
                        cid = execute("INSERT INTO companies(name,industry,stage,location,business_model,website,founded_year,employee_count,description,source_type) VALUES(?,?,?,?,?,?,?,?,?,?)", (name.strip(),industry,stage,location,business_model,website,int(founded_year),int(employees),description,source_type))
                        log_action("company", cid, "created", name)
                        st.success(f"Added {name}."); st.rerun()
                    except Exception as e: st.error(f"Could not add company: {e}")
    q1,q2,q3 = st.columns([1.3,1,1])
    search = q1.text_input("Search companies")
    industries = ["All"] + sorted(companies["industry"].dropna().unique().tolist()) if not companies.empty else ["All"]
    selected_industry = q2.selectbox("Industry", industries)
    stages = ["All","Pre-seed","Seed","Series A","Series B","Series C+"]
    selected_stage = q3.selectbox("Funding stage", stages)
    filtered = companies.copy()
    if search: filtered = filtered[filtered["name"].str.contains(search, case=False, na=False)]
    if selected_industry != "All": filtered = filtered[filtered["industry"] == selected_industry]
    if selected_stage != "All": filtered = filtered[filtered["stage"] == selected_stage]
    st.caption(f"Showing {len(filtered)} of {len(companies)} companies")
    display_cols = ["name","industry","stage","location","business_model","pipeline_status","source_type"]
    edited = st.data_editor(filtered[display_cols], use_container_width=True, hide_index=True, disabled=["name","industry","stage","location","business_model","source_type"], key="deal_editor")
    if not filtered.empty:
        selected_name = st.selectbox("Update pipeline stage for", filtered["name"].tolist())
        selected_status = st.selectbox("New stage", ["New","Initial Screening","Under Evaluation","Due Diligence","Investment Committee","Passed / Archived"])
        if st.button("Save pipeline stage"):
            cid = int(filtered.loc[filtered.name == selected_name,"company_id"].iloc[0])
            execute("UPDATE companies SET pipeline_status=?, updated_at=CURRENT_TIMESTAMP WHERE company_id=?", (selected_status,cid))
            log_action("company",cid,"pipeline_updated",selected_status); st.success("Pipeline updated."); st.rerun()
    st.download_button("Export company list (CSV)", filtered.to_csv(index=False).encode(), "ventureos_companies.csv", "text/csv")


def company_analysis():
    header("Company Analysis", "Review business models, available financial data, investment context, and open diligence questions.")
    if companies.empty: st.info("Add a company in Deal Flow first."); return
    name = st.selectbox("Select company", companies.name.tolist(), key="analysis_company")
    co = companies[companies.name == name].iloc[0]
    st.subheader(name)
    a,b,c,d = st.columns(4)
    a.metric("Industry", co.industry); b.metric("Stage", co.stage); c.metric("Headquarters", co.location or "Not supplied"); d.metric("Pipeline", co.pipeline_status)
    st.write(co.description or "No company description has been entered.")
    fm = metrics[metrics.company_id == co.company_id].sort_values("period")
    if not fm.empty:
        st.subheader("Financial snapshot")
        show = fm[["period","revenue","ebitda","cash_balance","monthly_net_burn","customer_count"]].copy()
        show.columns = ["Period","Revenue","EBITDA","Cash balance","Monthly net burn","Customers"]
        st.dataframe(show, use_container_width=True, hide_index=True)
        if len(fm) >= 2:
            growth = revenue_growth(float(fm.iloc[-1].revenue), float(fm.iloc[-2].revenue))
            st.metric("Revenue growth vs. prior period", pct(growth))
    else: st.info("No financial metrics recorded. Add them through Excel & Data.")
    st.subheader("Investment thesis and diligence")
    with st.form("screening_form"):
        score = st.slider("Preliminary thesis fit (1–5)",1,5,3)
        decision = st.selectbox("Screening disposition",["Needs review","Advance","Pass","Watchlist"])
        thesis = st.text_area("Investment thesis")
        notes = st.text_area("Risks, evidence, and open questions")
        if st.form_submit_button("Save screening assessment", type="primary"):
            execute("INSERT INTO screenings(company_id,score,thesis,decision,notes) VALUES(?,?,?,?,?)",(int(co.company_id),score,thesis,decision,notes))
            log_action("company",int(co.company_id),"screening_saved",decision); st.success("Assessment saved.")
    history = query_df("SELECT score, decision, thesis, notes, screening_date FROM screenings WHERE company_id=? ORDER BY screening_date DESC",(int(co.company_id),))
    if not history.empty:
        st.subheader("Screening history"); st.dataframe(history,use_container_width=True,hide_index=True)


def financial_modeling():
    header("Financial Modeling", "Transparent, assumption-driven analysis. Outputs depend on user-entered inputs and are not investment advice.")
    tab1,tab2,tab3,tab4 = st.tabs(["Operating metrics","VC returns","Sensitivity analysis","Comparable companies"])
    with tab1:
        st.subheader("Operating metrics calculator")
        c1,c2,c3 = st.columns(3)
        revenue = c1.number_input("Revenue ($)",min_value=0.0,value=5_000_000.0,step=100_000.0,format="%.0f")
        cogs = c2.number_input("COGS ($)",min_value=0.0,value=2_000_000.0,step=100_000.0,format="%.0f")
        op_income = c3.number_input("Operating income ($)",value=-500_000.0,step=50_000.0,format="%.0f")
        c4,c5,c6 = st.columns(3)
        da = c4.number_input("D&A ($)",min_value=0.0,value=100_000.0,step=10_000.0,format="%.0f")
        cash = c5.number_input("Cash balance ($)",min_value=0.0,value=2_000_000.0,step=100_000.0,format="%.0f")
        burn = c6.number_input("Monthly net burn ($)",value=150_000.0,step=10_000.0,format="%.0f")
        gp = revenue-cogs; ebitda_value = ebitda(op_income,da); gm = gross_margin(revenue,cogs); em = ebitda_margin(ebitda_value,revenue); runway = runway_months(cash,burn)
        x1,x2,x3,x4 = st.columns(4)
        x1.metric("Gross profit",money(gp)); x2.metric("Gross margin",pct(gm)); x3.metric("EBITDA",money(ebitda_value)); x4.metric("EBITDA margin",pct(em))
        st.metric("Cash runway", "Cash-flow positive / no burn" if runway == math.inf else (f"{runway:.1f} months" if runway is not None else "N/A"))
        st.caption("These are simplified operating metrics. Confirm accounting definitions and period consistency before using in an investment analysis.")
    with tab2:
        st.subheader("Venture return model")
        c1,c2,c3 = st.columns(3)
        invest = c1.number_input("Initial investment ($)",min_value=1.0,value=2_000_000.0,step=100_000.0,format="%.0f",key="vc_inv")
        premoney = c2.number_input("Pre-money valuation ($)",min_value=0.0,value=8_000_000.0,step=500_000.0,format="%.0f",key="vc_pre")
        exitval = c3.number_input("Exit valuation ($)",min_value=0.0,value=100_000_000.0,step=5_000_000.0,format="%.0f",key="vc_exit")
        d1,d2,d3 = st.columns(3)
        dil1 = d1.slider("Round 1 dilution",0,80,15,key="dil1")/100
        dil2 = d2.slider("Round 2 dilution",0,80,15,key="dil2")/100
        dil3 = d3.slider("Round 3 dilution",0,80,0,key="dil3")/100
        result = vc_return(invest,premoney,exitval,[dil1,dil2,dil3])
        a,b,c,d = st.columns(4)
        a.metric("Post-money valuation",money(result["post_money_valuation"]))
        b.metric("Initial ownership",pct(result["initial_ownership"]))
        c.metric("Exit ownership",pct(result["exit_ownership"]))
        d.metric("Exit proceeds",money(result["exit_proceeds"]))
        st.metric("Gross MOIC",f"{result['moic']:.2f}x")
        years = st.number_input("Holding period (years)",min_value=0.25,max_value=30.0,value=5.0,step=0.25)
        irr = irr_from_dates(invest,result["exit_proceeds"],years)
        st.metric("Illustrative annualized IRR",pct(irr))
        st.caption("Simplified single-investment model. Does not account for fees, carry, reserves, follow-on investments, liquidation preferences, or complex cap-table mechanics.")
    with tab3:
        st.subheader("MOIC sensitivity")
        invest_s = st.number_input("Investment amount ($)",min_value=1.0,value=2_000_000.0,step=100_000.0,key="sens_inv")
        pre_s = st.number_input("Pre-money valuation ($)",min_value=0.0,value=8_000_000.0,step=500_000.0,key="sens_pre")
        initial = invest_s/(invest_s+pre_s) if invest_s+pre_s else 0
        exits = [25_000_000,50_000_000,100_000_000,150_000_000,250_000_000]
        dilutions = [0.1,0.2,0.3,0.4,0.5]
        table = pd.DataFrame({f"{d:.0%} dilution": [initial*(1-d)*x/invest_s for x in exits] for d in dilutions}, index=[money(x) for x in exits])
        table.index.name = "Exit valuation"
        st.dataframe(table.style.format("{:.2f}x"),use_container_width=True)
        fig = px.imshow(table, text_auto=".2f", aspect="auto", color_continuous_scale="Tealgrn", labels=dict(x="Total dilution",y="Exit valuation",color="MOIC"))
        st.plotly_chart(fig,use_container_width=True)
    with tab4:
        st.subheader("Comparable company analysis")
        st.caption("Enter public comparable company data in the Excel template, then import it in Excel & Data.")
        comps = query_df("SELECT * FROM comps") if table_exists("comps") else pd.DataFrame()
        if comps.empty:
            st.info("No comparable-company dataset is loaded yet. Use the downloadable Excel template to enter sourced data.")
        else:
            calc = calculate_comps_multiples(comps)
            st.dataframe(calc,use_container_width=True,hide_index=True)
            st.write("Median EV / Revenue:", f"{calc.ev_revenue.median():.2f}x")
            st.write("Median EV / EBITDA:", f"{calc.ev_ebitda.median():.2f}x")


def table_exists(name):
    return not query_df("SELECT name FROM sqlite_master WHERE type='table' AND name=?",(name,)).empty


def ai_research():
    header("AI Research Assistant", "Draft structured company research from information you provide. This tool does not independently browse or verify claims.")
    if companies.empty: st.info("Add a company first."); return
    name = st.selectbox("Company",companies.name.tolist(),key="research_company")
    co = companies[companies.name == name].iloc[0]
    context = st.text_area("Paste company information, notes, or sourced excerpts",height=220,placeholder="Paste only information you are permitted to use. Include source URLs in the text where possible.")
    if st.button("Generate research draft",type="primary"):
        if not context.strip(): st.warning("Provide company context before generating a research draft.")
        else:
            with st.spinner("Preparing research draft..."):
                result = generate_research(name,context)
            st.session_state["research_result"] = result
            st.session_state["research_context"] = context
    result = st.session_state.get("research_result")
    if result:
        st.info(result.get("mode","Draft"))
        st.subheader("Research output")
        for key,value in result.items():
            if key == "mode": continue
            st.markdown(f"**{key.replace('_',' ').title()}**")
            if isinstance(value,list):
                for item in value: st.markdown(f"- {item}")
            else: st.write(value)
        content = "# Investment Research Draft\n\n" + "\n\n".join(f"## {k.replace('_',' ').title()}\n{v if isinstance(v,str) else chr(10).join('- '+str(x) for x in v)}" for k,v in result.items() if k != "mode")
        st.download_button("Download research draft (Markdown)",content.encode(),f"{name.lower().replace(' ','_')}_research.md","text/markdown")
        if st.button("Save memo to company record"):
            execute("INSERT INTO investment_memos(company_id,title,content,status) VALUES(?,?,?,'Draft')",(int(co.company_id),f"{name} Research Draft",content))
            st.success("Memo saved to the company record.")


def ai_operations():
    header("AI Operations Control Center", "A shared registry for understanding which AI tools exist, who uses them, and where workflows may overlap.")
    with st.expander("＋ Register an AI agent",expanded=False):
        with st.form("agent_form"):
            c1,c2 = st.columns(2)
            name = c1.text_input("Agent name *")
            category = c2.selectbox("Category",["Company Research","Market Research","Pitch Analysis","Investment Writing","Financial Analysis","Founder Research","Portfolio Monitoring","Administrative","Other"])
            description = st.text_area("Purpose and functionality *")
            owner = c1.text_input("Owner",value="Unassigned")
            model = c2.text_input("Model / technology",value="Not specified")
            inputs = c1.text_area("Inputs",placeholder="Company URL, pitch deck, financial statements...")
            outputs = c2.text_area("Outputs",placeholder="Research brief, extracted metrics...")
            f1,f2,f3,f4 = st.columns(4)
            freq = f1.number_input("Uses per month",min_value=0.0,value=20.0)
            cost = f2.number_input("Monthly cost ($)",min_value=0.0,value=0.0)
            manual = f3.number_input("Manual minutes per task",min_value=0.0,value=30.0)
            automated = f4.number_input("Automated minutes per task",min_value=0.0,value=5.0)
            status = st.selectbox("Status",["Active","Testing","Deprecated"])
            source = st.selectbox("Data type",["User-entered","Illustrative"])
            if st.form_submit_button("Register agent",type="primary"):
                if not name.strip() or not description.strip(): st.error("Name and purpose are required.")
                else:
                    try:
                        aid=execute("INSERT INTO agents(name,description,category,owner,inputs,outputs,model_name,frequency_per_month,monthly_cost,manual_minutes,automated_minutes,status,source_type) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(name,description,category,owner,inputs,outputs,model,freq,cost,manual,automated,status,source))
                        log_action("agent",aid,"created",name); st.success("Agent registered."); st.rerun()
                    except Exception as e: st.error(f"Could not register agent: {e}")
    agents_now = query_df("SELECT * FROM agents ORDER BY name")
    st.subheader("Agent registry")
    if not agents_now.empty:
        cols=["name","category","owner","model_name","frequency_per_month","monthly_cost","status","source_type"]
        st.dataframe(agents_now[cols],use_container_width=True,hide_index=True)
        selected = st.selectbox("Inspect agent",agents_now.name.tolist())
        ag=agents_now[agents_now.name==selected].iloc[0]
        st.write(ag.description)
        a,b,c = st.columns(3)
        estimate=estimate_monthly_savings(ag.frequency_per_month,ag.manual_minutes,ag.automated_minutes,ag.monthly_cost,75)
        a.metric("Estimated hours saved / month",f"{estimate['hours_saved_monthly']:.1f}")
        b.metric("Estimated labor value",money(estimate["estimated_labor_value"]))
        c.metric("Estimated net benefit",money(estimate["estimated_net_monthly_benefit"]))
        st.caption("Labor value assumes an illustrative $75/hour rate. Change assumptions in the underlying agent record or Excel workflow before relying on the estimate.")
    st.subheader("Workflow inventory by category")
    if not agents_now.empty:
        counts=agents_now.groupby("category").size().reset_index(name="Agents")
        fig=px.bar(counts,x="category",y="Agents",color_discrete_sequence=["#83A99A"])
        fig.update_layout(xaxis_title="",yaxis_title="Number of agents",height=300)
        st.plotly_chart(fig,use_container_width=True)


def optimization():
    header("AI Workflow Optimization", "Identify possible overlap and prioritize human-reviewed workflow improvements.")
    agents_now=query_df("SELECT * FROM agents ORDER BY name")
    if len(agents_now)<2: st.info("Register at least two agents to compare workflows."); return
    threshold=st.slider("Minimum similarity threshold",0.0,1.0,0.25,0.05,help="Lower thresholds show more possible overlaps. Similarity is based on text, not actual performance.")
    overlaps=detect_overlaps(agents_now.fillna("").to_dict("records"),threshold)
    if not overlaps: st.success("No pairs crossed the selected threshold.")
    else:
        st.metric("Potential overlapping pairs",len(overlaps))
        out=pd.DataFrame(overlaps)
        out["similarity_pct"]=out["similarity"].map(lambda x:f"{x:.0%}")
        st.dataframe(out[["agent_a","agent_b","similarity_pct","recommendation","shared_terms","caveat"]],use_container_width=True,hide_index=True)
        st.download_button("Export overlap review (CSV)",out.to_csv(index=False).encode(),"ventureos_agent_overlap_review.csv","text/csv")
        st.subheader("Review a recommendation")
        pair_options=[f"{x['agent_a']}  ↔  {x['agent_b']}" for x in overlaps]
        chosen=st.selectbox("Agent pair",pair_options)
        rec=overlaps[pair_options.index(chosen)]
        st.write(f"**Similarity score:** {rec['similarity']:.1%}")
        st.write("**Shared terms:** " + (", ".join(rec["shared_terms"]) or "No obvious shared terms"))
        decision=st.selectbox("Human review outcome",["Investigate further","Retain both","Consolidate","Retire one","Improve functionality"])
        rationale=st.text_area("Reasoning / evidence")
        if st.button("Save human review",type="primary"):
            ids=query_df("SELECT agent_id,name FROM agents WHERE name IN (?,?)",(rec["agent_a"],rec["agent_b"]))
            ids=ids.sort_values("agent_id").agent_id.tolist()
            execute("INSERT INTO agent_overlaps(agent_a,agent_b,similarity,explanation,recommendation,reviewed) VALUES(?,?,?,?,?,1) ON CONFLICT(agent_a,agent_b) DO UPDATE SET similarity=excluded.similarity, explanation=excluded.explanation, recommendation=excluded.recommendation, reviewed=1",(ids[0],ids[1],rec["similarity"],rationale,decision))
            st.success("Human review saved.")
    st.warning("A high text-similarity score is only a lead for investigation. Confirm actual use cases, outputs, users, quality, security, and maintenance requirements before consolidating tools.")


def excel_data():
    header("Excel & Data Workspace", "Use Excel for assumptions and financial inputs, then import structured worksheets into VentureOS.")
    st.subheader("Download financial modeling workbook")
    st.write("The workbook includes Companies, Financials, Comps, and VC Returns tabs. Replace illustrative rows with your assumptions and clearly label sources.")
    st.download_button("Download VentureOS Excel template",build_finance_template(),"VentureOS_Financial_Model_Template.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",type="primary")
    st.divider(); st.subheader("Import financial metrics from Excel")
    upload=st.file_uploader("Upload completed workbook (.xlsx)",type=["xlsx"])
    if upload:
        try:
            xls=pd.ExcelFile(upload)
            if "Financials" not in xls.sheet_names: st.error("Workbook must include a Financials worksheet.")
            else:
                df=pd.read_excel(upload,sheet_name="Financials")
                st.write("Preview",df.head(10))
                required={"Company","Period","Revenue","COGS","Operating Income","D&A","Cash Balance","Monthly Net Burn","Customers"}
                if not required.issubset(df.columns): st.error("Missing required columns: " + ", ".join(sorted(required-set(df.columns))))
                elif st.button("Import financial metrics",type="primary"):
                    imported=0; skipped=[]
                    for _,r in df.iterrows():
                        co=query_df("SELECT company_id FROM companies WHERE name=?",(str(r["Company"]),))
                        if co.empty: skipped.append(str(r["Company"])); continue
                        cid=int(co.iloc[0,0]); period=str(r["Period"])
                        values=[None if pd.isna(r[c]) else float(r[c]) for c in ["Revenue","COGS","Operating Income","D&A","Cash Balance","Monthly Net Burn","Customers"]]
                        execute("INSERT INTO financial_metrics(company_id,period,revenue,cogs,operating_income,depreciation_amortization,ebitda,cash_balance,monthly_net_burn,customer_count,source_type) VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(company_id,period) DO UPDATE SET revenue=excluded.revenue,cogs=excluded.cogs,operating_income=excluded.operating_income,depreciation_amortization=excluded.depreciation_amortization,ebitda=excluded.ebitda,cash_balance=excluded.cash_balance,monthly_net_burn=excluded.monthly_net_burn,customer_count=excluded.customer_count,source_type=excluded.source_type",(cid,period,values[0],values[1],values[2],values[3],(values[2]+(values[3] or 0)) if values[2] is not None else None,values[4],values[5],values[6],str(r.get("Source Type","User-entered"))))
                        imported+=1
                    st.success(f"Imported or updated {imported} financial records.")
                    if skipped: st.warning("Companies not found and skipped: " + ", ".join(sorted(set(skipped))))
                    st.rerun()
                if "Comps" in xls.sheet_names:
                    comps_df=pd.read_excel(upload,sheet_name="Comps")
                    required_comps={"Company","Enterprise Value","Revenue","EBITDA"}
                    if required_comps.issubset(comps_df.columns):
                        st.subheader("Comparable-company import preview")
                        st.dataframe(comps_df.head(10),use_container_width=True)
                        if st.button("Import comparable companies"):
                            for _,r in comps_df.iterrows():
                                execute("INSERT INTO comps(company_name,enterprise_value,revenue,ebitda,source_url,as_of_date,source_type) VALUES(?,?,?,?,?,?,?)",(str(r["Company"]),float(r["Enterprise Value"]) if pd.notna(r["Enterprise Value"]) else None,float(r["Revenue"]) if pd.notna(r["Revenue"]) else None,float(r["EBITDA"]) if pd.notna(r["EBITDA"]) else None,str(r.get("Source URL","")),str(r.get("As Of Date","")),str(r.get("Source Type","User-entered"))))
                            st.success(f"Imported {len(comps_df)} comparable-company rows.")
                            st.rerun()
        except Exception as e: st.error(f"Could not read workbook: {e}")
    st.divider(); st.subheader("Export current datasets")
    for table in ["companies","financial_metrics","agents","screenings","investment_memos","agent_overlaps"]:
        if table_exists(table):
            df=query_df(f"SELECT * FROM {table}")
            st.download_button(f"Export {table}.csv",df.to_csv(index=False).encode(),f"ventureos_{table}.csv","text/csv",key=f"export_{table}")

pages={"Overview":overview,"Deal Flow":deal_flow,"Company Analysis":company_analysis,"Financial Modeling":financial_modeling,"AI Research":ai_research,"AI Operations":ai_operations,"Optimization":optimization,"Excel & Data":excel_data}
pages[page]()

st.divider()
st.caption("VentureOS is an independent educational prototype. Demo data is synthetic. AI outputs are drafts, not verified diligence. Nothing in this application constitutes investment advice.")
