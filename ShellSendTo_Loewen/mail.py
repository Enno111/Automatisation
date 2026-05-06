import sys
import os
import tempfile
import subprocess

def main():
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        return
    
    for i in range(1, len(sys.argv)):
        if not os.path.exists(sys.argv[i]):
            return

        filepath = sys.argv[i]
        filename = os.path.basename(filepath)

        vbs = 'Set objOutlook = CreateObject("Outlook.Application")\n'
        vbs += 'Set objMail = objOutlook.CreateItem(0)\n'
        vbs += 'objMail.To = "example@example.com; example2@example.com"\n' #update with real email addresses
        vbs += 'objMail.Subject = WScript.Arguments(0)\n'
        vbs += 'objMail.Attachments.Add WScript.Arguments(1)\n'
        vbs += 'objMail.Display\n'

        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.vbs', delete=False)
        tmp.write(vbs)
        tmp.close()

        subprocess.Popen(['wscript', tmp.name, filename, filepath])

if __name__ == "__main__":
    main()
