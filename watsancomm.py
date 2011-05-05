import os, logging, datetime
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from settings import CUTOFF_DAY
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models import WeeklyUpdate

class PreviewWeekly(webapp.RequestHandler):
    def get(self):
        content = WeeklyUpdate.generate_summary_content(WeeklyUpdate.get_weekly_updates())
        email = WeeklyUpdate.generate_summary_email(content)
        self.response.out.write(email.html)

class SendUpdate(webapp.RequestHandler):
    def get(self):
        content = WeeklyUpdate.generate_summary_content(WeeklyUpdate.get_weekly_updates())
        email = WeeklyUpdate.generate_summary_email(content)
        email.send()

class SendReminder(webapp.RequestHandler):
    def get(self):
        reminder_day = (CUTOFF_DAY - 2) >= 0 and (CUTOFF_DAY - 2) or (CUTOFF_DAY + 5)
        if datetime.date.today().weekday() == reminder_day:
            logging.info('Reminder scheduled today! Sending.')
            email = WeeklyUpdate.generate_reminder_email()
            email.send()
        else:
            logging.info('No reminder scheduled today.')

class SendScheduledUpdate(SendUpdate):
    def get(self):
        if datetime.date.today().weekday() == CUTOFF_DAY:
            logging.info('Update scheduled today! Sending.')
            return super(SendScheduledUpdate, self).get()
        else:
            logging.info('No update scheduled today.')

application = webapp.WSGIApplication([
                                        ('/main/preview', PreviewWeekly),
                                        ('/main/send_update', SendUpdate),
                                        ('/main/send_reminder', SendReminder),
                                        ('/main/send_scheduled_update', SendScheduledUpdate),
                                     ], debug=True,)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
