from flask import render_template, Blueprint, request, redirect
import flask_restful as restful
from app.forms import *

import helper as hl

blueprint = Blueprint('pages', __name__)
api = restful.Api(blueprint)

################
#### routes ####
################




class GetYoutubeLinkDetails(restful.Resource):
    def get(self):
        return redirect('/')

    # @login_required
    def post(self):
        try:
            youtube_link = request.form
            resp = hl.find_resolutions_of_a_video(youtube_link)

            return resp
        except Exception as e:
            return e

api.add_resource(GetYoutubeLinkDetails, '/get_youtube_video_details')


@blueprint.route('/')
def home():
    return render_template('pages/placeholder.home.html')




@blueprint.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@blueprint.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@blueprint.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@blueprint.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)
