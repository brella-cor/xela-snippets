import pandas as pd


EXCHANGE_MAP = {
    "NYSE": 1,
    "AMEX": 2,
    "NASDAQ": 3,
}


def pull_crsp_stocks(
    start_date,
    end_date,
    market_cap_floor,
    granularity="daily",
    exchanges=("NYSE", "AMEX", "NASDAQ"),
    permnos=None,
):
    """
    Pull CRSP stocks using CRSP Stock (Annual).

    granularity:
        - "daily"   -> dsf + dsenames
        - "monthly" -> msf + msenames
        - "yearly"  -> derived from msf by keeping last obs in each year
    """
    granularity = granularity.lower().strip()

    if granularity == "daily":
        data_table = "crsp_a_stock.dsf"
        name_table = "crsp_a_stock.dsenames"

    elif granularity == "monthly":
        data_table = "crsp_a_stock.msf"
        name_table = "crsp_a_stock.msenames"

    elif granularity == "yearly":
        data_table = "crsp_a_stock.msf"
        name_table = "crsp_a_stock.msenames"

    else:
        raise ValueError("granularity must be one of: daily, monthly, yearly")

    exchcds = [EXCHANGE_MAP[x.upper()] for x in exchanges]
    exch_clause = ",".join(str(x) for x in exchcds)

    permno_clause = ""

    if permnos is not None and len(permnos) > 0:
        permno_list = ",".join(str(int(x)) for x in permnos)
        permno_clause = f"AND a.permno IN ({permno_list})"

    sql = f"""
        SELECT
            a.permno,
            a.permco,
            a.date,
            b.ticker,
            b.comnam,
            b.exchcd,
            b.shrcd,
            a.prc,
            a.shrout,
            ABS(a.prc) * a.shrout * 1000 AS mktcap_usd
        FROM {data_table} AS a
        JOIN {name_table} AS b
          ON a.permno = b.permno
         AND a.date BETWEEN b.namedt AND b.nameendt
        WHERE a.date BETWEEN %s AND %s
          AND b.exchcd IN ({exch_clause})
          AND b.shrcd IN (10, 11)
          AND a.prc IS NOT NULL
          AND a.shrout IS NOT NULL
          AND ABS(a.prc) * a.shrout * 1000 >= %s
          {permno_clause}
        ORDER BY a.permno, a.date
    """

    df = conn.raw_sql(sql, params=[start_date, end_date, market_cap_floor])

    if granularity == "yearly" and not df.empty:
        df["year"] = pd.to_datetime(df["date"]).dt.year

        df = (
            df.sort_values(["permno", "date"])
              .groupby(["permno", "year"], as_index=False)
              .tail(1)
              .drop(columns=["year"])
              .reset_index(drop=True)
        )

    return df


crsp_prices = pull_crsp_stocks(
    start_date="2020-01-01",
    end_date="2024-12-31",
    market_cap_floor=1_000_000_000,  # USD: $1B
    granularity="monthly",          # daily / monthly / yearly
    exchanges=("NYSE", "AMEX", "NASDAQ"),
    permnos=None,                  # None = all qualifying securities
)