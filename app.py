from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Future Value Calculator</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2em;
        }
        .section {
            margin-bottom: 25px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:active {
            transform: translateY(0);
        }
        .result {
            margin-top: 30px;
            padding: 25px;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            border-radius: 10px;
            text-align: center;
            display: none;
        }
        .result h2 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .result p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .hidden {
            display: none;
        }
        .note {
            background: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            color: #856404;
            margin-top: 15px;
        }
        .cash-flow-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border: 2px solid #e0e0e0;
        }
        .cash-flow-item h4 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .add-btn {
            background: #28a745;
            margin-bottom: 15px;
        }
        .remove-btn {
            background: #dc3545;
            padding: 8px 15px;
            font-size: 14px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💰 Future Value Calculator</h1>
        
        <div class="section">
            <label>Is this an annuity (equal periodic payments)?</label>
            <select id="isAnnuity" onchange="toggleSections()">
                <option value="">-- Select --</option>
                <option value="yes">Yes</option>
                <option value="no">No</option>
            </select>
        </div>

        <!-- ANNUITY SECTION -->
        <div id="annuitySection" class="hidden">
            <div class="section">
                <label>Is this a perpetuity (payments continue forever)?</label>
                <select id="isPerpetual" onchange="togglePerpetuity()">
                    <option value="">-- Select --</option>
                    <option value="yes">Yes</option>
                    <option value="no">No</option>
                </select>
            </div>

            <div id="perpetuityNote" class="note hidden">
                <strong>⚠️ Note:</strong> Perpetuities have infinite future value since payments continue forever!<br>
                Future Value = ∞ (Infinity)
            </div>

            <div id="annuityInputs" class="hidden">
                <div class="section">
                    <label>When are payments made?</label>
                    <select id="annuityType">
                        <option value="">-- Select --</option>
                        <option value="end">End of period</option>
                        <option value="beginning">Beginning of period</option>
                    </select>
                </div>

                <div class="section">
                    <label>Periodic Payment Amount ($)</label>
                    <input type="number" id="payment" step="0.01" placeholder="e.g., 1000">
                </div>

                <div class="section">
                    <label>Annual Interest Rate (%)</label>
                    <input type="number" id="annuityRate" step="0.01" placeholder="e.g., 5">
                </div>

                <div class="section">
                    <label>Number of Payments Per Year</label>
                    <input type="number" id="paymentsPerYear" placeholder="e.g., 12 for monthly">
                </div>

                <div class="section">
                    <label>Total Time Period (Years)</label>
                    <input type="number" id="timePeriod" step="0.01" placeholder="e.g., 10">
                </div>

                <button onclick="calculateAnnuity()">Calculate Future Value</button>
            </div>
        </div>

        <!-- NON-ANNUITY SECTION -->
        <div id="nonAnnuitySection" class="hidden">
            <div class="section">
                <label>Annual Interest Rate (%)</label>
                <input type="number" id="interestRate" step="0.01" placeholder="e.g., 5">
            </div>

            <div class="section">
                <label>Compounding Periods Per Year</label>
                <input type="number" id="compoundingPeriods" placeholder="e.g., 12 for monthly">
            </div>

            <div class="section">
                <label>Target Future Time (Years from now)</label>
                <input type="number" id="targetTime" step="0.01" placeholder="e.g., 10">
            </div>

            <div class="section">
                <label>Number of Cash Flows</label>
                <input type="number" id="numCashFlows" min="1" value="1" onchange="generateCashFlowInputs()">
            </div>

            <div id="cashFlowsContainer"></div>

            <button onclick="calculateNonAnnuity()">Calculate Future Value</button>
        </div>

        <div id="result" class="result"></div>
    </div>

    <script>
        function toggleSections() {
            const isAnnuity = document.getElementById('isAnnuity').value;
            document.getElementById('annuitySection').classList.toggle('hidden', isAnnuity !== 'yes');
            document.getElementById('nonAnnuitySection').classList.toggle('hidden', isAnnuity !== 'no');
            document.getElementById('result').style.display = 'none';
        }

        function togglePerpetuity() {
            const isPerpetual = document.getElementById('isPerpetual').value;
            document.getElementById('perpetuityNote').classList.toggle('hidden', isPerpetual !== 'yes');
            document.getElementById('annuityInputs').classList.toggle('hidden', isPerpetual !== 'no');
        }

        function generateCashFlowInputs() {
            const num = parseInt(document.getElementById('numCashFlows').value) || 1;
            const container = document.getElementById('cashFlowsContainer');
            container.innerHTML = '';

            for (let i = 1; i <= num; i++) {
                container.innerHTML += `
                    <div class="cash-flow-item">
                        <h4>Cash Flow #${i}</h4>
                        <label>Amount ($)</label>
                        <input type="number" id="cf_amount_${i}" step="0.01" placeholder="e.g., 5000">
                        <label style="margin-top: 10px;">Occurs at (Years from now)</label>
                        <input type="number" id="cf_time_${i}" step="0.01" placeholder="e.g., 2">
                    </div>
                `;
            }
        }

        async function calculateAnnuity() {
            const isPerpetual = document.getElementById('isPerpetual').value;
            
            if (isPerpetual === 'yes') {
                showResult('∞', 'Perpetuities have infinite future value!');
                return;
            }

            const data = {
                type: 'annuity',
                annuityType: document.getElementById('annuityType').value,
                payment: parseFloat(document.getElementById('payment').value),
                rate: parseFloat(document.getElementById('annuityRate').value),
                paymentsPerYear: parseInt(document.getElementById('paymentsPerYear').value),
                timePeriod: parseFloat(document.getElementById('timePeriod').value)
            };

            const response = await fetch('/calculate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (result.error) {
                alert(result.error);
            } else {
                showResult(`$${result.fv.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`, 
                          `Payments at ${data.annuityType} of period`);
            }
        }

        async function calculateNonAnnuity() {
            const num = parseInt(document.getElementById('numCashFlows').value);
            const cashFlows = [];

            for (let i = 1; i <= num; i++) {
                cashFlows.push({
                    amount: parseFloat(document.getElementById(`cf_amount_${i}`).value),
                    time: parseFloat(document.getElementById(`cf_time_${i}`).value)
                });
            }

            const data = {
                type: 'non_annuity',
                rate: parseFloat(document.getElementById('interestRate').value),
                compoundingPeriods: parseInt(document.getElementById('compoundingPeriods').value),
                targetTime: parseFloat(document.getElementById('targetTime').value),
                cashFlows: cashFlows
            };

            const response = await fetch('/calculate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (result.error) {
                alert(result.error);
            } else {
                showResult(`$${result.fv.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`, 
                          `Total FV at year ${data.targetTime}`);
            }
        }

        function showResult(value, subtitle) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = `<h2>${value}</h2><p>${subtitle}</p>`;
            resultDiv.style.display = 'block';
        }

        // Initialize
        generateCashFlowInputs();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        
        if data['type'] == 'annuity':
            pmt = data['payment']
            r = data['rate'] / 100
            n = data['paymentsPerYear']
            t = data['timePeriod']
            annuity_type = data['annuityType']
            
            periodic_rate = r / n
            total_periods = n * t
            
            if periodic_rate == 0:
                fv = pmt * total_periods
            else:
                fv = pmt * (((1 + periodic_rate) ** total_periods - 1) / periodic_rate)
                
                if annuity_type == 'beginning':
                    fv *= (1 + periodic_rate)
            
            return jsonify({'fv': fv})
        
        elif data['type'] == 'non_annuity':
            r = data['rate'] / 100
            n = data['compoundingPeriods']
            target_time = data['targetTime']
            cash_flows = data['cashFlows']
            
            total_fv = 0
            
            for cf in cash_flows:
                remaining_time = target_time - cf['time']
                
                if remaining_time < 0:
                    fv = 0
                else:
                    fv = cf['amount'] * ((1 + r/n) ** (n * remaining_time))
                
                total_fv += fv
            
            return jsonify({'fv': total_fv})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# For Vercel serverless
app = app

if __name__ == '__main__':
    app.run(debug=True)
```

---
