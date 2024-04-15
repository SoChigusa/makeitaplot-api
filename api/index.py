from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/plot', methods=['POST'])
def graph():
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from io import BytesIO

    # read file
    files = request.files
    file = files.get('plot_data')
    data_raw = file.read()

    # data processing
    data = np.array([np.fromstring(line, sep='\t') for line in data_raw.splitlines()])
    # print(data, file=sys.stderr)

    # plot
    matplotlib.use('agg')
    fig = plt.figure(figsize=[8,6])
    ax = fig.add_subplot(1,1,1)
    ax.plot(data[:,0], data[:,1])
    
    # plot range
    # ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # title, labels
    ax.set_title('Plot Title', size=20)
    ax.set_xlabel('x-label', size=15)
    ax.set_ylabel('y-label', size=15)
    ax.tick_params(labelsize=15)
    
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

@app.route('/plot-vercel-blob')
def graph2():
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
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
        fig = plt.figure(figsize=[8,6])
        ax = fig.add_subplot(1,1,1)
        ax.plot(data[:,0], data[:,1])
        
        # plot range
        # ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        # title, labels
        ax.set_title('Plot Title', size=20)
        ax.set_xlabel('x-label', size=15)
        ax.set_ylabel('y-label', size=15)
        ax.tick_params(labelsize=15)
        
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
