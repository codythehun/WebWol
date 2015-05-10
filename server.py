from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, abort
from wakeonlan import wol
import os
import config
import network_utils as nu
import shelve
from contextlib import closing

app = Flask(__name__)

app.config.update(dict(USERNAME=config.username, PASSWORD=config.password),
SECRET_KEY=config.secret_key)

db = shelve.open(config.db_file, writeback=True) #TODO: this ain't thread or process safe! switch to ZODB

def discover_hosts():
    return [(hostname or 'Unknown', mac, ip) for (hostname, mac, ip) in nu.scan_subnet()]
    

def discover_and_persist_hosts():
    up_hosts = discover_hosts()
    result = []
    up_macs = set()
    for name, mac, ip in up_hosts:
        if mac not in db:
            db[mac] = (name, ip)
        else:
            saved_name, saved_ip = db[mac]
            db[mac] = (saved_name, ip) # refresh ip 
        result.append((db[mac][0], mac, ip, True))
        up_macs.add(mac)
    for mac,(name, ip) in db.iteritems():
        if mac not in up_macs:
            result.append((name, mac, ip, False))
    db.sync()
    return result        

@app.route("/wakey", methods=['GET','POST'])
def wakey():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    error=None
    if request.method == 'GET':
        if 'delete' in request.args:
            try:
                del db[request.args['delete']]
                db.sync()
            except KeyError:
                error = "No such host"  
        if 'wake' in request.args:
            try:
                wol.send_magic_packet(request.args['wake'])
                flash('Magic packet sent')
            except ValueError:
                error = "Incorrect MAC address"
    elif request.method == 'POST':
        db[str(request.form['mac'])] = (request.form['name'], request.form['ip'])
        db.sync()

    hosts = discover_and_persist_hosts()
    return render_template('wakey.html', error=error, hosts=hosts)

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
    	if request.method == 'POST':
    		if request.form['username'] != app.config['USERNAME']:
    			error = 'Invalid username'
    		elif request.form['password'] != app.config['PASSWORD']:
   			    error = 'Invalid password'
    		else:
    			session['logged_in'] = True
    			flash('You were logged in')
    			return redirect(url_for('wakey'))
	return render_template('login.html', error=error)
    
@app.route('/logout')
def logout():
	session.pop('logged_in', None)
   	flash('You were logged out')
   	return redirect(url_for('wakey'))	

if __name__ == "__main__":
    with closing(db):
        app.run('0.0.0.0', port=config.port, debug=True)
