import dash

import warnings
warnings.filterwarnings('ignore')

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

server = app.server