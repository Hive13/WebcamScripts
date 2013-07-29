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
       webview = WebViewCompat(host, username, password)
       webview.OpenCameraServer()
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
                print "Preset %s not found. Exiting." % preset
                sys.exit(1)

    # Operate webcam by first gaining control
    print "Attempting to claim control over the webcam..."
    results = webview.GetCameraControl()
    print results

    results = webview.OperateCamera()
    if "No Camera Control Right" in results:
        print "Waiting to secure control rights..."
        time_passed = 0
        while "No Camera Control Right" in results and time_passed <= timeout:
            time.sleep(1)
            time_passed += 1
            print "Still waiting..."
            results = webview.OperateCamera()

            if "No Camera Control Right" not in results:
                print "Control rights obtained..."
                print results
                can_control = True
                break

            if time_passed == timeout - 1:
                print "Unable to obtain control rights (timeout)."
                break

    elif "OK" in results:
       "Control rights obtained..."
       can_control = True

    else:
        print "Failed to obtain camera controls"

    if can_control:
        for position in goto_position:
            pan = position[0]
            tilt = position[1]
            zoom = position[2]

            print "Moving camera to pan='%s', tilt='%s', zoom='%s'" \
                  "" % (pan, tilt, zoom),
            #webview.OperateCamera(pan=pan, tilt=tilt, zoom=zoom)# New presets
            webview.OperateCamera(p=pan, t=tilt, z=zoom)         # Compat presets

            print "\nSleeping for " + str(delay) + " seconds to allow time " \
                  "for positioning..."
            time.sleep(delay)

            print "Grabbing camera image and writing to file..."
            return_data = webview.GetOneShot(video_set, '30000', '1')
            position_str = pan + tilt + zoom
            fn = sys.path[0] + "/images/" + filename + "_" + timestamp() + \
                 "_" + position_str + ".jpg"
            out = open(fn, 'wb')
            out.write(return_data)
            out.close()
            print "Written to file %s" % fn

        print "Attempting to release control over the webcam..."
        results = webview.ReleaseCameraControl()
        print results

    print "Deleting the session id as part of cleanup..."
    results = webview.CloseCameraServer()
    print results

# If ran directly, execute main
if __name__ == "__main__":
    main()
