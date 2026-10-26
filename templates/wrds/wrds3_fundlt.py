import pandas as pd


def pull_compustat_stocks(
    start_date,
    end_date,
    market_cap_floor,
    granularity="daily",
    exchange_names=("NYSE", "AMEX", "NASDAQ"),
    permnos=None,
    fields=None,
):
    """
    Pull Compustat North America stock data linked to CRSP PERMNOs.

    Parameters
    ----------
    start_date, end_date : str
        Date range to pull.
    market_cap_floor : float
        Minimum market cap using the existing price * shares calculation.
    granularity : str
        "daily", "monthly", or "yearly".
        Yearly keeps the last qualifying observation per PERMNO per year.
    exchange_names : tuple/list
        Exchange names to keep.
    permnos : list[int] or None
        Restrict to these PERMNOs. None pulls all linked securities.
    fields : list[str] or None
        Output fields to return. None returns all fields in field_map.

    Notes
    -----
    Requires access to Compustat and the CRSP-Compustat link table.
    Date, exchange, and market-cap filters still apply to selected PERMNOs.
    """
    granularity = granularity.lower().strip()

    if granularity == "daily":
        data_table = "comp_na_daily_all.secd"
        price_col = "prccd"
        shares_col = "cshoc"
        year_rollup = False

    elif granularity in ("monthly", "yearly"):
        data_table = "comp_na_daily_all.secm"
        price_col = "prccm"
        shares_col = "cshom"
        year_rollup = granularity == "yearly"

    else:
        raise ValueError(
            "granularity must be one of: daily, monthly, yearly"
        )

    field_map = {
        "permno": "l.permno",
        "gvkey": "a.gvkey",
        "iid": "a.iid",
        "date": "a.datadate AS date",
        "tic": "a.tic",
        "conm": "a.conm",
        "exchg": "a.exchg",
        "tpci": "a.tpci",
        "price": f"a.{price_col} AS price",
        "shares_outstanding": (
            f"a.{shares_col} AS shares_outstanding"
        ),
        "mktcap_usd": (
            f"ABS(a.{price_col}) * a.{shares_col} AS mktcap_usd"
        ),
    }

    if fields is None:
        requested_fields = list(field_map)

    else:
        if isinstance(fields, str):
            raise TypeError(
                "fields must be a list of field names, not a string."
            )

        requested_fields = list(dict.fromkeys(fields))

        if not requested_fields:
            raise ValueError("fields must contain at least one field.")

        invalid_fields = [
            field for field in requested_fields
            if field not in field_map
        ]

        if invalid_fields:
            raise ValueError(
                f"Unknown fields: {invalid_fields}. "
                f"Available fields: {list(field_map)}"
            )

    # Include identifiers internally for duplicate checks and yearly rollup.
    query_fields = requested_fields.copy()

    for field in ("permno", "gvkey", "iid", "date"):
        if field not in query_fields:
            query_fields.append(field)

    select_clause = ",\n            ".join(
        field_map[field] for field in query_fields
    )

    exchange_names = list(exchange_names)

    if not exchange_names:
        raise ValueError(
            "exchange_names must contain at least one exchange."
        )

    exchange_placeholders = ", ".join(
        ["%s"] * len(exchange_names)
    )

    params = list(exchange_names)

    permno_clause = ""

    if permnos is not None:
        if isinstance(permnos, (str, bytes)):
            raise TypeError("permnos must be a list of integers.")

        permnos = list(dict.fromkeys(int(value) for value in permnos))

        if not permnos:
            raise ValueError(
                "permnos cannot be empty. Use None for all linked securities."
            )

        placeholders = ", ".join(["%s"] * len(permnos))
        permno_clause = f"AND lpermno IN ({placeholders})"
        params.extend(permnos)

    params.extend([start_date, end_date, market_cap_floor])

    sql = f"""
        WITH ex_codes AS (
            SELECT DISTINCT code
            FROM comp_na_daily_all.r_ex_codes
            WHERE description IN ({exchange_placeholders})
        ),
        links AS (
            SELECT DISTINCT
                gvkey,
                liid AS iid,
                lpermno AS permno,
                linkdt,
                linkenddt
            FROM crsp_a_ccm.ccmxpf_linktable
            WHERE lpermno IS NOT NULL
              AND linktype IN ('LC', 'LU')
              {permno_clause}
        )
        SELECT
            {select_clause}
        FROM {data_table} AS a
        JOIN ex_codes AS e
          ON a.exchg = e.code
        JOIN links AS l
          ON a.gvkey = l.gvkey
         AND a.iid = l.iid
         AND a.datadate BETWEEN
             COALESCE(l.linkdt, DATE '1900-01-01')
             AND COALESCE(l.linkenddt, DATE '9999-12-31')
        WHERE a.datadate BETWEEN %s AND %s
          AND a.tpci = '0'
          AND a.{price_col} IS NOT NULL
          AND a.{shares_col} IS NOT NULL
          AND ABS(a.{price_col}) * a.{shares_col} >= %s
        ORDER BY l.permno, a.datadate, a.gvkey, a.iid
    """



    df = conn.raw_sql(sql, params=params)
    
    if not df.empty:
        df["permno"] = df["permno"].astype("int64")
        df["date"] = pd.to_datetime(df["date"])

        # Overlapping link records can produce identical rows.
        df = df.drop_duplicates().reset_index(drop=True)

        if df.duplicated(["permno", "date"]).any():
            raise ValueError(
                "Multiple Compustat observations map to the same "
                "PERMNO and date. Check the CCM links before proceeding."
            )

        if year_rollup:
            df["year"] = df["date"].dt.year

            df = (
                df.sort_values(["permno", "date"])
                  .groupby(["permno", "year"], as_index=False)
                  .tail(1)
                  .drop(columns=["year"])
                  .reset_index(drop=True)
            )

    return df.loc[:, requested_fields]


# Example usage
if __name__ == "__main__":
    df = pull_compustat_stocks(
        start_date="2020-01-01",
        end_date="2024-12-31",
        market_cap_floor=1_000_000_000,
        granularity="monthly",
        exchange_names=("NYSE", "AMEX", "NASDAQ"),
        permnos=[14593, 10107],
        fields=["permno", "date", "conm", "price", "mktcap_usd"],
        # permnos=None pulls all linked securities.
        # fields=None returns all fields in field_map.
    )

    print(df.head())