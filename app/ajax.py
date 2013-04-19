"""
Todd Page
4/21/2012
"""

## standard libraries

## third-party libraries
import json
import webapp2

## custom libraries
from models import *
from google.appengine.api import users
class AjaxHandler(webapp2.RequestHandler):
    """
    handle all ajax calls
    """
    #----------------------------------------------------------------------
    def get(self, request_type):
        """ 
        Returns current user
        Or error, if none
        """
        current_user = users.get_current_user()
        if request_type == 'getallgames':
            response_dct = self.getAllGameData()
        elif request_type == 'getreviews':
            game_id = int(self.request.get("game_id"))
            response_dct = self.getReviewForGame(game_id)
            
        return self.response.out.write(json.dumps(response_dct))

    #----------------------------------------------------------------------
    def getAllGameData(self):
        """Returns a dictionary of all games and their data"""
        game_dct = {}
        game_lst = []
        for game in Game.all():
            game_dct[game.key().id()] = game.getAsDictionary()
            game_lst.append(game)
            
        sort_by = str(self.request.get("sort_by"))
        sort_by = sort_by if sort_by else "avg"
        
        sorted_id_lst = [int(g.key().id()) for g in getSortedIdList(game_lst, sort_by)]
        
        response_dct = {
            "status": "OK",
            "data": {
                "games": game_dct,
                "list": sorted_id_lst
            }
        }
        
        return response_dct
    
    def getReviewForGame(self, game_id):
        game = Game.get_by_id(game_id)
        reviews = game.review_set
        
        response_dct = {
            "status": "OK",
            "data": {
                "game": game.getAsDictionary(),
                "singular": [r.getAsDictionary() for r in reviews],
                "average": getAverageScoresForGame(game)
            }
        }
        
        return response_dct

def fn_game_compare(game_a, game_b, category):
    """
    """
    category_score_a = game_a.getCachedScores()[category]
    category_score_b = game_b.getCachedScores()[category]
    if category_score_a != category_score_b:
        return cmp(category_score_a, category_score_b)
    else:
        sec_category = 'rl' if category == 'avg' else 'avg'
        sec_score_a = game_a.getCachedScores()[sec_category]
        sec_score_b = game_b.getCachedScores()[sec_category]
        
        return cmp(sec_score_a, sec_score_b)

def getSortedIdList(game_lst, category):
    """
    Return a [list] of ids sorted by the given category
    """
    #return sorted(game_lst, key=lambda x: x.getCachedScores()[category], reverse=True)
    return sorted(game_lst, cmp=lambda x, y: fn_game_compare(x, y, category), reverse=True)