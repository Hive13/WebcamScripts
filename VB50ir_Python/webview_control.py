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

    parser.add_option("", "--preset-list", action="store", type="string",
            default=None, dest="preset_list", help="Move camera to preset" \
            " positions in this list")

    parser.add_option("", "--position", action="store", type="string",
            default=None, dest="position", help="Move camera to this position" \
            " (pan, tilt, zoom)")

    opts, args = parser.parse_args()

    if not args:
        parser.print_help(sys.stderr)
        parser.error("You must supply a hostname to connect with.")

    if not (opts.position or opts.preset_list):
        parser.print_help(sys.stderr)
        parser.error("You must supply a position or preset list to move the " \
                     "webcam to.")

    return opts, args

def main():
    '''Main staring point of entire program.'''

    # Parse and gather all command line arguments
    opts, args = parse_options()

    password = opts.password
    username = opts.username
    host = args[0]
    filename = opts.filename
    preset_list = opts.preset_list
    video_set = opts.video
    position = opts.position

    delay = 3                          # time to give camera to position
    timeout = 42                       # time to wait for control
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

    if position:
        my_splitter = shlex.shlex(position, posix=True)
        my_splitter.whitespace += ','
        my_splitter.whitespace_split = True
        position = list(my_splitter)
        goto_position.append((position[0], position[1], position[2]))

    if preset_list:
        my_splitter = shlex.shlex(preset_list, posix=True)
        my_splitter.whitespace += ','
        my_splitter.whitespace_split = True
        preset_list = list(my_splitter)
        for preset in preset_list:
            preset_vals = webview.select_preset(preset_no=preset)
            if (preset_vals['pan'] != "" or \
                preset_vals['tilt'] != "" or \
                preset_vals['zoom'] != ""):
                goto_position.append((preset_vals['pan'], preset_vals['tilt'],
                                      preset_vals['zoom']))
            else:
                print "Preset %s not found. Exiting" % preset
                sys.exit(1)

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
        for position in goto_position:
            pan = position[0]
            tilt = position[1]
            zoom = position[2]

            print "Moving camera to pan='%s', tilt='%s', zoom='%s'" \
                  "" % (pan, tilt, zoom),
            return_data = webview.control(pan=pan, tilt=tilt, zoom=zoom)

            print " (sleeping for " + str(delay) + " seconds to allow time " \
                  "for positioning)..."
            time.sleep(delay)

            print "Grabbing camera image and writing to file..."
            return_data = webview.image(video=video_set)
            position_str = pan + tilt + zoom
            fn = sys.path[0] + "/images/" + filename + "_" + timestamp() + \
                 "_" + position_str + ".jpg"
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
