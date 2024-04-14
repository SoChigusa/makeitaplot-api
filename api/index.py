from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/plot')
def graph():
    import numpy as np
    import matplotlib.pyplot
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from io import BytesIO

    # data fetch
    fetch = requests.get(request.args.get('url'))
    if fetch.status_code == 200:
        data_raw = fetch.text
        
        # data processing
        data = np.array([np.fromstring(line, sep='\t') for line in data_raw.splitlines()])
        # print(data, file=sys.stderr)

        # plot
        matplotlib.use('agg')
        fig, ax = matplotlib.pyplot.subplots()
        ax.plot(data[:,0], data[:,1])
        ax.set_title('Plot')
        
        # png data
        canvas = FigureCanvasAgg(fig)
        buf = BytesIO()
        canvas.print_png(buf)
        png = buf.getvalue()
        
        # return as response
        response = make_response(png)
        response.headers['Content-Type'] = 'image/png'
        response.headers['Content-Length'] = len(png)
        return response
    
    else:
        return jsonify({'error': 'Failed to fetch data'})
