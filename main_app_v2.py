from flask import Flask, request, redirect, url_for

app = Flask(__name__)

# Application State
APP_STATE = {
    "balance": 1000.0,
    "user_logged": True,     # Public user session
    "admin_logged": False    # Admin portal session
}

MATCHES = [
    {"id": 1, "home": "Arsenal", "away": "Chelsea", "1": 1.85, "x": 3.40, "2": 4.20, "status": "Open", "winner": None},
    {"id": 2, "home": "Real Madrid", "away": "Barcelona", "1": 2.10, "x": 3.20, "2": 3.10, "status": "Open", "winner": None}
]
SLIPS = []

# ==================== PUBLIC PORTAL ====================

@app.route('/')
def public_portal():
    match_html = ""
    for m in MATCHES:
        if m['status'] == "Open":
            match_html += f'''
            <div style="background: #1b2230; border-radius: 8px; padding: 12px; margin-bottom: 12px; border: 1px solid #2a3447;">
                <div style="font-size: 14px; font-weight: bold; margin-bottom: 8px; color: #fff;">{m['home']} vs {m['away']}</div>
                <form action="/bet" method="POST">
                    <input type="hidden" name="match_id" value="{m['id']}">
                    <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                        <button type="submit" name="pick" value="1" style="flex:1; background:#121824; border:1px solid #334155; color:#10b981; padding:8px; border-radius:4px; font-weight:bold;">1: {m['1']}</button>
                        <button type="submit" name="pick" value="X" style="flex:1; background:#121824; border:1px solid #334155; color:#10b981; padding:8px; border-radius:4px; font-weight:bold;">X: {m['x']}</button>
                        <button type="submit" name="pick" value="2" style="flex:1; background:#121824; border:1px solid #334155; color:#10b981; padding:8px; border-radius:4px; font-weight:bold;">2: {m['2']}</button>
                    </div>
                    <input type="number" name="stake" placeholder="Enter stake..." min="10" required style="width:100%; padding:8px; background:#121824; border:1px solid #334155; color:#fff; border-radius:4px; box-sizing:border-box;">
                </form>
            </div>
            '''
        else:
            match_html += f'''
            <div style="background: #1b2230; border-radius: 8px; padding: 10px; margin-bottom: 10px; opacity: 0.6; border: 1px solid #2a3447; font-size: 13px;">
                <div><b>{m['home']} vs {m['away']}</b> (Finished)</div>
                <div style="color: #10b981;">Result: <b>{m['winner']}</b></div>
            </div>
            '''

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ProSport - Public Portal</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: sans-serif; background: #121824; color: #fff; margin: 0; padding: 12px; }}
            .wallet {{ background: #1b2230; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-bottom: 2px solid #10b981; }}
            .bal {{ background: #121824; padding: 8px 14px; border-radius: 20px; border: 1px solid #10b981; color: #10b981; font-weight: bold; display: inline-block; font-size: 16px; }}
            .btn-dep {{ background: #059669; color: #fff; border: none; padding: 8px 12px; border-radius: 4px; font-weight: bold; cursor: pointer; }}
            .btn-wit {{ background: #dc2626; color: #fff; border: none; padding: 8px 12px; border-radius: 4px; font-weight: bold; cursor: pointer; }}
            h3 {{ color: #10b981; border-bottom: 1px solid #2a3447; padding-bottom: 4px; }}
        </style>
    </head>
    <body>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <h2 style="color:#10b981; margin:0;">ProSport Portal</h2>
            <a href="/admin" style="color:#38bdf8; text-decoration:none; font-size:12px; font-weight:bold; background:#1e293b; padding:6px 10px; border-radius:4px;">Admin Portal &rarr;</a>
        </div>

        <div class="wallet">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="font-size:13px; color:#94a3b8;">My Account</span>
                <a href="/history" style="color:#38bdf8; text-decoration:none; font-size:12px; font-weight:bold;">Bet History</a>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div class="bal">🪙 {APP_STATE['balance']:.2f}</div>
                <div>
                    <form action="/deposit" method="POST" style="display:inline;"><button type="submit" class="btn-dep">+ Deposit</button></form>
                    <form action="/withdraw" method="POST" style="display:inline;"><button type="submit" class="btn-wit">- Withdraw</button></form>
                </div>
            </div>
        </div>

        <h3>Live Match Fixtures</h3>
        {match_html}
    </body>
    </html>
    '''

@app.route('/deposit', methods=['POST'])
def deposit():
    APP_STATE['balance'] += 500.0
    return redirect(url_for('public_portal'))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if APP_STATE['balance'] >= 500.0:
        APP_STATE['balance'] -= 500.0
    return redirect(url_for('public_portal'))

@app.route('/bet', methods=['POST'])
def place_bet():
    match_id = int(request.form.get('match_id'))
    pick = request.form.get('pick')
    stake = float(request.form.get('stake', 0))
    
    match_obj = next((m for m in MATCHES if m['id'] == match_id), None)
    if match_obj and APP_STATE['balance'] >= stake and stake > 0:
        APP_STATE['balance'] -= stake
        SLIPS.append({
            "match_id": match_id,
            "match": f"{match_obj['home']} vs {match_obj['away']}",
            "pick": pick,
            "stake": stake,
            "status": "Pending",
            "payout": 0.0
        })
    return redirect(url_for('public_portal'))

@app.route('/history')
def history():
    history_html = ""
    for s in reversed(SLIPS):
        color = "#eab308"
        if s['status'] == "Won": color = "#10b981"
        elif s['status'] == "Lost": color = "#ef4444"
        
        history_html += f'''
        <div style="background: #1b2230; padding: 12px; margin-bottom: 8px; border-radius: 6px; border-left: 4px solid {color}; font-size: 13px;">
            <div style="font-weight:bold; margin-bottom:4px;">{s['match']}</div>
            <div style="color: #94a3b8;">Pick: <span style="color:#fff;">{s['pick']}</span> | Stake: {s['stake']} tokens</div>
            <div style="margin-top:4px; display:flex; justify-content:space-between;">
                <span>Status: <b style="color:{color};">{s['status']}</b></span>
                <span>Payout: <b>{s['payout']:.2f}</b></span>
            </div>
        </div>
        '''
    if not history_html:
        history_html = "<p style='color:#64748b; text-align:center;'>No betting history found.</p>"

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bet History</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: sans-serif; background: #121824; color: #fff; margin: 0; padding: 12px; }}
            h3 {{ color: #10b981; border-bottom: 1px solid #2a3447; padding-bottom: 4px; }}
            .back-btn {{ display: inline-block; background: #334155; color: #fff; text-decoration: none; padding: 6px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-bottom: 15px; }}
        </style>
    </head>
    <body>
        <a href="/" class="back-btn">&#8592; Back to Public Portal</a>
        <h3>My Betting Ledger</h3>
        {history_html}
    </body>
    </html>
    '''


# ==================== ADMIN PORTAL ====================

@app.route('/admin', methods=['GET', 'POST'])
def admin_portal():
    if request.method == 'POST':
        user = request.form.get('user')
        pwd = request.form.get('pass')
        if user == 'admin' and pwd == 'password123':
            APP_STATE['admin_logged'] = True
        return redirect(url_for('admin_portal'))

    if not APP_STATE['admin_logged']:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Login</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: sans-serif; background: #121824; color: #fff; padding: 20px; display: flex; justify-content: center; align-items: center; height: 85vh; margin:0; }
                .box { background: #1b2230; width: 100%; max-width: 350px; padding: 25px; border-radius: 10px; border-top: 4px solid #38bdf8; box-sizing: border-box; }
                input { width: 100%; padding: 12px; margin: 10px 0; background: #121824; border: 1px solid #334155; color: #fff; border-radius: 6px; box-sizing: border-box; }
                button { width: 100%; padding: 12px; background: #0284c7; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="box">
                <h2 style="color: #38bdf8; text-align: center; margin-top:0;">Admin Portal Login</h2>
                <form method="POST">
                    <label style="font-size:12px; color:#94a3b8;">Username</label>
                    <input type="text" name="user" value="admin" required>
                    <label style="font-size:12px; color:#94a3b8;">Password</label>
                    <input type="password" name="pass" value="password123" required>
                    <button type="submit" style="margin-top:15px;">Login to Admin</button>
                </form>
                <div style="text-align:center; margin-top:15px;">
                    <a href="/" style="color:#94a3b8; font-size:12px; text-decoration:none;">&larr; Back to Public Portal</a>
                </div>
            </div>
        </body>
        </html>
        '''

    # Admin Dashboard View
    manage_html = ""
    for m in MATCHES:
        if m['status'] == "Open":
            manage_html += f'''
            <div style="background: #1b2230; border-radius: 8px; padding: 10px; margin-bottom: 10px; border: 1px solid #2a3447; font-size: 13px;">
                <div><b>{m['home']} vs {m['away']}</b></div>
                <div style="margin-top: 6px; display: flex; gap: 4px;">
                    <span style="color: #94a3b8; align-self: center; font-size:11px;">Settle Match:</span>
                    <form action="/admin/settle/{m['id']}/1" method="POST" style="display:inline;"><button type="submit" style="background:#059669; color:#fff; border:none; padding:4px 8px; border-radius:3px; cursor:pointer; font-size:11px;">Home</button></form>
                    <form action="/admin/settle/{m['id']}/X" method="POST" style="display:inline;"><button type="submit" style="background:#d97706; color:#fff; border:none; padding:4px 8px; border-radius:3px; cursor:pointer; font-size:11px;">Draw</button></form>
                    <form action="/admin/settle/{m['id']}/2" method="POST" style="display:inline;"><button type="submit" style="background:#dc2626; color:#fff; border:none; padding:4px 8px; border-radius:3px; cursor:pointer; font-size:11px;">Away</button></form>
                </div>
            </div>
            '''

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: sans-serif; background: #121824; color: #fff; margin: 0; padding: 12px; }}
            h3 {{ color: #38bdf8; border-bottom: 1px solid #2a3447; padding-bottom: 4px; }}
            input {{ width: 100%; padding: 8px; margin: 5px 0; background: #121824; border: 1px solid #334155; color: #fff; border-radius: 4px; box-sizing: border-box; }}
        </style>
    </head>
    <body>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; background:#1b2230; padding:12px; border-radius:8px;">
            <span style="font-weight:bold; color:#38bdf8;">Admin Control Panel</span>
            <div>
                <a href="/" style="color:#10b981; text-decoration:none; font-size:12px; font-weight:bold; margin-right:10px;">Public Portal</a>
                <a href="/admin/logout" style="color:#ef4444; text-decoration:none; font-size:12px; font-weight:bold;">Logout</a>
            </div>
        </div>

        <h3>Create New Match</h3>
        <div style="background: #1b2230; padding: 12px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #2a3447;">
            <form action="/admin/add_match" method="POST">
                <div style="display:flex; gap:8px;">
                    <input type="text" name="home" placeholder="Home Team" required style="flex:1;">
                    <input type="text" name="away" placeholder="Away Team" required style="flex:1;">
                </div>
                <div style="display:flex; gap:6px; margin-top:6px;">
                    <input type="number" step="0.01" name="odd_1" placeholder="1 Odd" value="1.85" required style="flex:1;">
                    <input type="number" step="0.01" name="odd_x" placeholder="X Odd" value="3.40" required style="flex:1;">
                    <input type="number" step="0.01" name="odd_2" placeholder="2 Odd" value="2.50" required style="flex:1;">
                </div>
                <button type="submit" style="width:100%; margin-top:8px; background:#0284c7; color:#fff; border:none; padding:8px; border-radius:4px; font-weight:bold; cursor:pointer;">+ Add Match</button>
            </form>
        </div>

        <h3>Active Fixtures Management</h3>
        {manage_html}
    </body>
    </html>
    '''

@app.route('/admin/logout')
def admin_logout():
    APP_STATE['admin_logged'] = False
    return redirect(url_for('admin_portal'))

@app.route('/admin/add_match', methods=['POST'])
def admin_add_match():
    if not APP_STATE['admin_logged']: return redirect(url_for('admin_portal'))
    home = request.form.get('home')
    away = request.form.get('away')
    odd_1 = float(request.form.get('odd_1', 1.8))
    odd_x = float(request.form.get('odd_x', 3.2))
    odd_2 = float(request.form.get('odd_2', 2.5))
    
    if home and away:
        new_id = len(MATCHES) + 1
        MATCHES.append({
            "id": new_id, "home": home, "away": away, 
            "1": odd_1, "x": odd_x, "2": odd_2, 
            "status": "Open", "winner": None
        })
    return redirect(url_for('admin_portal'))

@app.route('/admin/settle/<int:match_id>/<winner>', methods=['POST'])
def admin_settle(match_id, winner):
    if not APP_STATE['admin_logged']: return redirect(url_for('admin_portal'))
    for m in MATCHES:
        if m['id'] == match_id and m['status'] == "Open":
            m['status'] = "Closed"
            m['winner'] = winner
            for s in SLIPS:
                if s['match_id'] == match_id and s['status'] == "Pending":
                    if s['pick'] == winner:
                        s['status'] = "Won"
                        odd = m['1'] if winner == '1' else (m['x'] if winner == 'X' else m['2'])
                        payout = s['stake'] * odd
                        APP_STATE['balance'] += payout
                        s['payout'] = payout
                    else:
                        s['status'] = "Lost"
                        s['payout'] = 0.0
    return redirect(url_for('admin_portal'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
