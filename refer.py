@app.route("/update", methods=['GET', 'POST'])
def update():
    msg = ''
    ph=PasswordHasher()
    if 'loggedin' in session:
        if request.method == 'POST' and 'password' in request.form:
            password = request.form['password']
            username = session['username']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("Update accounts set password = %s where username = %s",(password,username))
            mysql.connection.commit()
            msg = 'You have successfully updated !'
            return render_template("login.html")
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("update.html", msg=msg)
    return redirect(url_for('login'))
