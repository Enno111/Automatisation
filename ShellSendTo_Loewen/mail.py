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

        vbs += 'Set objNamespace = objOutlook.GetNamespace("MAPI")\n'
        vbs += 'For Each account In objNamespace.Accounts\n'
        vbs += '    If LCase(account.SmtpAddress) = "beispiel@beispiel.de" Then\n'
        vbs += '        Set objMail.SendUsingAccount = account\n'
        vbs += '    End If\n'
        vbs += 'Next\n'

        vbs += 'objMail.To = "beispiel@beispiel.de; beispiel@beispiel.de"\n'
        vbs += 'objMail.Subject = WScript.Arguments(0)\n'
        vbs += 'objMail.Attachments.Add WScript.Arguments(1)\n'
        vbs += 'objMail.Display\n'

        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.vbs', delete=False)
        tmp.write(vbs)
        tmp.close()

        subprocess.Popen(['wscript', tmp.name, filename, filepath])

if __name__ == "__main__":
    main()
