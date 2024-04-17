from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import requests
import json

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
    settings_raw = files.get('settings').read()
    settings = json.loads(settings_raw.decode('utf-8'))
    data_raw = files.get('plot_data').read()

    # data processing
    data = np.array([np.fromstring(line, sep='\t') for line in data_raw.splitlines()])
    # print(data, file=sys.stderr)

    # plot
    matplotlib.use('agg')
    fig = plt.figure() if not settings['fig']['size-specify'] else plt.figure(figsize=[settings['fig']['size'][0], settings['fig']['size'][1]])
    ax = fig.add_subplot(1,1,1)
    for plot in settings['plot']:
        ax.plot(data[:,plot['x']],
            data[:,plot['y']],
            color=plot['color'],
            ls=plot['line-style'],
            lw=plot['line-width'])
    
    # axis settings
    if(settings['x-axis']['lim-specify']):
        ax.set_xlim(settings['x-axis']['lim'][0], settings['x-axis']['lim'][1])
    if(settings['y-axis']['lim-specify']):
        ax.set_ylim(settings['y-axis']['lim'][0], settings['y-axis']['lim'][1])
    if(settings['x-axis']['log-scale']):
        ax.set_xscale('log')
    if(settings['y-axis']['log-scale']):
        ax.set_yscale('log')

    # title, labels
    if(settings['fig']['title-specify']):
        ax.set_title(settings['fig']['title'], size=settings['fig']['title-size'])
    ax.set_xlabel(settings['x-axis']['label'],
        size=settings['x-axis']['label-size'])
    ax.set_ylabel(settings['y-axis']['label'],
        size=settings['y-axis']['label-size'])
    ax.tick_params(labelsize=settings['tick']['label-size'])
    
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
