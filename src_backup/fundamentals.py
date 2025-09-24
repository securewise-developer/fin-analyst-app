from __future__ import annotations
from typing import Dict, Any

def compute_fundamental_ratios(raw: Dict[str, Any], sec_type: str = "equity") -> Dict[str, Any]:
    out: Dict[str, Any] = {"type": sec_type}

    if sec_type == "equity":
        def g(key):
            return raw.get(key)

        out.update(
            dict(
                pe_trailing=g("trailingPE"),
                pe_forward=g("forwardPE"),
                pb=g("priceToBook"),
                ev_ebitda=g("enterpriseToEbitda"),
                gross_margin=g("grossMargins"),
                op_margin=g("operatingMargins"),
                profit_margin=g("profitMargins"),
                roe=g("returnOnEquity"),
                rev_growth_yoy=g("revenueGrowth"),
                ebitda_margin=g("ebitdaMargins"),
                debt_to_equity=g("debtToEquity"),
                fcf=g("freeCashflow"),
                cash=g("totalCash"),
                debt=g("totalDebt"),
                beta=g("beta"),
                dividend_yield=g("dividendYield"),
            )
        )
    else:
        out.update(
            dict(
                expense_ratio=raw.get("annualReportExpenseRatio"),
                aum=raw.get("totalAssets"),
                distribution_yield=raw.get("yield"),
                category=raw.get("category"),
            )
        )

    return out
