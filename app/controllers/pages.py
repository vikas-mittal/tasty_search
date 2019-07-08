from __future__ import print_function
from flask import render_template, Blueprint, request, redirect
import flask_restful as restful
from app.forms import *

import sys

from ..easy_search import helper as hl

blueprint = Blueprint('pages', __name__)
api = restful.Api(blueprint)


################
#### routes ####
################


class Search_top_k(restful.Resource):
    def get(self):
        return redirect('/')

    def post(self):
        try:
            query_data = request.get_json()
            resp = hl.search_top_k_results(query_data)
            return resp
        except Exception as e:
            return e


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


api.add_resource(Search_top_k, '/search_top_results')