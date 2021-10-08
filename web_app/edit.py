from datetime import datetime

from flask import Blueprint, jsonify, current_app, request

bp = Blueprint('edit', __name__, url_prefix='/edit')

@bp.route('/<sheet_name>/append', methods=['POST'], defaults={"sheet_range": "A2:F"})
@bp.route('/<sheet_name>/<sheet_range>/append', methods=['POST'])
def append_row(sheet_name, sheet_range):
    """Append a new row to the spreadsheet"""
    spreadsheet = current_app.config['SPREADSHEET_OBJ']
    spreadsheet.range = sheet_range
    if sheet_name:
        spreadsheet.sheet_name = sheet_name
    else:
        current_app.logger.error("sheet_name must be given.")
        return jsonify({"response_success": False, "response_message": "`sheet_name` must be given."})
    
    payload = request.get_json()
    
    # date
    values = [payload.get('date')]

    # reason: income or expense
    reason = payload.get('reason', '-')
    if payload.get('amount'):
        if payload['amount'] < 0:
            values.extend([reason, '-'])
        else:
            values.extend(['-', reason])
    
    # amount and which currency
    amount = payload.get('amount', 0.0)
    if payload.get('currency') == "CHF":
        values.extend([amount, 0.0])
    else:
        values.extend([0.0, amount])

    # bank account charged
    values.append(payload.get('account', '-'))

    # timestamp (when the expense has been recorded)
    values.append(payload.get('recordedOn', datetime.now().strftime("%d.%m.%Y, %H:%M")))

    # append the data
    spreadsheet_response = spreadsheet.append_record(values)

    return jsonify({"response_success": True,
                    "response_message": "Row added successfully.",
                    "response_content": spreadsheet_response})