"""
Todd Page
4/21/2012
"""

## standard libraries
import datetime, json

## custom libraries
## third-party libraries
from google.appengine.ext import db

########################################################################
class Game(db.Model):
    """
    Represents a 7drl challenge entry
    """
    title = db.StringProperty(required=True)
    author = db.StringProperty()
    platform = db.StringProperty()
    link_main = db.LinkProperty(required=True)
    image_shot = db.StringProperty()
    name_key = db.StringProperty()
    
    ## cache sorted stuff
    score_comp = db.FloatProperty()
    score_lookfeel = db.FloatProperty()
    score_fun = db.FloatProperty()
    score_innovation = db.FloatProperty()
    score_scope = db.FloatProperty()
    score_rl = db.FloatProperty()
    score_avg = db.FloatProperty()
    
    #----------------------------------------------------------------------
    def cacheScores(self, score_dct):
        """
        Set scores for this Game based on any/all Review objects associated with it
        """
        for category, score in score_dct.items():
            setattr(self, 'score_' + category, score)
        self.put()
        
        return True
        
    #----------------------------------------------------------------------
    def getCachedScores(self):
        """Return cached average scores if we got them already"""
        score_list_dct = {cat: getattr(self, 'score_' + cat) for cat in Review.category_lst}
        score_list_dct['avg'] = self.score_avg
        return score_list_dct
    
    def hasCachedScores(self):
        return self.score_avg != None
        
    #----------------------------------------------------------------------
    def getAsDictionary(self):
        """"""
        return {
            "id": self.key().id(),
            "title": str(self.title),
            "author": str(self.author),
            "platform": str(self.platform),
            "link_main": str(self.link_main),
            "image_shot": str(self.image_shot),
            "scores": self.getCachedScores()
        }
    
########################################################################
class Review(db.Model):
    category_lst = ['comp', 'lookfeel', 'fun', 'innovation', 'scope', 'rl']
    """
    Represents a (anonymous) reviewer's score of a Game
    """
    game = db.ReferenceProperty(Game, required=True)
    reviewer = db.StringProperty() # should be anonymous, maybe hash it
    
    # category scores
    comp_score = db.IntegerProperty()
    lookfeel_score = db.IntegerProperty()
    fun_score = db.IntegerProperty()
    innovation_score = db.IntegerProperty()
    scope_score = db.IntegerProperty()
    rl_score = db.IntegerProperty()
    
    # category notes
    comp_note = db.TextProperty()
    lookfeel_note = db.TextProperty()
    fun_note = db.TextProperty()
    innovation_note = db.TextProperty()
    scope_note = db.TextProperty()
    rl_note = db.TextProperty()

    overall_review = db.TextProperty()
    
    #----------------------------------------------------------------------
    def getCategoryScore(self, category):
        return getattr(self, category+'_score')
        
    #----------------------------------------------------------------------
    def getCategoryNote(self, category):
        return getattr(self, category+'_note')    
    
    #----------------------------------------------------------------------
    def getAsDictionary(self):
        """
        Returns this Review as a JSONable dictionary
        """
        result_dct = {
            "scores": { cat: self.getCategoryScore(cat) for cat in Review.category_lst},
            "reviews": { cat: self.getCategoryNote(cat) for cat in Review.category_lst}
        }
        
        result_dct["scores"]["avg"] = self.getAverageScore()
        result_dct["reviews"]["avg"] = self.overall_review
        
        return result_dct
    
    #----------------------------------------------------------------------
    def getAverageScore(self):
        """Returns a simple average of all categories"""
        return round(sum([self.getCategoryScore(category) for category in Review.category_lst]) / 6.0, 2)
    
    #----------------------------------------------------------------------
    def setScores(self, score_lst):
        """
        Sets all scores - IN ORDER - based on an integer list
        """
        for score, category in zip(score_lst, Review.category_lst):
            setattr(self, category+'_score', score)
        
        return len(score_lst) == len(Review.category_lst)
    
    #----------------------------------------------------------------------
    def setReviews(self, review_lst):
        """
        Sets all reviews - IN ORDER - based on an string list
        """
        for review, category in zip(review_lst, Review.category_lst):
            setattr(self, category+'_note', review)
        
        return len(review_lst) == len(Review.category_lst)
    
def getAverageScoresForGame(game):
    """
    Return a dictionary of average scores for a given game
    based on ALL reviews
    """
    if game.hasCachedScores():
        return game.getCachedScores()
    else:
        score_list_dct = {cat: [] for cat in Review.category_lst}
        total_lst = []
        
        for review in game.review_set:
            for cat in Review.category_lst:
                score_list_dct[cat].append(review.getCategoryScore(cat))
                total_lst.append(review.getCategoryScore(cat))
                
        score_avg_dct = {cat: round((sum(score_list_dct[cat]) / float(len(score_list_dct[cat]))), 2) for cat in Review.category_lst}
        score_avg_dct["avg"] = round(sum(total_lst) / float(len(total_lst)), 2)
        game.cacheScores(score_avg_dct)
        return score_avg_dct