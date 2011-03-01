# -*- coding: utf-8 -*-

from flask import Flask
from mongoAdmin.application import create_app
app = create_app()

if __name__ == '__main__':
    app.run()
