import sys, time, optparse
import shlex
import urllib2
from include.webview import *

def parse_options():
    '''Parse through the command line parameters being passed in'''

    parser = optparse.OptionParser(version=VERSION, description=DESCRIPTION,
                                   usage=USAGE)

    parser.add_option("-u", "--username", action="store", type="string",
            default=None, dest="username", help="Username to connect with")

    parser.add_option("-p", "--password", action="store", type="string",
            default=None, dest="password", help="Password to connect with")

    parser.add_option("-f", "--filename", action="store", type="string",
            default="webview", dest="filename",
            help="Write output to this filename (\"webview\" by default)")

    parser.add_option("", "--video", action="store", type="string",
            default='jpg:640x480:5:30000', dest="video",
            help="Video mode for camera")

    opts, args = parser.parse_args()

    if not args:
        parser.print_help(sys.stderr)
        parser.error("You must supply a hostname to connect with.")

    return opts, args

def main():
    '''Main staring point of entire program.'''

    # Parse and gather all command line arguments
    opts, args = parse_options()

    password = opts.password
    username = opts.username
    host = args[0]
    filename = opts.filename
    video_set = opts.video

    first_delay = 3                    # time to give camera to position
    second_delay = 1                   # time to give camera to position
    timeout = 60                       # time to wait for control
    can_control = False                # Assume we can't control camera yet

    # Instantiate a new webview object and open the session
    print "Logging in and starting the webview session..."
    try:
       webview = WebView(host, username, password)
       webview.open(video=video_set)

    except urllib2.URLError, e:
       print "Unable to connect to host (%s)" % e
       sys.exit(1)

    # [(pan, tilt, zoom), (pan2, tilt2, zoom2), ...]
    goto_position = []

    count = 0
    for tilt in range(50, -10101, -3350):
        for pan in range(17000, -18000, -4900):
            count += 1
            goto_position.append((str(pan), str(tilt), '5590'))
    print "Going to capture %s images to create 360 degree panorama..." \
          "" % count

    # Operate webcam by first gaining control
    print "Attempting to claim control over the webcam..."
    claim_results = webview.get_claim_control_results()
    if claim_results['control status'] == "enabled":
        print "Control right secured for %s seconds" \
              "" % str(int(claim_results['control time']) / 1000)
        can_control = True

    elif claim_results['control status'] == "waiting":
        time_passed = 0
        print "Waiting to secure control right (%s seconds at most)" \
              "" % str(int(claim_results['control time']) / 1000)

        while claim_results['control status'] == "waiting" and \
              time_passed <= timeout:

            if time_passed == timeout:
                print "Timeout exceeded. Giving up."
                break

            print "Still waiting..."
            time.sleep(1)
            time_passed += 1

            if webview.get_claim_control_results()['control status'] == "enabled":
                print "Control right secured for %s seconds" \
                      "" % str(int(claim_results['control time']) / 1000)
                can_control = True
                break

    elif claim_results['control status'] == "disabled":
        print "Failed to secure control privilege! Check the username and " \
              "password and try again. Otherwise, somebody like the admin " \
              "has control and won't let go."
        sys.exit(1)

#    TODO: Need to account for our time limit running out. When it does,
#          We need to go through the same process we just did (try to claim,
#           wait if needed, control).
#    if can_control and int(claim_results['control time']) / 1000 > 0:
    if can_control:
        count = 0
        thetime = ""
        thetime = timestamp()
        for position in goto_position:
            pan = position[0]
            tilt = position[1]
            zoom = position[2]
            count += 1
            print "Moving camera to pan='%s', tilt='%s', zoom='%s'" \
                  "" % (pan, tilt, zoom),
            return_data = webview.control(pan=pan, tilt=tilt, zoom=zoom)

            if count == 1:
                print " (sleeping for " + str(first_delay) + " seconds to allow time " \
                      "for positioning)..."
                time.sleep(first_delay)
            else:
                print " (sleeping for " + str(second_delay) + " seconds to allow time " \
                      "for positioning)..."
                time.sleep(second_delay)

            print "Grabbing camera image and writing to file..."
            return_data = webview.image(video=video_set)
            position_str = pan + tilt + zoom
            fn = sys.path[0] + "/images/360/" + filename + "_" + thetime + \
                 "_" + str(count) + ".jpg"
            out = open(fn, 'wb')
            out.write(return_data)
            out.close()
            print "Written to file %s" % fn

    print "Releasing control of the webcam..."
    yield_status = webview.get_yield_control_results()
    if yield_status == "disabled":
        print >> sys.stderr, "SUCCESS: released camera control"
    if yield_status == "failed":
        print >> sys.stderr, "WARNING: failed to release camera control"

    close_result = webview.close()
    if "OK" in close_result:
        print "Successfully closed webview session."
    else:
        print "WARNING: Unable to close the connection!"

# If ran directly, execute main
if __name__ == "__main__":
    main()
