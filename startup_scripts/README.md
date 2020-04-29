#### Instructions for making the pi send an email with the new IP at startup
1. Create a folder in /home/pi/ called "startup"
2. Copy "launcher.sh", "startup_mailer.py" and "prev_ip.sh" into that folder
3. Add the email addresses to the "receiver_email" list
4. Try running "sh launcher.sh", if permission denided then the device needs to be whitelisted by google. 
5. Create a folder in "startup" called "logs"
6. Run the command "crontab -e", you might have to sudo apt-get install cron
7. Paste this at the top of the document:
   @reboot sh /home/pi/startup/launcher.sh >/home/pi/startup/logs/cronlog 2>&1
8. Check if it is working by changing the IP in prev_ip.sh and rebooting the pi
