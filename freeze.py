"""Build static version of the dashboard for GitHub Pages.
Run: python freeze.py
Then push the 'site' folder to gh-pages branch.
"""

import os, sys, shutil
sys.path.insert(0, '.')

# Disable CSRF for static build
os.environ['WTF_CSRF_ENABLED'] = 'False'

from flask_frozen import Freezer
from app import create_app

app = create_app()
app.config['FREEZER_DESTINATION'] = 'site'
app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_IGNORE_MIMETYPE_WARNINGS'] = True

# URLs to freeze
URLS = [
    '/auth/login',
    '/auth/forgot-password',
    '/dashboard',
    '/users/',
    '/users/add',
    '/users/edit/1',
    '/products/',
    '/products/add',
    '/products/edit/1',
    '/reports/',
    '/settings/',
    '/settings/profile',
    '/ai/assistant',
]

freezer = Freezer(app)

@freezer.register_generator
def all_urls():
    for url in URLS:
        yield url

if __name__ == '__main__':
    if os.path.exists('site'):
        shutil.rmtree('site')
    freezer.freeze()
    print(f'\nStatic site built in "site/" directory')
    print('Deploy to GitHub Pages:')
    print('  git checkout -b gh-pages')
    print('  copy site/* to root or use: gh-pages deploy')
