from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from spreadsheet import Spreadsheet

bp = Blueprint("edit", __name__, url_prefix="/edit")


@bp.route("/<sheet_name>/append", methods=["POST"], defaults={"sheet_range": "A2:F"})
@bp.route("/<sheet_name>/<sheet_range>/append", methods=["POST"])
def append_row(sheet_name, sheet_range):
    """Append a new row to the spreadsheet"""
    spreadsheet: Spreadsheet = current_app.config["SPREADSHEET_OBJ"]
    spreadsheet.range = sheet_range
    if sheet_name:
        spreadsheet.sheet_name = sheet_name
    else:
        current_app.logger.error("Sheet name must be given.")
        return jsonify(
            {"response_success": False, "response_message": "Sheet name must be given."}
        )

    payload = request.get_json()

    # date
    values = [payload.get("date")]

    # reason: income or expense
    reason = payload.get("reason", "-")
    amount = payload.get("amount", None)
    if amount:
        if amount < 0:
            values.extend([reason, "-"])
        elif amount > 0:
            values.extend(["-", reason])
        else:
            current_app.logger.warning(
                "A zero amount in request payload. Might it be a mistake client-side?"
            )
            values.extend(["(zero amount)", "(zero amount)"])
    else:
        current_app.logger.error("'amount' cannot be none")
        values.extend(["ERROR", "ERROR"])

    # amount and which currency
    values.extend([amount, payload.get("currency", "-")])

    # bank account charged
    values.append(payload.get("account", "-"))

    # timestamp (when the expense has been recorded)
    values.append(payload.get("recordedOn", datetime.now().strftime("%d.%m.%Y, %H:%M")))

    # append the data
    spreadsheet_response = spreadsheet.append_record(values)

    return jsonify(
        {
            "response_success": True,
            "response_message": "Row added successfully.",
            "response_content": spreadsheet_response,
        }
    )
