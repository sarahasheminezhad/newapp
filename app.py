from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'my_secret_key'  # برای استفاده از session


# مرحله 1
@app.route('/')
def index():
    return redirect(url_for('step_one'))


@app.route('/step-one', methods=['GET', 'POST'])
def step_one():
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        session['company_name'] = company_name
        return redirect(url_for('step_two'))
    return render_template('steps.html', step=1)


# مرحله 2
@app.route('/step-two', methods=['GET', 'POST'])
def step_two():
    if request.method == 'POST':
        # دریافت داده‌ها از فرم
        w = request.form.get('w')
        Qr = request.form.get('Qr')
        Rp = request.form.get('Rp')
        recycled = request.form.get('recycled')

        # تبدیل به عدد
        try:
            w = float(w)
            Qr = float(Qr)
            Rp = float(Rp)
            recycled = float(recycled)
        except (TypeError, ValueError):
            w = Qr = Rp = recycled = 0

        # محاسبه‌ی مبلغ پیش‌پرداخت و دریافتنی
        prepayment = w * Qr
        receivables = Rp * recycled

        # ذخیره در session
        session['w'] = w
        session['Qr'] = Qr
        session['Rp'] = Rp
        session['recycled'] = recycled
        session['prepayment'] = prepayment
        session['receivables'] = receivables

        # بعد از محاسبه، برو مرحله بعد
        return redirect(url_for('step_three'))

    prepayment = session.get('prepayment')
    return render_template('steps.html', step=2, prepayment=prepayment)


# مرحله 3
@app.route('/step-three', methods=['GET', 'POST'])
def step_three():
    if request.method == 'POST':
        # ذخیره روش انتخابی (سنتی یا بلاکچین)
        method = request.form.get('method')
        session['method'] = method
        return redirect(url_for('step_four'))

    return render_template('steps.html', step=3)


# مرحله 4
@app.route('/step-four', methods=['GET'])
def step_four():
    # گرفتن داده‌ها از session
    prepayment = session.get('prepayment', 0)
    receivables = session.get('receivables', 0)
    total = prepayment + receivables

    # پارامترهای هر روش
    alpha_trad, i_trad, cost_trad = 0.55, 15, 10000
    alpha_block, i_block, cost_block = 0.88, 8, 1500

    # محاسبه سود بانکی برای هر روش
    pbank_trad = alpha_trad * total * i_trad - cost_trad
    pbank_block = alpha_block * total * i_block - cost_block

    # تصمیم نهایی وام برای روش سنتی
    if pbank_trad > 10000:
        loan_status = 'approve'
    elif 0 <= pbank_trad <= 10000:
        loan_status = 'half_approve'
    else:
        loan_status = 'not_approved'

    if pbank_block > 10000:
        loan_status = 'approve'
    elif 0 <= pbank_block <= 10000:
        loan_status = 'half_approve'
    else:
        loan_status = 'not_approved'
        
    return render_template(
        'steps.html',
        step=4,
        prepayment=prepayment,
        receivables=receivables,
        total=total,
        pbank_trad=pbank_trad,
        pbank_block=pbank_block,
        loan_status=loan_status
    )



if __name__ == '__main__':
    app.run(debug=True)