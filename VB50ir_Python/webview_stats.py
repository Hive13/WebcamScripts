import sys
from include.webview import *

def main():
    '''Main staring point of entire program.'''

    # Define user variables for access to administrative logs
    un = 'root'
    pw = 'password'
    host = 'hostname'

    # Define user variables for access to database
    db_host = 'localhost'
    db_name = 'webview'
    db_un = 'username'
    db_pw = 'password'
    db_table = 'visits'

    # Create our objects
    try:
        wvadmin = WebViewAdmin(host, un, pw)
        wvstatdb = WebViewStatDB(db_host, db_un, db_pw, db_name, db_table)
    except Exception, e:
        print "%s" % e
        sys.exit(1)

    # CAUTION: Uncomment only if needed (ie. running for the first time)
    #wvstatdb.reset_db()

    # Grab the user summary from syslog and write the results to the DB
    syslog_stats = wvadmin.get_user_summary()
    for user, visited, ip in syslog_stats:
        if wvstatdb.add_stats_to_db(user, visited, ip):
            print "Added %s who visited on %s from %s" % (user, visited, ip)

# If ran directly, execute main
if __name__ == "__main__":
    main()
