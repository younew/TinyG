#TinyG Manual / Loader Application
#www.synthetos.com/tinyG
#Riley Porter [ a t ] Gmail <dot> com


import wx
import ser.serial_init as serinit
import time
from threading import *


class FlexGridSizer(wx.Frame):
    def __init__(self, parent, id, title):
        self.Frame = wx.Frame.__init__(self, parent, id, title, (-1,-1), size=(750,650))
        #State Keepers for Nudging
        self.X_STATE  = 0
        self.Y_STATE = 0
        #Needed for Threading
        self.worker = 0
        #Needed for Threading

        #MenuBars and Menus
        #menubar = wx.MenuBar()
        #file = wx.Menu()
        #file.Append(wx.ID_EXIT,'Quit', 'Quit Application')
        #menubar.Append(file, '&File')
        #self.SetMenuBar(menubar)
        #menubar.Show()

        #Status Bar
        self.status_bar = self.CreateStatusBar(1,style=wx.EXPAND|wx.ALL)
        self.status_bar.SetStatusText("TinyG")

        #self.panel
        self.panel = wx.Panel(self, -1)

        #Text Ctrl Boxes
        self.DebugMsg = wx.TextCtrl(self.panel,size=(300,300), style=wx.TE_MULTILINE |wx.EXPAND | wx.ALL)
        self.CmdInput = wx.TextCtrl(self.panel, id=30, style =wx.TE_PROCESS_ENTER )
        self.CmdInput.Value = "g1 x50 y50 z50 f450"
        self.CmdInput.SetToolTip(wx.ToolTip("Type a Gcode command and hit enter to execute the command."))
        self.CmdInput.SetEditable(True)
        self.GcodeTxt = wx.TextCtrl(self.panel) #TextCtrl Box that displays the Loaded Gcode File
        self.NudgeTxt = wx.TextCtrl(self.panel, size=(40,20), value=str(.1))
        #self.NudgeFdTxt = wx.TextCtrl(self.panel, size=(40,20), value="50")

        #Sliders
        self.feedSlider = wx.Slider(self.panel, -1, 50, 50, 500, (10, 10),(300, 50), wx.SL_HORIZONTAL  | wx.SL_LABELS)

        #Sizers
        hbox = wx.BoxSizer(wx.VERTICAL) #Create a master hbox then add everything into it
        gbs = wx.GridBagSizer(5, 5)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        #Serial Port Speeds:
        self.SPORT_SPEEDS = ["115200", "57600", "38400","19200"]
        self.SERIAL_PORTS = []
        self.FindInitPorts() #Scan for ports on program start

        #Combo Boxes
        self.FindInitPorts()
        self.cmbSports = wx.ComboBox(self.panel, -1, value=self.SERIAL_PORTS[-1], pos=wx.Point(10,30), choices=self.SERIAL_PORTS)
        self.cmbSpeeds = wx.ComboBox(self.panel, -1, value=self.SPORT_SPEEDS[0], pos=wx.Point(10,30), choices=self.SPORT_SPEEDS)

        #buttons 
        #Dbtn = wx.Button(self.panel, 1001, "D", (10,10), size=(30,20))
        #Ubtn = wx.Button(self.panel, 1002, "U", (10,10), size=(30,20))
        #Lbtn = wx.Button(self.panel, 1003, "L", (10,10), size=(30,20))
        #Rbtn = wx.Button(self.panel, 1004, "R", (10,10), size=(30,20))
        self.LoadBtn = wx.Button(self.panel,        17,  "Load Gcode", size=(75,25))
        self.RunBtn  = wx.Button(self.panel,   18,   "Run Gcode", size=(75,25))
        self.RefBtn  = wx.Button(self.panel,        19,   "Refresh",   size=(75,25))
        self.ConBtn  = wx.Button(self.panel,        20,   "Connect",   size=(75,25))
        #ExeBtn  = wx.Button(self.panel,       21,   "Execute",   size=(75,25)) #Just hit enter no need for this anymore
        #ClrBrn  = wx.Button(self.panel,       22,   "Clear",     size=(75,25)) #Not super functional just hit enter
        self.StopBtn = wx.Button(self.panel,        23,   "Stop",      size=(75,25))
        self.HardBtn = wx.Button(self.panel,        24,   "Hard Stop", size=(75,25))

        self.PauseBtn = wx.Button(self.panel,       25,   "Pause",     size=(75,25))
        self.ResumeBtn = wx.Button(self.panel,      26,   "Resume",    size=(75,25))


        #Static Text
        self.Gtext =   wx.StaticText(self.panel,   -1, "Gcode File:")
        self.Sertext = wx.StaticText(self.panel,   -1, "Serial Port:")
        self.Cmdtext = wx.StaticText(self.panel,   -1, "Gcode Command:")
        self.OutText = wx.StaticText(self.panel,   -1, "Ouput Text:")
        self.NudgeText = wx.StaticText(self.panel, -1, "Nudge Amount")
        self.SliderText = wx.StaticText(self.panel,-1, "Manual Feed Rate")
        #self.NudgeFeedText = wx.StaticText(self.panel, -1, "Nudge Feed Rate")

        #Add Items to hbox2
        hbox2.Add(self.PauseBtn, border=5, flag=wx.ALL)
        hbox2.Add(self.ResumeBtn, border=5, flag=wx.ALL)
        hbox2.Add(self.HardBtn, border=5, flag=wx.ALL)


        #Add Items to hbox3
        hbox3.Add(self.RefBtn, border=5, flag=wx.ALL)
        hbox3.Add(self.ConBtn, border=5, flag=wx.ALL)

        #Add Items to hbox4
        hbox4.Add(self.LoadBtn, border=5, flag=wx.ALL)
        hbox4.Add(self.RunBtn, border=5, flag=wx.ALL)
        hbox4.Add(self.StopBtn, border=5, flag=wx.ALL)


        #Add Items to the Flex Grid
        gbs.Add(self.Sertext,    pos=(0,0),   span=(1,1),   flag=wx.ALL)               #Row 0
        gbs.Add(self.cmbSports,  pos=(0,1),   span=(1,5),   flag=wx.ALL | wx.EXPAND)   #Row 0
        gbs.Add(self.cmbSpeeds,  pos=(0,6),   span=(1,3),   flag=wx.ALL | wx.EXPAND)   #Row 0
        gbs.Add(hbox3,           pos=(0,9),   span=(1,2))                              #Row 0


        gbs.Add(self.Cmdtext,    pos=(1,0),   span=(1,1),   flag=wx.ALL | wx.EXPAND)   #Row 1
        gbs.Add(self.CmdInput,   pos=(2,0),   span=(1,11),  flag=wx.ALL | wx.EXPAND)   #Row 2
        gbs.Add(self.Gtext,      pos=(3,0),   span=(1,13),  flag=wx.ALL|wx.EXPAND)     #Row 3

        gbs.Add(self.GcodeTxt,   pos=(4,0),   span=(1,9),   flag=wx.ALL|wx.EXPAND)     #Row 4
        gbs.Add(hbox4,           pos=(4,9),   span=(1,2),   flag=wx.ALL|wx.EXPAND)     #Row 4

        gbs.Add(self.OutText,    pos=(5,0),   span=(1,1))                              #Row 5
        gbs.Add(self.DebugMsg,   pos=(6,0),   span=(3,13), flag=wx.ALL|wx.EXPAND )     #Row 6


        gbs.Add(hbox2,           pos=(10,8),   span=(1,4),  flag=wx.ALL|wx.EXPAND)      #Row 9
        gbs.Add(self.NudgeText,  pos=(9,0),   span=(1,1))
        gbs.Add(self.NudgeTxt,   pos=(9,1),   span=(1,1))

        #gbs.Add(self.NudgeFeedText, pos=(9,0),  span=(1,1))
        #gbs.Add(self.NudgeFdTxt, pos=(10,1), span=(1,1))
        gbs.Add(self.SliderText, pos=(9,3), span=(1,1))
        gbs.Add(self.feedSlider, pos=(10,0), span=(5,5))


        hbox.Add(gbs, -1, wx.ALL | wx.CENTER)  #Add the gbs to the main hbox
        self.panel.SetSizer(hbox)

        #Bind Events
        #Text Ctrl Events
        wx.EVT_TEXT_ENTER(self, 30, self.OnExecute)

        #Menu Events
        wx.EVT_MENU(self, wx.ID_EXIT, self.OnQuit)

        #Button Events
        EVT_RESULT(self,self.OnResult) #THREADING
        wx.EVT_BUTTON(self, 17, self.OnLoad)
        wx.EVT_BUTTON(self, 18, self.OnStart)
        wx.EVT_BUTTON(self, 19, self.OnRefresh)
        wx.EVT_BUTTON(self, 20, self.OnConnect)
        wx.EVT_BUTTON(self, 21, self.OnExecute)
        wx.EVT_BUTTON(self, 22, self.OnClear)
        wx.EVT_BUTTON(self, 23, self.OnStop)
        wx.EVT_BUTTON(self, 24, self.OnStopHARD)
        wx.EVT_BUTTON(self, 25, self.OnPause)
        wx.EVT_BUTTON(self, 26, self.OnResume)

        #wx.EVT_IDLE(self, self.CheckSerial)    #Detects if tinyg was unplugged
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)

        #wx.EVT_CHAR(self, self.OnKeyDown)

        #Show the Frame Code
        self.Centre()
        self.Show(True)

    def OnKeyDown(self, event):
        #print "HERE"
        keycode = event.GetKeyCode()
        nudgeAmount = self.NudgeTxt.Value
        feed = float(self.feedSlider.Value)
        try:
            if keycode == wx.WXK_RIGHT:
                self.X_STATE = self.X_STATE + float(nudgeAmount)
                self.MoveNudge("X", self.X_STATE, feed)

            if keycode == wx.WXK_LEFT:
                self.X_STATE = self.X_STATE - float(nudgeAmount)
                self.MoveNudge("X", self.X_STATE, feed)         

            if keycode == wx.WXK_UP:
                self.Y_STATE = self.Y_STATE + float(nudgeAmount)
                self.MoveNudge("Y", self.Y_STATE, feed)

            if keycode == wx.WXK_DOWN:
                self.Y_STATE = self.Y_STATE - float(nudgeAmount)
                self.MoveNudge("Y", self.Y_STATE, feed)

            if keycode == wx.WXK_ESCAPE: #space for osx compat.
                self.ClearNudge()
                #self.MoveNudge("X", 0)
                #self.MoveNudge("Y", 0)
            else:
                event.Skip()
        except ValueError:
            self.PrintDebug("[!!]Nudge Amount Needs to be an float")
            return

    def ClearNudge(self):
        self.X_STATE  = 0
        self.Y_STATE = 0
        self.SetZero()

    def MoveNudge(self, axis, amount, feed):
        #try:
        if float(amount) or amount == 0:
            pass
        else:
            self.PrintDebug("[!!]Nudge Amount Needs to be an Float")
            return
        try:
            cmd = ("g0 %s%s F%s\n" % (axis, amount, feed))
            self.quickCommand(cmd)
            self.PrintDebug("[*]CORD DETAIL: X:%s Y:%s" % (self.X_STATE, self.Y_STATE))
        except AttributeError:
            self.PrintDebug("[!!]Connect to TinyG First!")
        except Exception, f:
            self.PrintDebug("[!!] %s" % f)


    def quickCommand(self, cmd):
        """This is used to send manual commands with the arrow keys in order to have some sort of flow control implemented"""

        self.connection.write(cmd)
        while (1):
            delim = self.connection.read()
            if delim == "*":
                break

    def SetZero(self):
        try:
            self.quickCommand(("G92 X0 Y0 Z0\n"))
            self.PrintDebug("[*]Zeroing Coordinate System. ")
            self.PrintDebug("[*]Sent: G92 X0 Y0 Z0")
        except AttributeError:
            self.PrintDebug("[!!]Connect to TinyG First!")


    def OnLoad(self, event):
        self.PrintDebug("Loading Gcode Files")
        tmpFile = self.GcodeTxt.Value  #Stores the filename that was previously selectev in case of cancel being clicked on dialog
        newFile = wx.FileSelector("Select the Gcode File", default_path="", default_filename="",default_extension="", wildcard="*.gcode", flags=0, parent=None,x=-1, y=-1)
        if newFile == "":
            pass
        else:
            self.GcodeTxt.Value = newFile

    def processFile(self, line):
        """Pass a serialport and the file object"""
        try:
            self.connection.write(3*"\n") #This might not be need anymore but it just sends a few \n down the wire to clear anything before sending gcode
        except serial.serialutil.SerialException:
            print "[ERROR] Write Failed"
            print "System Exiting"
            sys.exit(6)
        delim = ""
        line = line.rstrip() #remove trailing new line character
        self.PrintDebug("[*]Writing: %s" % line)
        self.connection.write(line+"\n") #send a line of gcode
        delim = self.connection.read() #check to see if we found our delimeter '*' 
        while delim != "*":  #Loop until we find the delim
            delim = self.connection.read()
        return

    def OnClear(self, event):
        """Clear the execute box."""
        self.CmdInput.Value = ""

    def OnExecute(self, event):
        """Execute the gcode command that is typed into the Cmd Input Box"""
        CMD = self.CmdInput.Value
        if CMD == "":
            self.PrintDebug("[!!]ERROR: Invalid Gcode Command")
        else:
            try:
                """Section is still under development,
		we are waiting to standardize a feed back standard
		with TinyG.  For now this will just echo what command was ran"""
                self.connection.write(CMD+"\n")
                self.PrintDebug("[*]Sending: %s" % CMD)
                response = ""
                while (1):
                    tmp = self.connection.read()
                    if tmp == "*":
                        break
                msg = self.connection.readline()
                self.PrintDebug("[TG OUT]--%s" % msg)

                self.CmdInput.Value = ""  #Clear the execute command after enter was pressed.
            except:
                self.PrintDebug("[!!]ERROR: Serial Port Not Connected")
                return
            #self.PrintDebug("[TINYG RESPONSE]: %s " % fullResponse.lstrip())

    def PrintDebug(self, msg):
        """Accepts a MSG you want to display"""
        return self.DebugMsg.AppendText(msg+"\n")

    def FindInitPorts(self):
        """Initial Run to find connected ports"""
        self.SERIAL_PORTS = serinit.scan() #Find the serial ports connected to a system (OS independent)
        self.status_bar.SetStatusText("%s Serial Port/s Found." % str(len(self.SERIAL_PORTS))) 
        if self.SERIAL_PORTS == []:  #If no serial ports were detected we return a msg where the port should be
            msg = "No Serial Ports Found"
            self.SERIAL_PORTS.append(msg)

    def OnRefresh(self, event):
        try:
            self.connection.close()
        except:
            pass
        self.PrintDebug("[*]Scanning For New Serial Ports")
        self.FindInitPorts()
        self.cmbSports.Items = self.SERIAL_PORTS #This updates the combo box with the list of ports returned

    def OnConnect(self, event):
        Connection_State = (self.ConBtn.Label == "Connect")  #If this evaluates to False we are connected.
        if Connection_State == True:
            """We are connected"""
            try:
                self.connection = serinit.connect(self.cmbSports.Value, self.cmbSpeeds.Value) # Try to establish an connection to the serial port
                self.connection.write("\n")                                                    #See if we can send a new line the serial port.  
                                                                                                #This is a test to see if TG is the device we are connected to
                self.status_bar.SetStatusText("Connected to Port: %s Speed: %s" % (self.connection.port, self.connection._baudrate))
                self.ConBtn.Label = "Disconnect"
            except:
                self.PrintDebug("[!!]ERROR: Connecting to the Serial Port")
                self.status_bar.SetStatusText("DISCONNECTED:")
        else:
            """This will hit when the ConBtn's label says "Disconnect" and it is clicked"""
            try:
                self.connection.close() #Try to disconnect the serial port.
                self.ConBtn.Label = "Connect"
                self.status_bar.SetStatusText("DISCONNECTED:")
            except Exception, disconnect_exception:
                self.PrintDebug("[ERROR] When trying to disconnect active serial port:\n %s" % disconnect_exception)

    def OnResume(self, event):
        """This will cause the system to pause and wait for the resume command"""
        try:
            self.connection.write('\x11')
            self.PrintDebug("[*]Sending Resume (XON)")
        except AttributeError:
            self.PrintDebug("[!!]ERROR: Serial Port Not Connected")

        except Exception, e:
            self.PrintDebug(str(e))

    def OnPause(self, event):
        """This will cause the system to pause and wait for the resume command"""
        try:
            self.connection.write('\x13')
            self.PrintDebug("[*]Sending Pause (XOFF)")
        except AttributeError:
            self.PrintDebug("[!!]ERROR: Serial Port Not Connected")

        except Exception, e:
            self.PrintDebug(str(e))

    def OnQuit(self, event):
        self.Destroy()

    def OnStart(self, event):
        if not self.worker:
            self.RunBtn.SetLabel("Running")
            """Worker takes self, serial port, debug text box and the loaded file"""
            self.worker = WorkerThread(self, self.connection, self.GcodeTxt.Value)

    def OnResult(self, event):
        if event.data is None:
            pass
        else:
            msg = event.data[0]
            currentLine = event.data[1]
            totalLines = event.data[2]
            #event.data = str(event.data)
            self.PrintDebug("%s of %s : %s" % (currentLine, totalLines, msg))
            #self.RunBtn.SetLabel("%s: Running" % ((currentLine/totalLines)))



    def OnStopHARD(self, event):
        try:
            self.connection.write('\x03')  #Send the CTRL+C control character
            self.PrintDebug("[!!]HARD STOP!\n You most likely will need to reboot TinyG now.")

        except AttributeError:
            self.PrintDebug("[!!] Not Connected to TinyG!")

    def OnStop(self, event):
        """Stop Processing the Gcode File and kill the tinyG"""
        # Flag the worker thread to stop if running
        if self.worker:
            self.RunBtn.SetLabel("Run Gcode")  #Change the Run button label back from Running
            self.PrintDebug('"[!!]Abort Signal Sent,  Trying to Abort Now!"')
            self.worker.abort()
            self.worker = None
            #self.connection.close()  #Try to close the serial port connection


    def CheckSerial(self, event):
        """Is called by the window IDLE event to check serial connection"""
        try:
            if self.connection.read():
                pass
        except:
            self.status_bar.SetStatusText("Disconnected")

"""THREADING CODE SHOULD BE WORKING CORRECTLY"""
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        try:
            msg = data[0]
            currentLine = data[1]
            totalLines = data[2]
        except TypeError:
            pass

        except Exception, z:
            print z

        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class WorkerThread(Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window, ser, gcodeFile):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.connection = ser        #Give the worker object access to the serial port
        self.gcodeFile = gcodeFile   #Give the worker object access to the file
        self.start()                 #Starts the thread



    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1

    def run(self):
        """Run Worker Thread."""
        if self._want_abort:
            """Catch Aborts"""
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        if self.connection:                        #check to see if the serial port is connected
            f = open(self.gcodeFile, 'r')          #Open the gcode file 
            fread =  f.readlines()                 #Read the whole gcode file
            totalLines = len(fread)                     #Get the total lines of gcode in the file
            currentLine = 1
            for line in fread:                     #Loop through gcode file
                currentLine = currentLine + 1
                line = line.strip()                #Strip \n at the beggining of the line
                delim = self.processFile(line)     #Send one line of gcode to ProcessGcode get a readline() back
                while delim != "*":                #Loop until we find the delim
                    try:
                        delim = self.connection.read() #Read a char again to find delim
                    except Exception, e:
                        wx.PostEvent(self._notify_window, ResultEvent(str(e)))
                        return
                wx.PostEvent(self._notify_window, ResultEvent((line, currentLine, totalLines)))

                if self._want_abort:
                    """Catch Aborts and break the loop!"""
                    wx.PostEvent(self._notify_window, ResultEvent("[!!]Aborted"))
                    return

    def processFile(self, line):
        """Pass a line of the file object (aka line of gcode)"""
        self.connection.write(line+"\n")   #send a line of gcode
        return self.connection.read()      #check to see if we found our delimeter '*' 



app = wx.App()
FlexGridSizer(None, -1, 'TinyG Controller / Loader')
app.MainLoop()
