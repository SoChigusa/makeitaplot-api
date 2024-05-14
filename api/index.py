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
    from matplotlib.backends.backend_pdf import FigureCanvasPdf
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
    fig = plt.figure() if not settings['fig']['sizeSpecify'] else plt.figure(figsize=[settings['fig']['size'][0], settings['fig']['size'][1]])
    ax = fig.add_subplot(1,1,1)
    for plot in settings['plots']['plotList']:
        ax.plot(data[:,plot['x']-1],
            data[:,plot['y']-1],
            color=plot['color'],
            ls=plot['lineStyle']['spec'],
            lw=plot['lineWidth'],
            label=plot['legend'])

    # plot legend
    if(settings['plots']['legendFlag']):
        ax.legend(loc=settings['plots']['legendLocation'], fontsize=settings['plots']['legendSize'])

    # axis settings
    if(settings['xAxis']['limSpecify']):
        ax.set_xlim(settings['xAxis']['lim'][0], settings['xAxis']['lim'][1])
    if(settings['yAxis']['limSpecify']):
        ax.set_ylim(settings['yAxis']['lim'][0], settings['yAxis']['lim'][1])
    if(settings['xAxis']['logScale']):
        ax.set_xscale('log')
    if(settings['yAxis']['logScale']):
        ax.set_yscale('log')

    # title, labels
    if(settings['fig']['titleSpecify']):
        ax.set_title(settings['fig']['title'], size=settings['fig']['titleSize'])
    ax.set_xlabel(settings['xAxis']['label'],
        size=settings['xAxis']['labelSize'])
    ax.set_ylabel(settings['yAxis']['label'],
        size=settings['yAxis']['labelSize'])
    ax.tick_params(labelsize=settings['ticks']['labelSize'])

    # some adjustment
    fig.tight_layout()

    buf = BytesIO()
    if(settings['imageType'] == 'png'):
        
        # png data
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(buf)
        png = buf.getvalue()

        # return as response
        response = make_response(png)
        response.headers['Content-Type'] = 'image/png'
        response.headers['Content-Length'] = len(png)
        return response

    elif(settings['imageType'] == 'pdf'):

        # pdf data
        canvas = FigureCanvasPdf(fig)
        canvas.print_pdf(buf)
        pdf = buf.getvalue()

        # return as response
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Length'] = len(pdf)
        return response

@app.route('/source', methods=['POST'])
def source():
    
    # get file name
    file_name_full = request.form['file_name']
    file_name = file_name_full.split('.')[0]

    # read settings file
    files = request.files
    settings_raw = files.get('settings').read()
    settings = json.loads(settings_raw.decode('utf-8'))

    # components
    components = {}
    if settings['fig']['sizeSpecify']:
        components["figPreparation"] = "plt.figure(figsize=["+ str(settings['fig']['size'][0]) +","+ str(settings['fig']['size'][1]) +"])"
    else:
        components["figPreparation"] = "fig = plt.figure()"

    s1 = [
        "import numpy as np",
        "import matplotlib.pyplot as plt",
        "",
        "# data input",
        "data = np.loadtxt('" + file_name_full + "', delimiter='\\t', skiprows=0)",
        "",
        "# figure",
        components["figPreparation"],
        "ax = fig.add_subplot(1,1,1)",
    ]
    
    s2 = ["", "# plot"]
    for plot in settings['plots']['plotList']:
        s2.append(
            "ax.plot(data[:," + str(plot['x']-1) + "],"
            "data[:," + str(plot['y']-1) + "],"
            "color='" + plot['color'] + "',"
            "ls='" + plot['lineStyle']['spec'] + "',"
            "lw=" + str(plot['lineWidth']) + ","
            "label='" + plot['legend'] + "')"
        )

    s3 = []
    if(settings['plots']['legendFlag']):
        s3 += [
            "",
            "# plot legend",
            "ax.legend(loc='" + settings['plots']['legendLocation'] + "', fontsize=" + str(settings['plots']['legendSize']) + ")",
        ]

    s4 = ["", "# axis settings"]
    if(settings['xAxis']['limSpecify']):
        s4.append("ax.set_xlim(" + str(settings['xAxis']['lim'][0]) + ", " + str(settings['xAxis']['lim'][1]) + ")")
    if(settings['yAxis']['limSpecify']):
        s4.append("ax.set_ylim(" + str(settings['yAxis']['lim'][0]) + ", " + str(settings['yAxis']['lim'][1]) + ")")
    if(settings['xAxis']['logScale']):
        s4.append("ax.set_xscale('log')")
    if(settings['yAxis']['logScale']):
        s4.append("ax.set_yscale('log')")
        
    s5 = ["", "# title, labels"]
    if(settings['fig']['titleSpecify']):
        s5.append("ax.set_title(" + settings['fig']['title'] + ", size=" + str(settings['fig']['titleSize']) + ")")
        
    s6 = [
        "ax.set_xlabel('" + settings['xAxis']['label'] + "', size=" + str(settings['xAxis']['labelSize']) + ")",
        "ax.set_ylabel('" + settings['yAxis']['label'] + "', size=" + str(settings['yAxis']['labelSize']) + ")",
        "ax.tick_params(labelsize=" + str(settings['ticks']['labelSize']) + ")",
        "",
        "# figure output",
        "plt.tight_layout()",
        "plt.savefig('" + file_name + ".pdf', bbox_inches='tight')"
    ]

    s = '\n'.join(s1 + s2 + s3 + s4 + s5 + s6)

    # return as response
    response = make_response(s)
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Length'] = len(s)
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
