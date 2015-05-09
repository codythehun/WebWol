from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, abort
from wakeonlan import wol
import os
import config
import network_utils as nu
import shelve

app = Flask(__name__)

app.config.update(dict(USERNAME=config.username, PASSWORD=config.password),
SECRET_KEY=config.secret_key)


def discover_hosts():
    hosts = nu.scan_subnet()
    filtered_hosts = [(hostname, mac, ip) for (hostname, mac, ip) in hosts if hostname]
    return filtered_hosts

def discover_and_persist_hosts():
    stored_hosts = shelve.open(config.db_file, writeback=True) #TODO: this ain't threadsafe!
    up_hosts = discover_hosts()
    result = []
    up_macs = set()
    for name, mac, ip in up_hosts:
        if mac not in stored_hosts:
            stored_hosts[mac] = (name, ip)
        result.append((name, mac, ip, True))
        up_macs.add(mac)
    for mac,(name, ip) in stored_hosts.iteritems():
        if mac not in up_macs:
            result.append((name, mac, ip, False))
    stored_hosts.close()
    return result        

@app.route("/discover", methods=['GET','POST'])
def discover():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    error=None
    if request.method == 'GET':
        if 'delete' in request.args:
            saved_hosts = shelve.open(config.db_file, writeback=True)
            try:
                del saved_hosts[request.args['delete']]
            except KeyError:
                error = "No such host"  
            saved_hosts.close()
        if 'wake' in request.args:
            try:
                wol.send_magic_packet(request.args['wake'])
                flash('Magic packet sent')
            except ValueError:
                error = "Incorrect MAC address"
    elif request.method == 'POST':
        saved_hosts = shelve.open(config.db_file, writeback=True)
        saved_hosts[str(request.form['mac'])] = (request.form['name'], request.form['ip'])
        saved_hosts.close()

    hosts = discover_and_persist_hosts()
    return render_template('discover.html', error=error, hosts=hosts)

@app.route("/wakey", methods=['GET', 'POST'])
def wakey():
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	if request.method == 'POST':
		if request.form['action'] == 'WakeyWakey':
			wol.send_magic_packet(config.mac_addr)
			flash('Magic packet sent')
		if request.form['action'] == 'Uthere':
			response = os.system("ping -c 1 " + config.ip_addr)
			if response == 0:
				flash("Yeppers")
			else:
				flash("Nah bro!")
				
	return render_template('wakey.html', error=None)	

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
	app.run('0.0.0.0', port=config.port, debug=True)
