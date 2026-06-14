# e2e-marqeta-simulator/frontend/iso_mapping.py
"""ISO 8583 Data Element → Marqeta JCF (JIT Common Fields) mapping defaults.

These mappings represent how the JPBOS (JPMorgan Banking OS) driven JCF
conversion translates ISO 8583 Data Elements (DEs) into the Marqeta
JIT Funding webhook / JCF fields used by the issuer processor.

Includes all primary AND secondary DEs (up to DE128) commonly used in
Visa/Mastercard authorisation, including DE55 ICC/EMV chip data.

The mapping table is editable in the Streamlit UI (session-scoped).
"""

# ──────────────────────────────────────────────────────────────────────────────
# ISO 8583 → JCF field mapping table (full set)
# ──────────────────────────────────────────────────────────────────────────────
# Keys:
#   de          – ISO 8583 Data Element number (string, e.g. "DE2")
#   iso_name    – official ISO 8583 field name
#   jcf_field   – name of the corresponding field in the simulator request / JCF
#   description – plain-English explanation of what JPBOS does with this DE
#   transform   – how the value is converted before being passed to JCF
#   category    – grouping: "primary" | "secondary" | "emv" | "merchant" | "trace"
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_ISO_JCF_MAPPING = [
    # ── Primary bitmap DEs ──────────────────────────────────────────────────
    {
        "de":          "DE2",
        "iso_name":    "Primary Account Number (PAN)",
        "jcf_field":   "pan",
        "description": "PAN → Marqeta card_token (tokenised in production)",
        "transform":   "tokenize",
        "category":    "primary",
    },
    {
        "de":          "DE3",
        "iso_name":    "Processing Code",
        "jcf_field":   "processing_code",
        "description": "6-digit code: first 2 = txn type (00=purchase, 01=withdrawal, 20=refund)",
        "transform":   "passthrough",
        "category":    "primary",
    },
    {
        "de":          "DE4",
        "iso_name":    "Amount, Transaction",
        "jcf_field":   "amount",
        "description": "Transaction amount in minor units (cents/pence) matching jit_funding.amount",
        "transform":   "passthrough",
        "category":    "primary",
    },
    {
        "de":          "DE5",
        "iso_name":    "Amount, Settlement",
        "jcf_field":   "settlement_amount",
        "description": "Settlement amount in minor units (may differ from txn amount after DCC)",
        "transform":   "passthrough",
        "category":    "primary",
    },
    {
        "de":          "DE6",
        "iso_name":    "Amount, Cardholder Billing",
        "jcf_field":   "billing_amount",
        "description": "Billed amount in cardholder home currency",
        "transform":   "passthrough",
        "category":    "primary",
    },
    {
        "de":          "DE7",
        "iso_name":    "Transmission Date & Time",
        "jcf_field":   "datetime",
        "description": "ISO 8601 UTC timestamp of transmission",
        "transform":   "format_iso8601",
        "category":    "primary",
    },
    {
        "de":          "DE11",
        "iso_name":    "System Trace Audit Number (STAN)",
        "jcf_field":   "stan",
        "description": "6-digit terminal-assigned audit number (DE11)",
        "transform":   "passthrough",
        "category":    "trace",
    },
    {
        "de":          "DE12",
        "iso_name":    "Local Transaction Time",
        "jcf_field":   "local_transaction_time",
        "description": "HHMMSS extracted from transaction datetime",
        "transform":   "extract_time",
        "category":    "trace",
    },
    {
        "de":          "DE13",
        "iso_name":    "Local Transaction Date",
        "jcf_field":   "local_transaction_date",
        "description": "MMDD local date from terminal clock",
        "transform":   "extract_date",
        "category":    "trace",
    },
    {
        "de":          "DE14",
        "iso_name":    "Expiration Date",
        "jcf_field":   "card_expiry",
        "description": "YYMM card expiry — compared against card record at issuer",
        "transform":   "passthrough",
        "category":    "primary",
    },
    {
        "de":          "DE18",
        "iso_name":    "Merchant Type (MCC)",
        "jcf_field":   "mcc",
        "description": "4-digit ISO 18245 Merchant Category Code → transaction.merchant.mcc",
        "transform":   "passthrough",
        "category":    "merchant",
    },
    {
        "de":          "DE19",
        "iso_name":    "Acquiring Institution Country Code",
        "jcf_field":   "acquiring_country",
        "description": "ISO 3166 numeric country of acquirer",
        "transform":   "numeric_to_alpha",
        "category":    "trace",
    },
    {
        "de":          "DE22",
        "iso_name":    "POS Entry Mode",
        "jcf_field":   "pos_entry_mode",
        "description": "051=chip+PIN, 071=contactless, 011=mag-stripe, 010=manual; → transaction.pos.entry_mode",
        "transform":   "passthrough",
        "category":    "primary",
    },
    {
        "de":          "DE25",
        "iso_name":    "POS Condition Code",
        "jcf_field":   "pos_condition_code",
        "description": "Identifies attended/unattended, card-present/not-present conditions",
        "transform":   "passthrough",
        "category":    "primary",
    },
    {
        "de":          "DE32",
        "iso_name":    "Acquiring Institution ID Code",
        "jcf_field":   "acquiring_institution_id",
        "description": "BIN/IIN of the acquiring bank — ties to Marqeta program funding source",
        "transform":   "passthrough",
        "category":    "trace",
    },
    {
        "de":          "DE33",
        "iso_name":    "Forwarding Institution ID Code",
        "jcf_field":   "forwarding_institution_id",
        "description": "Identifies the forwarding institution (network switch or aggregator)",
        "transform":   "passthrough",
        "category":    "trace",
    },
    {
        "de":          "DE35",
        "iso_name":    "Track 2 Equivalent Data",
        "jcf_field":   "track2_data",
        "description": "PAN + expiry + service code in track-2 format; present for mag-stripe / contactless",
        "transform":   "tokenize",
        "category":    "primary",
    },
    {
        "de":          "DE37",
        "iso_name":    "Retrieval Reference Number (RRN)",
        "jcf_field":   "rrn",
        "description": "12-character network retrieval reference (yDDDhhmm + 4 digits)",
        "transform":   "passthrough",
        "category":    "trace",
    },
    {
        "de":          "DE38",
        "iso_name":    "Authorization Code",
        "jcf_field":   "auth_code",
        "description": "6-char alphanumeric code returned on approval — echoed back to merchant",
        "transform":   "passthrough",
        "category":    "trace",
    },
    {
        "de":          "DE39",
        "iso_name":    "Response Code",
        "jcf_field":   "response_code",
        "description": "2-digit ISO 8583 response code: 00=approved, 05=declined, 51=insufficient funds",
        "transform":   "passthrough",
        "category":    "trace",
    },
    {
        "de":          "DE41",
        "iso_name":    "Card Acceptor Terminal ID",
        "jcf_field":   "terminal_id",
        "description": "8-character terminal identifier assigned by acquirer → transaction.pos.terminal_id",
        "transform":   "passthrough",
        "category":    "merchant",
    },
    {
        "de":          "DE42",
        "iso_name":    "Card Acceptor ID Code",
        "jcf_field":   "acquiring_institution_id",
        "description": "Merchant / acquirer institution identification code (15 chars)",
        "transform":   "passthrough",
        "category":    "merchant",
    },
    {
        "de":          "DE43",
        "iso_name":    "Card Acceptor Name / Location",
        "jcf_field":   "merchant_name",
        "description": "Merchant name + city + state packed as 40-char field; JPBOS splits into sub-fields",
        "transform":   "truncate_25",
        "category":    "merchant",
    },
    {
        "de":          "DE43.city",
        "iso_name":    "Card Acceptor City (sub-field of DE43)",
        "jcf_field":   "merchant_city",
        "description": "Merchant city extracted from DE43 location field → transaction.merchant.city",
        "transform":   "passthrough",
        "category":    "merchant",
    },
    {
        "de":          "DE43.state",
        "iso_name":    "Card Acceptor State (sub-field of DE43)",
        "jcf_field":   "merchant_state",
        "description": "Merchant state/region code extracted from DE43 → transaction.merchant.state",
        "transform":   "passthrough",
        "category":    "merchant",
    },
    {
        "de":          "DE43.country",
        "iso_name":    "Card Acceptor Country (sub-field of DE43)",
        "jcf_field":   "merchant_country",
        "description": "ISO 3166 alpha-3 country extracted from DE43 → transaction.merchant.country",
        "transform":   "numeric_to_alpha",
        "category":    "merchant",
    },
    {
        "de":          "DE49",
        "iso_name":    "Currency Code, Transaction",
        "jcf_field":   "currency",
        "description": "ISO 4217 numeric code: 840=USD, 978=EUR, 826=GBP, 392=JPY → jit_funding.currency_code",
        "transform":   "numeric_to_alpha",
        "category":    "primary",
    },
    {
        "de":          "DE50",
        "iso_name":    "Currency Code, Settlement",
        "jcf_field":   "settlement_currency",
        "description": "Currency in which settlement is performed (may differ from txn currency)",
        "transform":   "numeric_to_alpha",
        "category":    "primary",
    },
    # ── Secondary bitmap DEs ────────────────────────────────────────────────
    {
        "de":          "DE55",
        "iso_name":    "ICC System Related Data (EMV)",
        "jcf_field":   "icc_data",
        "description": "Full BER-TLV EMV chip data (ARQC, CDOL, ATC, TVR, etc.) from the chip card",
        "transform":   "emv_tlv_decode",
        "category":    "emv",
    },
    {
        "de":          "DE56",
        "iso_name":    "Original Data Elements",
        "jcf_field":   "original_transaction_id",
        "description": "MTI + STAN + date/time + acquiring BIN of the original transaction for reversals",
        "transform":   "passthrough",
        "category":    "secondary",
    },
    {
        "de":          "DE60",
        "iso_name":    "Additional POS Information",
        "jcf_field":   "additional_pos_info",
        "description": "Network-specific POS terminal capabilities and environment flags",
        "transform":   "passthrough",
        "category":    "secondary",
    },
    {
        "de":          "DE61",
        "iso_name":    "POS Data Code",
        "jcf_field":   "pos_data_code",
        "description": "12-character code describing cardholder/card presence and input method",
        "transform":   "passthrough",
        "category":    "secondary",
    },
    {
        "de":          "DE63",
        "iso_name":    "Network Data",
        "jcf_field":   "network",
        "description": "Network identifier (e.g. VISANET) carried through to response",
        "transform":   "passthrough",
        "category":    "secondary",
    },
    {
        "de":          "DE95",
        "iso_name":    "Replacement Amounts",
        "jcf_field":   "replacement_amount",
        "description": "Partial reversal amounts (actual amount + fee amounts)",
        "transform":   "passthrough",
        "category":    "secondary",
    },
    {
        "de":          "DE128",
        "iso_name":    "MAC (Message Authentication Code)",
        "jcf_field":   "mac",
        "description": "8-byte message authentication code for network security",
        "transform":   "passthrough",
        "category":    "secondary",
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# ISO 4217 numeric → alpha-3 mapping (common codes)
# ──────────────────────────────────────────────────────────────────────────────
_CURRENCY_NUM_TO_ALPHA = {
    "840": "USD",
    "978": "EUR",
    "826": "GBP",
    "392": "JPY",
    "036": "AUD",
    "124": "CAD",
    "756": "CHF",
    "344": "HKD",
    "356": "INR",
    "554": "NZD",
    "702": "SGD",
    "752": "SEK",
    "578": "NOK",
    "208": "DKK",
    "710": "ZAR",
    "076": "BRL",
    "484": "MXN",
}


def _apply_transform(value: str, transform: str) -> str:
    """Apply a named transform to produce the JCF-side value."""
    if not value or value == "(none)":
        return value
    if transform == "tokenize":
        # Mask all but last 4 digits (simulates tokenisation)
        if len(value) >= 4:
            return "****" + value[-4:]
        return value
    if transform == "truncate_25":
        return value[:25]
    if transform == "numeric_to_alpha":
        return _CURRENCY_NUM_TO_ALPHA.get(str(value), value)
    if transform == "format_iso8601":
        # Already ISO 8601 in our simulator; just flag that conversion happened
        return value
    if transform == "extract_time":
        # Extract HHMMSS from an ISO timestamp
        if "T" in str(value):
            return str(value).split("T")[1][:8].replace(":", "")
        return value
    if transform == "extract_date":
        # Extract MMDD from an ISO timestamp
        if "T" in str(value):
            parts = str(value).split("T")[0].split("-")
            if len(parts) == 3:
                return parts[1] + parts[2]
        return value
    if transform == "emv_tlv_decode":
        # Indicate that a BER-TLV decode is applied to chip data
        if value and value != "(none)":
            return f"[EMV TLV] {value[:32]}..." if len(value) > 32 else f"[EMV TLV] {value}"
        return value
    # passthrough (and all other unknown transforms)
    return value


def extract_iso_jcf_values(
    mapping_rows: list,
    request_sent: dict,
    response_received: dict,
    category_filter: str = "all",
) -> list:
    """
    Given live mapping table rows and a transaction trace, produce a
    translation table showing ISO field values alongside JCF field values.

    Args:
        mapping_rows:    rows from the editable mapping table
        request_sent:    outbound request dict (ISO / simulator fields)
        response_received: response dict (may carry enriched JCF fields)
        category_filter: "all" | "primary" | "emv" | "merchant" | "trace" | "secondary"

    Returns a list of dicts with keys:
      de, iso_name, iso_value, jcf_field, jcf_value, transform, transformed, category
    """
    # Merge: request fields take precedence for ISO input; response may enrich
    all_vals: dict = {}
    all_vals.update(response_received or {})
    all_vals.update(request_sent or {})

    result = []
    for row in mapping_rows:
        cat = row.get("category", "primary")
        if category_filter != "all" and cat != category_filter:
            continue

        jcf_field = row.get("jcf_field", "")
        transform  = row.get("transform", "passthrough")

        # ISO value = raw field from the outbound request
        raw_iso = (request_sent or {}).get(jcf_field, "")
        # JCF value = field from combined dict (response may override/enrich)
        raw_jcf = all_vals.get(jcf_field, "")

        iso_val = str(raw_iso) if raw_iso not in ("", None) else "(none)"
        # Apply the declared transform to produce the JCF value
        jcf_val_raw = str(raw_jcf) if raw_jcf not in ("", None) else iso_val
        jcf_val = _apply_transform(jcf_val_raw, transform)

        result.append({
            "de":          row.get("de", ""),
            "iso_name":    row.get("iso_name", ""),
            "iso_value":   iso_val,
            "jcf_field":   jcf_field,
            "jcf_value":   jcf_val,
            "transform":   transform,
            "transformed": transform not in ("passthrough", ""),
            "category":    cat,
        })
    return result
