"""
Todd Page
4/21/2012
"""

## standard libraries
import json, os

from google.appengine.api import users#, channel
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext import db

## custom libraries
from models import *

#----------------------------------------------------------------------
def getTemplatePath(html_file):
    """
    Returns the path to the template file/directory from the app/ directory
    """
    return os.path.join(os.path.split(os.path.dirname(__file__))[0], "templates", html_file)

########################################################################    
class LandingPage(webapp2.RequestHandler):
    template_path = getTemplatePath("index.html")
    
    def get(self):
        current_user = users.get_current_user()
        url_logout = users.create_logout_url(self.request.uri)

        #category_name_dct = {
            #"comp": "Completeness",
            #"lookfeel": "Aesthetics",
            #"fun": "Fun",
            #"innovation": "Innovation",
            #"scope": "Scope",
            #"rl": "Roguelikeness",
        #}
        ## list of games
        game_lst = [g for g in Game.all()]
        template_values = {"game_lst": game_lst,
                           "url_logout": url_logout,
                           "image_lst": getImageFiles()}
                           #"category_lst": Review.category_lst,
                           #"category_name_dct": category_name_dct}
        
        self.response.out.write(template.render(LandingPage.template_path, template_values))
        
########################################################################
class DataLoadHandler(webapp2.RequestHandler):
    """"""
    def get(self):
        ## dump existing DB
        db.delete(Game.all())
        db.delete(Review.all())
        
        
        
        import csv
        
        gamedata_csv = csv.reader(open('gamedata.csv', 'r'))
        
        for i, row_lst in enumerate(gamedata_csv):
            if i == 0: continue
            rowid, image, title, author, link_url, platform = row_lst
            newgame = Game(title=title.strip(),
                           author=author.strip(),
                           platform=platform.strip(),
                           link_main=link_url.strip(),
                           image_shot=image.strip(),
                           name_key=title.upper())
            newgame.put()
            
        reviewdata_csv = csv.reader(open('reviewdata.csv', 'r'))
        
        for i, row_lst in enumerate(reviewdata_csv):
            if i == 0: continue
            game_name, reviewer, rv_comp, rv_lookfeel, rv_fun, rv_innovation, rv_scope, rv_rl, full_review = row_lst
            
            ## split individual category reviews 
            score_lst = []
            review_lst = []
            for prop in [rv_comp, rv_lookfeel, rv_fun, rv_innovation, rv_scope, rv_rl]:
                if prop[0] in ['1', '2', '3']:
                    score = int(prop[0])
                    review = prop[1:].strip(" ").strip("- ")
                    
                    score_lst.append(score)
                    review_lst.append(review)
            
            ## find which game we're talking about
            game_gql = Game.gql("WHERE name_key = :1", game_name.upper())
            
            if game_gql.count() == 0:
                assert 0 == 1
            elif game_gql.count() > 1:
                assert 0 == 1
            else:
                reviewed_game = game_gql[0]
                
            try:
                newreview = Review(game=reviewed_game,
                                   overall_review=str(full_review))
            except UnicodeDecodeError:
                pass
            newreview.setScores(score_lst)
            newreview.setReviews(review_lst)
            
            newreview.put()
            
        for game in Game.all():
            getAverageScoresForGame(game) ## cache it
            
        self.redirect("/")
        
#----------------------------------------------------------------------
def getImageFiles():
    """
    Returns a list of image hrefs
    """
    url_prefix = "/static/images/"
    img_lst = ['03_2149RL.png', '05_drillworms.png', '06_asylum.png', '08_bonebuilder.png', '09_cavechop.png', '10_cogmind.png', '12_deadnightforest.png', '13_drakefirechasm.jpg', '14_dunerl.png', '16_equalindeath.png', '18_fictionalrogue.png', '20_gateway.png', '23_hunterrl.png', '24_hyperrogue2.png', '27_jaggedrl.png', '28_jelly.png', '29_kaiju.png', '30_kitchenmaster.png', '32_linlem.png', '33_locks.png', '35_montasall.png', '38_nightfall.png', '39_phage.png', '43_robocaptain.png', '44_ruinsofkalraman.png', '45_shadowrogue.png', '46_smoothrogue.png', '47_steelknights.png', '48_suncrusher.png', '49_swampmonster.png', '50_swordinhand.png', '51_adventurersguild.png', '52_thechallenge.png', '53_tdojtd.png', '54_wellofenchant.png', '55_topdog.png', '56_traprl.png', '57_turambar.png', '62_fragilewrath.png', '64_portalucis.png', 'noimage.png']
    return [url_prefix + i for i in img_lst]