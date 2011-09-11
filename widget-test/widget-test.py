
import random


from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

# Increment this every time we do new tests
BASE_WIDGET_INDEX = 0

WIDGETS = ['one %s',
           'two %s',
           'three %s',
           'four %s']



class Impression (db.Model):
    datetime = db.DateTimeProperty (auto_now_add = True)
    widgetid = db.IntegerProperty ()

class Feedback (db.Model):
    impression = db.ReferenceProperty (Impression)
    widgetid = db.IntegerProperty ()
    hascomment = db.BooleanProperty ()
    
class WidgetHandler (webapp.RequestHandler):

    def __init__ (self):
        return
        
    def get (self):
        selection = random.randint (0, len (WIDGETS) - 1)
        widget = WIDGETS [selection]

        impression = Impression ()
        impression.widgetid = BASE_WIDGET_INDEX + selection
        impression.put ()

        self.response.out.write (str (impression.widgetid))
        self.response.out.write (widget % str (impression.key ().id ()))
        

class FeedbackHandler (webapp.RequestHandler):

    def __init__ (self):
        return

    def get (self):
        imp_id = self.request.get ("impression")

        try:
            imp_id = int (imp_id)
        except:
            self.error (500)
            return

        impression = Impression.get_by_id (imp_id)
        if (impression == None):
            self.error (500)
            return

        query = Feedback.all ()
        query.filter ('impression =', impression)

        if (query.count () > 0):
            # Already has one, so just return
            return
        
        feedback = Feedback (impression=impression)
        feedback.hascomment = self.request.get ('comment', default_value=None) != None
        feedback.widgetid = impression.widgetid
        feedback.put ()
        

class ResultsHandler (webapp.RequestHandler):

    def __init__ (self):
        return

    def add_row (self, name, feedback, impressions):
        width = float (feedback) / float (impressions) * 600

        self.response.out.write ('<tr><td width="200" align="center">%s</td>' % name)
        self.response.out.write ('<td width="400" valign="middle"> \
                                  <img border="2" src="/static/red.png" height="25" width="%d"> \
                                  </td><td align="center">%d/%d</td>' % (width, feedback, impressions))
        self.response.out.write ('</tr>')
            
    def get (self):
        self.response.out.write ('<html><head><title>CCF Test Results</title></head><body>')
        self.response.out.write ('<table border="1" width="800">')

        total_impressions = 0;
        total_feedback = 0;

        for i in range (0, len (WIDGETS)):
            
            query = Impression.all ()
            query.filter ('widgetid =', i)
            impressions = query.count ()
            total_impressions += impressions

            query = Feedback.all ()
            query.filter ('widgetid =', i)
            feedback = query.count ()
            total_feedback += feedback

            self.add_row (WIDGETS [i], feedback, impressions)

        self.add_row ('Total', total_feedback, total_impressions)
        
        self.response.out.write ('</table>')
        self.response.out.write ('</body></html>')
        
            

        
application = webapp.WSGIApplication(
                                     [('/widget', WidgetHandler),
                                      ('/feedback', FeedbackHandler),
                                      ('/results', ResultsHandler)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


