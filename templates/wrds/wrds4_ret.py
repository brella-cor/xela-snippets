import pandas as pd
import numpy as np

EXCHCD = {"NYSE": 1, "AMEX": 2, "NASDAQ": 3}

def pull_crsp_stock_returns(
    start_date,
    end_date,
    market_cap_floor_mm=0.0,
    granularity="daily",               # daily | monthly | yearly
    exchanges=("NYSE", "AMEX", "NASDAQ"),
    permnos=None,
    include_delisting_returns=True,    # default ON
):
    granularity = granularity.lower().strip()
    exchanges = [e.upper() for e in exchanges]
    exchcds = [EXCHCD[e] for e in exchanges]

    if granularity == "daily":
        stock_table = "dseall" if include_delisting_returns else "dsf"
        names_table = "dsenames"
    elif granularity in ("monthly", "yearly"):
        stock_table = "mseall" if include_delisting_returns else "msf"
        names_table = "msenames"
    else:
        raise ValueError("granularity must be one of: daily, monthly, yearly")


    select_cols = """
        a.permno,
        a.date,
        a.ret,
        a.prc,
        a.shrout,
        a.dlret,
        ABS(a.prc) * a.shrout / 1000.0 AS mktcap_mm
    """ if include_delisting_returns else """
        a.permno,
        a.date,
        a.ret,
        a.prc,
        a.shrout,
        NULL::numeric AS dlret,
        ABS(a.prc) * a.shrout / 1000.0 AS mktcap_mm
    """

    sql = f"""
        SELECT
            {select_cols}
        FROM crsp_a_stock.{stock_table} AS a
        JOIN crsp_a_stock.{names_table} AS n
          ON a.permno = n.permno
         AND a.date BETWEEN n.namedt AND n.nameendt
        WHERE a.date BETWEEN %(start_date)s AND %(end_date)s
          AND n.exchcd = ANY(%(exchcds)s)
          AND n.shrcd IN (10, 11)
    """

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "exchcds": exchcds,
    }

    if permnos:
        sql += " AND a.permno = ANY(%(permnos)s)"
        params["permnos"] = permnos

    df = conn.raw_sql(sql, params=params, date_cols=["date"])

    if df.empty:
        return df

    df = df[df["mktcap_mm"] >= market_cap_floor_mm].copy()

    if include_delisting_returns:
        # If dlret exists, merge it into the period return
        df["adj_ret"] = df["ret"]
        has_dl = df["dlret"].notna()

        both = has_dl & df["ret"].notna()
        only_dl = has_dl & df["ret"].isna()

        df.loc[both, "adj_ret"] = (1 + df.loc[both, "ret"]) * (1 + df.loc[both, "dlret"]) - 1
        df.loc[only_dl, "adj_ret"] = df.loc[only_dl, "dlret"]
    else:
        df["adj_ret"] = df["ret"]

    if granularity == "yearly":
        df["year"] = df["date"].dt.year
        out = (
            df.dropna(subset=["adj_ret"])
              .groupby(["permno", "year"], as_index=False)
              .agg(
                  annual_ret=("adj_ret", lambda x: (1 + x).prod() - 1),
                  last_date=("date", "max"),
                  last_mktcap_mm=("mktcap_mm", "last"),
              )
              .sort_values(["permno", "year"])
              .reset_index(drop=True)
        )
        return out

    return df.sort_values(["permno", "date"]).reset_index(drop=True)