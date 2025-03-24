def generate_tally_xml(ledgers):
    tally_message = ""

    for ledger in ledgers:
        ledger_name = ledger["LedgerName"]
        group = ledger["Group"]
        opening_balance = ledger["OpeningBalance"]

        tally_message += f"""
            <TALLYMESSAGE xmlns:UDF="TallyUDF">
                <LEDGER NAME="{ledger_name}" Action="Create">
                    <NAME>{ledger_name}</NAME>
                    <PARENT>{group}</PARENT>
                    <OPENINGBALANCE>{opening_balance}</OPENINGBALANCE>
                </LEDGER>
            </TALLYMESSAGE>
        """

    return f"""
    <ENVELOPE>
        <HEADER>
            <TALLYREQUEST>Import Data</TALLYREQUEST>
        </HEADER>
        <BODY>
            <IMPORTDATA>
                <REQUESTDESC>
                    <REPORTNAME>All Masters</REPORTNAME>
                </REQUESTDESC>
                <REQUESTDATA>
                    {tally_message}
                </REQUESTDATA>
            </IMPORTDATA>
        </BODY>
    </ENVELOPE>
    """

